
# Data Analysis and Visualization Web App

This Django-based web application provides users with a robust platform for data analysis and visualization. Users can upload CSV files and analyze their data through a range of statistical methods and visualizations.

## Features

1. **File Upload:**
   - Users can upload a CSV file for analysis.
   - The application previews the first few rows of the dataset and provides basic information such as the number of rows, columns, memory usage, and total missing values.

2. **Single Column Analysis:**
   - Performs descriptive statistical analysis (mean, median, mode, etc.) for numeric columns.
   - Generates visualizations such as histograms, box plots, violin plots, Q-Q plots, and empirical CDFs.
   - Provides the frequency distribution for categorical columns, including top values and their percentages.

3. **Two-Column Analysis:**
   - Supports X vs Y analysis for numeric and categorical columns.
   - For numeric pairs, it calculates Pearson and Spearman correlations and generates scatter plots, hexbin plots, 2D KDE plots, and residual plots.
   - For categorical pairs, it performs a chi-squared test and visualizes the results with heatmaps and stacked bar plots.

4. **Visualization Style:**
   - Implements a custom dark-themed visualization style using `matplotlib`.



## Dependencies

- Python 3.8+
- Django
- Pandas
- NumPy
- Matplotlib
- Seaborn
- plotly



## How to Run


   ```

1. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```



---

Thank you for using the Data Analysis and Visualization Web App. Feel free to contribute or raise issues on the project repository!


