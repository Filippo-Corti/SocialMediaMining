import itertools
from typing import Any

import joblib
import numpy as np
import spacy
from imblearn.over_sampling import SMOTE
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score


def precision_recall_weighted(y_true, y_pred):
    """Custom scorer that weights 70% precision and 30% recall"""
    precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
    recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
    # Weight precision 3x more than recall
    return 0.70 * precision + 0.30 * recall



class SpacyVectorTransformer(BaseEstimator, TransformerMixin):
    """
    A sklearn Transformer that preprocesses the field of a class using spacy
    """

    def __init__(
            self,
            model: str = 'en_core_web_md',
            field_name: str = 'content'
    ):
        self.model = model
        self.field_name = field_name
        self.nlp = None

    def fit(self, X, y=None):  # Does nothing (only loads model)
        self.nlp = spacy.load(self.model)
        return self

    def transform(self, X):  # Transforms with nlp(content)
        return np.vstack([doc.vector for doc in self.nlp.pipe(X[self.field_name], batch_size=64, n_process=3)])


def get_configurations_grid_for_precision() -> list[Any]:
    """
    Returns a grid of pipeline configurations, specialized on boosting precision for
    an underrepresented "1" class.
    """
    sampler_configs = [
        {
            'sampler': [None],
        },
        {
            'sampler': [SMOTE(random_state=42)],
            'sampler__sampling_strategy': [0.6, 0.8]
        },
    ]

    dim_reduction_configs = [
        {
            'dim_reduction': [None]
        },
        {
            'dim_reduction': [PCA(random_state=42)],
            'dim_reduction__n_components': [0.95]
        },
    ]

    classifier_configs = [
        {
            'classifier': [RandomForestClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100],
            'classifier__max_depth': [4, 8],
            'classifier__min_samples_split': [40, 60],
            'classifier__min_samples_leaf': [30, 60],
            'classifier__max_features': [0.3, 0.5],
            'classifier__class_weight': [{0: 1, 1: 1}, {0: 1, 1: 1.5}, {0: 2, 1: 1}],
        },
        {
            'classifier': [LogisticRegression(solver='liblinear', max_iter=10000, random_state=42)],
            'classifier__C': [0.01, 0.05],
            'classifier__penalty': ['l1'],
            'classifier__class_weight': [{0: 1, 1: 1}, {0: 1, 1: 1.5}, {0: 2, 1: 1}]
        }
    ]

    all_configs = [
        dict(itertools.chain(*(e.items() for e in configuration)))
        for configuration in itertools.product(
            sampler_configs,
            dim_reduction_configs,
            classifier_configs
        )
    ]
    return all_configs


class ClassifierWithThresholdModel:
    def __init__(self, pipeline, preprocessor, threshold):
        self.pipeline = pipeline
        self.preprocessor = preprocessor
        self.threshold = threshold

    def predict(self, X):
        """Main prediction method with threshold"""
        X_processed = self.preprocessor.transform(X)
        probas = self.pipeline.predict_proba(X_processed)
        return (probas[:, 1] >= self.threshold).astype(int)

    def predict_proba(self, X):
        """Get probabilities if needed"""
        X_processed = self.preprocessor.transform(X)
        return self.pipeline.predict_proba(X_processed)

    @staticmethod
    def save_model(model, path):
        """Saves the model in the storage"""
        model_package = {
            'pipeline': model.pipeline,
            'preprocessor': model.preprocessor,
            'threshold': model.threshold
        }

        joblib.dump(model_package, path)
        print(f"Model exported to {path}")

    @staticmethod
    def load_model(path):
        """Loads the model from the storage"""
        model_package = joblib.load(path)
        final_model = ClassifierWithThresholdModel(
            pipeline=model_package['pipeline'],
            preprocessor=model_package['preprocessor'],
            threshold=model_package['threshold']
        )
        return final_model


class StanceCrossPredictor:

    def __init__(
            self,
            republican_model : ClassifierWithThresholdModel,
            democratic_model : ClassifierWithThresholdModel,
    ):
        self.republican_model = republican_model
        self.democratic_model = democratic_model

    def predict(self, X):
        """
        Get a prediction for X.
        0 is Neutral, 1 is Republican, 2 is Democratic
        """
        rep_predictions = self.republican_model.predict(X)
        dem_predictions = self.democratic_model.predict(X)

        def merge(r, d):
            match(r, d):
                case (0, 0): return 0
                case (1, 0): return 1
                case (0, 1): return 2
                case (1, 1): return 0

            assert False, f"Unexpected values for {r} and {d}" # Should never happen

        final_predictions = [
            merge(r, d)
            for r, d in zip(rep_predictions, dem_predictions)
        ]
        return final_predictions