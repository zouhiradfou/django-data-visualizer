from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import seaborn as sns
import base64
from plotly.offline import plot
import plotly.express as px
from django.http import JsonResponse
import io

# Variable globale pour stocker les données téléchargées par l'utilisateur
data = None  

# Fonction pour télécharger et lire un fichier CSV
def upload_file(request):
    global data  # Utilisation de la variable globale
    stats = None  # Initialisation des statistiques à None

    if request.method == 'POST':  # Si un fichier est soumis via POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():  # Vérification de la validité du formulaire
            file = form.save()  # Sauvegarde du fichier
            data = pd.read_csv(file.file.path)  # Lecture du fichier CSV avec pandas
    else:
        form = UploadFileForm()  # Initialisation du formulaire vide

    # Si des données sont chargées, calculer les statistiques
    if data is not None:
        stats = {
            'num_rows': len(data),  # Nombre de lignes
            'num_columns': len(data.columns),  # Nombre de colonnes
            'columns': list(data.columns),  # Liste des colonnes
            'has_null_values': data.isnull().values.any(),  # Vérifier la présence de valeurs manquantes
            'null_count': data.isnull().sum().to_dict()  # Compter les valeurs manquantes par colonne
        }

    # Renvoyer la page d'upload avec le formulaire et les statistiques
    return render(request, 'upload_file.html', {
        'form': form,
        'stats': stats, 
    })

# Fonction pour afficher un aperçu des données
def data_preview(request):
    global data  # Utilisation de la variable globale

    # Vérifier si des données existent
    if data is not None:
        # Convertir le DataFrame en HTML pour l'affichage dans le template
        data_html = data.to_html(classes='data-table', index=False)
    else:
        data_html = "No data available. Please upload a CSV file first."

    return render(request, 'data_preview.html', {
        'data_html': data_html,
    })

# Fonction pour accéder aux lignes et colonnes des données
def access_row_column(request):
    global data  # Vérifier si des données sont chargées
    result = None
    columns = data.columns.tolist() if data is not None else []  # Obtenir les noms des colonnes

    if request.method == 'GET' and data is not None:
        # Récupérer les paramètres de l'utilisateur
        row_range = request.GET.get('row_range', None)  # Plage des lignes (ex. "1:5" ou "3")
        column_name = request.GET.get('column_name', None)  # Nom de la colonne
        include_column = request.GET.get('include_column', None)  # Inclure les valeurs de colonne
        include_row = request.GET.get('include_row', None)  # Inclure les valeurs de la plage de lignes

        try:
            # Si l'utilisateur sélectionne des colonnes
            if include_column:
                if column_name:  # Si un nom de colonne est fourni
                    if row_range:  # Si une plage de lignes est fournie
                        if ":" in row_range:  # Plage sous forme "1:5"
                            start, end = map(int, row_range.split(":"))
                            result = data.iloc[start:end][column_name].tolist()  # Valeurs pour la plage
                        else:  # Indice unique pour une ligne
                            row_index = int(row_range)
                            result = {"value": data.at[row_index, column_name]}  # Valeur unique
                    else:  # Si seulement la colonne est sélectionnée
                        result = data[column_name].tolist()

            # Si l'utilisateur sélectionne une plage de lignes
            elif include_row and row_range:
                if ":" in row_range:  # Plage de lignes
                    start, end = map(int, row_range.split(":"))
                    result = data.iloc[start:end].to_dict(orient="records")  # Plusieurs lignes
                else:  # Indice unique
                    row_index = int(row_range)
                    result = data.iloc[[row_index]].to_dict(orient="records")  # Une seule ligne

        except Exception as e:
            result = {"error": f"An error occurred: {str(e)}"}  # Gestion des erreurs

    return render(request, 'access_data.html', {
        'result': result,
        'columns': columns  # Passer les noms de colonnes au template
    })

# Fonction pour effectuer une analyse statistique sur une plage de données
def statistical_analysis(request):
    global data  # Utilisation de la variable globale
    stats = None

    if data is not None:  # Vérifier si des données existent
        if request.method == 'GET':
            # Récupérer les indices de début et fin, ainsi que la colonne sélectionnée
            start_index = request.GET.get('start_index', None)
            end_index = request.GET.get('end_index', None)
            selected_column = request.GET.get('selected_column', None)

            if start_index and end_index and selected_column:
                try:
                    start_index = int(start_index)
                    end_index = int(end_index)

                    # Vérifier si les indices sont valides
                    if start_index < len(data) and end_index <= len(data) and start_index < end_index:
                        subset = data.iloc[start_index:end_index]  # Sous-ensemble des lignes

                        # Calcul des statistiques pour la colonne sélectionnée
                        if selected_column in subset.columns:
                            column_data = subset[selected_column]
                            stats = {
                                'mean': column_data.mean(),
                                'median': column_data.median(),
                                'std_dev': column_data.std(),
                                'min': column_data.min(),
                                'max': column_data.max(),
                                'count': column_data.count(),
                            }
                        else:
                            stats = {'error': f"Column '{selected_column}' not found in the selected range."}

                    else:
                        stats = {'error': 'Invalid range of indices. Ensure start < end and within valid row indices.'}
                except ValueError:
                    stats = {'error': 'Invalid indices provided. Ensure indices are numbers.'}

            else:
                stats = {'error': 'Please provide both start and end indices, and select a column.'}

    else:
        stats = {'error': 'No data available. Please upload a dataset.'}

    return render(request, 'statistics.html', {
        'stats': stats,
        'columns': data.columns if data is not None else [],  # Passer les colonnes disponibles
    })

# Fonction pour générer des visualisations interactives
def visualization(request):
    global data
    plot_div = None
    plot_type = request.GET.get('plot_type', 'scatter')  # Type de graphique
    column_x = request.GET.get('column_x')  # Colonne X
    column_y = request.GET.get('column_y')  # Colonne Y
    use_axes = request.GET.get('use_axes', 'both')  # Choix des axes : 'x', 'y', 'both'

    if data is not None:
        try:
            # Génération de graphique selon le type et les axes choisis
            if use_axes == 'both' and column_x and column_y:
                if plot_type == 'scatter':
                    fig = px.scatter(data, x=column_x, y=column_y, title="Scatter Plot")
                elif plot_type == 'line':
                    fig = px.line(data, x=column_x, y=column_y, title="Line Plot")
                elif plot_type == 'bar':
                    fig = px.bar(data, x=column_x, y=column_y, title="Bar Chart")
                elif plot_type == 'box':
                    fig = px.box(data, x=column_x, y=column_y, title="Box Plot")
            elif use_axes == 'x' and column_x:
                if plot_type == 'histogram':
                    fig = px.histogram(data, x=column_x, title="Histogram")
                elif plot_type == 'pie':
                    fig = px.pie(data, names=column_x, title="Pie Chart")
            else:
                fig = None

            if fig:
                plot_div = plot(fig, output_type='div')  # Convertir le graphique en HTML
        except Exception as e:
            plot_div = f"An error occurred: {e}"  # Gestion des erreurs

    return render(request, 'visualization.html', {
        'plot_div': plot_div,
        'columns': data.columns if data is not None else [],  # Passer les colonnes disponibles
    })
