import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.constant.training_pipeline import TARGET_COLUMN,DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifacts_entity import DataValidationArtifact,DataTransformationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file


class DataTransformation:
    def __init__(self,data_transformation_config:DataTransformationConfig,data_validation_artifact:DataValidationArtifact):
        try:
            logging.info(f"{'>>'*20} Data Transformation {'<<'*20}")
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    def get_data_transformer_object(cls):
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            processor:Pipeline=Pipeline(steps=[
                ("imputer",imputer),
                ("scaler",StandardScaler())
            ])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        
    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Reading validated training and testing data for transformation")
            train_df = pd.read_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = pd.read_csv(self.data_validation_artifact.valid_test_file_path)
            logging.info(f"Splitting input and target features from training and testing dataframe")
            X_train = train_df.drop(TARGET_COLUMN,axis=1)
            y_train = train_df[TARGET_COLUMN]
            X_test = test_df.drop(TARGET_COLUMN,axis=1)
            y_test = test_df[TARGET_COLUMN]
            logging.info(f"Initializing imputer and scaler for transformation")
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            scaler = StandardScaler()
            pipeline = Pipeline(steps=[
                ("imputer",imputer),
                ("scaler",scaler)
            ])
            logging.info(f"Fitting and transforming training data")
            X_train_transformed = pipeline.fit_transform(X_train)
            logging.info(f"Transforming testing data")
            X_test_transformed = pipeline.transform(X_test)
            logging.info(f"Saving transformed training and testing data as numpy arrays")
            train_arr = np.c_[X_train_transformed,np.array(y_train)]
            test_arr = np.c_[X_test_transformed,np.array(y_test)]
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,test_arr)
            logging.info(f"Saving preprocessor object")
            save_object(self.data_transformation_config.preprocessor_object_file_path,pipeline)
            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                preprocessor_object_file_path=self.data_transformation_config.preprocessor_object_file_path
            )
            preprocessor=self.get_data_transformer_object()
            preprocessor_object=preprocessor.fit(X_train)
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
