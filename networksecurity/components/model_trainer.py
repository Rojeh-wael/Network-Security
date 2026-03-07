import os
import sys
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifacts_entity import DataTransformationArtifact,ModelTrainerArtifact,ClassificationMetricArtifact
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
)

class NetworkSecurityModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

    def track_mlflow(self,model_name:str,model_accuracy:float,precision_score:float,recall_score:float,f1_score:float):
        import mlflow
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("Network Security Model Training")
        with mlflow.start_run(run_name=model_name):
            mlflow.log_metric("model_accuracy", model_accuracy)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.log_metric("recall_score", recall_score)
            mlflow.log_metric("f1_score", f1_score)

    def model_predict(self,x_train,y_train,x_test,y_test):
        models = {
            "Logistic Regression": LogisticRegression(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "K-Nearest Neighbors": KNeighborsClassifier(),
            "Random Forest": RandomForestClassifier(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
        }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            "K-Nearest Neighbors": {
                'n_neighbors': [3, 5, 7, 9],
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean', 'manhattan', 'minkowski']
            },
            "Random Forest": {
                'n_estimators': [100, 200, 300],
                'criterion': ['gini', 'entropy', 'log_loss'],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            "AdaBoost": {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 1]
            },
            "Gradient Boosting": {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.01, 0.1, 1],
                    'max_depth': [3, 5, 7]
            }
        }
        model_report:dict = evaluate_models(x_train=x_train,y_train=y_train,x_test=x_test,y_test=y_test,models=models,params=params)
        best_model_score = max(model_report.values())
        best_model_name = max(model_report,key=model_report.get)
        best_model = models[best_model_name]

        y_test_pred = best_model.predict(x_test)
        classification_metric = get_classification_score(y_true=y_test,y_pred=y_test_pred,model_name=best_model_name)

        ## Track the MlFlow
        self.track_mlflow(model_name=best_model_name,model_accuracy=classification_metric.model_accuracy,precision_score=classification_metric.precision_score,recall_score=classification_metric.recall_score,f1_score=classification_metric.f1_score)
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.model_file_path,
            train_metric_artifact=classification_metric,
            test_metric_artifact=classification_metric
        )

        return best_model

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            logging.info(f"Loading transformed training and testing data")
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            x_train,y_train = train_arr[:,:-1],train_arr[:,-1]
            x_test,y_test = test_arr[:,:-1],test_arr[:,-1]

            logging.info(f"Training the model")
            model = self.model_predict(x_train,y_train,x_test,y_test)

            logging.info(f"Saving the trained model")
            save_object(self.model_trainer_config.model_file_path,model)

            train_metric_artifact = get_classification_score(y_train,model.predict(x_train),model_name="train_model")
            test_metric_artifact = get_classification_score(y_test,model.predict(x_test),model_name="test_model")

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.model_file_path,
                train_metric_artifact=train_metric_artifact,
                test_metric_artifact=test_metric_artifact
            )
            return model_trainer_artifact   
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        




