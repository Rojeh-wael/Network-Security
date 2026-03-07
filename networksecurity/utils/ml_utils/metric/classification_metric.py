from networksecurity.entity.artifacts_entity import ClassificationMetricArtifact
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
import sys
import os


def get_classification_score(y_true,y_pred,model_name)->ClassificationMetricArtifact:
    try:
        model_accuracy = accuracy_score(y_true,y_pred)
        precision = precision_score(y_true,y_pred)
        recall = recall_score(y_true,y_pred)
        f1score = f1_score(y_true,y_pred)
        classification_metric_artifact = ClassificationMetricArtifact(model_name=model_name,model_accuracy=model_accuracy,precision_score=precision,recall_score=recall,f1_score=f1score)
        return classification_metric_artifact
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e