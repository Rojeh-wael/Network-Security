from networksecurity.entity.artifacts_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
import os,sys
import pandas as pd
from scipy.stats import ks_2samp
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file



class DataValidation:
    def __init__(self,data_validation_config:DataValidationConfig,data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'>>'*20} Data Validation {'<<'*20}")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.schema_file_path = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        

    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        
    def validate_number_of_columns(self,df:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self.schema_file_path["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Dataframe has columns: {df.shape[1]}")
            if df.shape[1] == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        
    def detect_data_drift(self,base_df:pd.DataFrame,current_df:pd.DataFrame,threshold=0.05)->bool:
        try:
            drift_report = {}
            for column in base_df.columns:
                base_data = base_df[column]
                current_data = current_df[column]
                p_value = ks_2samp(base_data,current_data).pvalue
                drift_report[column] = {
                    "p_value": float(p_value),
                    "drift_status": p_value < threshold
                }
            write_yaml_file(self.data_validation_config.drift_report_name,drift_report)
            return drift_report
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            logging.info(f"Reading training and testing file for validation")
            train_df = pd.read_csv(self.data_ingestion_artifact.training_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.testing_file_path)

            ## Validate number of columns
            status = self.validate_number_of_columns(train_df)
            if not status:
                logging.info("Train dataframe does not contain all columns")
            status = self.validate_number_of_columns(test_df)
            if not status:
                logging.info("Test dataframe does not contain all columns")

            ## Detect data drift
            status = self.detect_data_drift(base_df=train_df, current_df=test_df)

            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            validation_status = True

            return DataValidationArtifact(
                validation_status=validation_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_name
            )
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e