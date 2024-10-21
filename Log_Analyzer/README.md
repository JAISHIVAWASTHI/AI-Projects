# Log Analyzer

Welcome to the **Log Analyzer**! This Python tool is designed to analyze log data, preprocess it, and apply various machine learning models to classify errors based on log entries.

## Features

- **Data Preprocessing**: Clean and preprocess log data for effective analysis.
- **Multiple Classifiers**: Implements various machine learning classifiers, including:
  - Naive Bayes
  - K-Nearest Neighbors (KNN)
  - Gradient Boosting
  - Support Vector Machine (SVM)
  - Random Forest
  - Logistic Regression
- **FastText Integration**: Use FastText for text classification based on log data.
- **Data Balancing**: Handles imbalanced datasets using SMOTE.
- **Visualization**: Generate confusion matrices and classification reports for performance evaluation.

## File Descriptions

- **LogAnalyzer.py**: The main class that contains methods for data processing, model training, and evaluation.
- **sample_data.csv**: Sample dataset for testing and demonstration purposes.

## Requirements

Ensure you have the following Python packages installed:

- `fasttext`
- `scikit-learn`
- `pandas`
- `spacy`
- `imbalanced-learn`
- `matplotlib`
- `seaborn`
- `numpy`

You can install the required packages using:

```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare Your Data**: Place your log data in a CSV file (e.g., `sample_data.csv`) in the specified path.


## Example of Usage

To run the FastText classifier, you can modify the `main` block as follows:

```python
if __name__ == "__main__":
    la = LogAnalyzer()
    x_train, x_test, y_train, y_test = la.return_stable_data_in_vectors()
    print(la.model_comparision(x_train, y_train))
```

## Model Comparison

The script includes a method to compare different classifiers and display their best scores and parameters, which can help you choose the most effective model for your data.

## Visualization

Confusion matrices and classification reports are generated to help you evaluate the performance of the classifiers visually.

## Contributing

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Submit a pull request.
