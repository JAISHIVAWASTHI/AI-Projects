"""
Log Analyzer
@since: 06-01-2024
"""

import fasttext
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
import re
import spacy
from imblearn.over_sampling import SMOTE
from matplotlib import pyplot as plt
import seaborn as sn
import numpy as np
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings("ignore")


class LogAnalyzer:
    """Log Analyzer tool"""

    def __init__(self):
        pass

    def read_csv_file(self, path):
        """Read CSV file"""
        data_frame = pd.read_csv(path)
        return data_frame

    def dataframe_shape(self, data_frame: pd.DataFrame):
        """Dataframe shape"""
        return data_frame.shape

    def dataframe_head(self, data_frame: pd.DataFrame, head_size: int = 5):
        """dataframe head"""
        return data_frame.head(head_size)

    def preprocess(self, text):
        text = re.sub(r"\b[A-Za-z]:((\S\w+)+\W.(\S\w+)(\S\w+)+)\b", " ", text)
        text = re.sub(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", " ", text
        )
        text = re.sub(" +", " ", text)
        text = re.sub(" #", " ", text)
        text = re.sub(r"[^\w\s\']", " ", text)
        text = re.sub(" +", " ", text)
        text = re.sub("\n", " ", text)
        return text.strip().lower()

    def column_data_parsher(self, data_frame: pd.DataFrame):
        """Parser for column data"""
        data_frame["category_description"] = data_frame["step_details"].map(
            self.preprocess
        )
        return data_frame

    def create_data_for_fasttext(self, data_frame: pd.DataFrame):
        """Create column for fasttext"""
        data_frame["fasttext_data"] = (
            "__label__"
            + data_frame["error_class"].astype(str)
            + " "
            + data_frame["category_description"]
        )
        return data_frame

    def split_data_frame(self, data_frame: pd.DataFrame, test_size: float):
        """split data in train and test"""
        train, test = train_test_split(
            data_frame, test_size=test_size, random_state=2025
        )
        return train, test

    def split_data_frame_column_data(
        self, values, label_num, test_size: float = 0.1
    ):
        """Split data column"""
        X_train, X_test, y_train, y_test = train_test_split(
            values, label_num, test_size=test_size, random_state=2022
        )
        return (X_train, X_test, y_train, y_test)

    def map_error_classes_to_num(self, data_frame: pd.DataFrame):
        """map error class"""
        data_frame["label_num"] = data_frame["error_class"].map(
            {"node_issue": 0, "script_issue": 1, "spirent_issue": 2}
        )
        return data_frame

    def create_num_vector(self, data_frame: pd.DataFrame):
        """Create a new num_vector
        Using spacy
        """
        nlp = spacy.load("en_core_web_lg")
        data_frame["vector"] = data_frame["step_details"].apply(
            lambda text: nlp(text).vector
        )
        return data_frame

    def convert_in_2d_vector(self, values):
        """Convert in 2d vector"""
        return np.stack(values)

    def balance_the_data_class(self, x_train_2d, y_train):
        """Balance the data class"""
        smote = SMOTE(sampling_strategy="minority")
        x_new, y_new = smote.fit_resample(x_train_2d, y_train)
        return x_new, y_new

    def print_confusion_matrix(self, y_test, y_pred):
        """print confusion matrix"""
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(5, 3))
        sn.heatmap(cm, annot=True, fmt="d")
        plt.xlabel("Prediction")
        plt.ylabel("Truth")
        plt.show()

    def print_classification_report(self, y_test, y_pred):
        """Print classification report"""
        return classification_report(y_test, y_pred)

    def model_comparision(self, x_train, y_train):
        """Model comparison"""
        model_params = {
            "svm": {
                "model": svm.SVC(gamma="auto"),
                "params": {"C": [1, 10, 20], "kernel": ["rbf", "linear"]},
            },
            "random_forest": {
                "model": RandomForestClassifier(),
                "params": {"n_estimators": [1, 5, 10]},
            },
            "logistic_regression": {
                "model": LogisticRegression(
                    solver="liblinear", multi_class="auto"
                ),
                "params": {"C": [1, 5, 10]},
            },
        }
        scores = []
        for model_name, mp in model_params.items():
            clf = GridSearchCV(
                mp["model"], mp["params"], cv=5, return_train_score=False
            )
            clf.fit(x_train, y_train)
            scores.append(
                {
                    "model": model_name,
                    "best_score": clf.best_score_,
                    "best_params": clf.best_params_,
                }
            )

        df = pd.DataFrame(
            scores, columns=["model", "best_score", "best_params"]
        )
        return df

    def fasttext_classifier(self, train: pd.DataFrame, test: pd.DataFrame):
        """Fasttext Classifier"""
        train.to_csv(
            "log.train", columns=["fasttext_data"], index=False, header=False
        )
        test.to_csv(
            "log.test", columns=["fasttext_data"], index=False, header=False
        )
        model = fasttext.train_supervised(input="log.train")
        print(model.test("log.test"))
        return model

    def naive_bayes_classifier(self, x_train, x_test, y_train, y_test):
        """Naive Bayes classifier"""
        scaler = MinMaxScaler()
        scaled_train_embed = scaler.fit_transform(x_train)
        scaled_test_embed = scaler.transform(x_test)
        clf = MultinomialNB()
        clf.fit(scaled_train_embed, y_train)
        y_pred = clf.predict(scaled_test_embed)
        print(self.print_classification_report(y_test, y_pred))
        self.print_confusion_matrix(y_test, y_pred)

    def knn_classifier(self, x_train, x_test, y_train, y_test):
        """KNN Classifier"""
        clf = KNeighborsClassifier(n_neighbors=3, metric="euclidean")
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        print(self.print_classification_report(y_test, y_pred))
        self.print_confusion_matrix(y_test, y_pred)

    def gradient_boosting_classifier(self, x_train, x_test, y_train, y_test):
        """gradient_boosting_classifier"""
        clf = GradientBoostingClassifier()
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        print(self.print_classification_report(y_test, y_pred))
        self.print_confusion_matrix(y_test, y_pred)

    def run_fasttext_classifier(self):
        """Run fasttext classifier"""
        data_frame = self.read_csv_file(
            "sasai\src\sasai\log_analyzer\data\sample_data.csv"
        )
        data_frame = self.column_data_parsher(data_frame)
        data_frame = self.create_data_for_fasttext(data_frame)
        train, test = self.split_data_frame(data_frame, 0.25)
        model = self.fasttext_classifier(train, test)
        return model

    def return_stable_data_in_vectors(self):
        """Return stable data in vector form"""
        df = self.read_csv_file("data\sample_data.csv")
        df = self.map_error_classes_to_num(df)
        df = self.create_num_vector(df)
        x_train, x_test, y_train, y_test = self.split_data_frame_column_data(
            df.vector.values, df.label_num, 0.25
        )
        x_train = self.convert_in_2d_vector(x_train)
        x_test = self.convert_in_2d_vector(x_test)
        x_train, y_train = self.balance_the_data_class(x_train, y_train)
        x_train, y_train = self.balance_the_data_class(x_train, y_train)
        return (x_train, x_test, y_train, y_test)

    def run_knn_classifier(self):
        """Run KNN classifier"""
        x_train, x_test, y_train, y_test = self.return_stable_data_in_vectors()
        model = self.knn_classifier(x_train, x_test, y_train, y_test)
        return model

    def run_gradient_boosting_classifier(self):
        """Run KNN classifier"""
        x_train, x_test, y_train, y_test = self.return_stable_data_in_vectors()
        model = self.gradient_boosting_classifier(
            x_train, x_test, y_train, y_test
        )
        return model

    def run_naive_bayes_classifier(self):
        """Run KNN classifier"""
        x_train, x_test, y_train, y_test = self.return_stable_data_in_vectors()
        model = self.naive_bayes_classifier(x_train, x_test, y_train, y_test)
        return model


if __name__ == "__main__":
    la = LogAnalyzer()
    x_train, x_test, y_train, y_test = la.return_stable_data_in_vectors()
    print(la.model_comparision(x_train, y_train))
