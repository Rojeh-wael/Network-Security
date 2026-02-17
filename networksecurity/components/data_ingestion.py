from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifacts_entity import DataIngestionArtifact
import os
import sys
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) 
        
    def export_collection_as_dataframe(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]
            df = pd.DataFrame(list(collection.find()))
            
            if "_id" in df.columns.to_list():
                df = df.drop("_id", axis=1)
            
            df.replace({np.inf: np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_as_feature_store(self):
        try:
            feature_store_dir = self.data_ingestion_config.feature_store_dir
            os.makedirs(feature_store_dir, exist_ok=True)
            dataframe = self.export_collection_as_dataframe()
            feature_store_file_path = os.path.join(
                feature_store_dir, 
                self.data_ingestion_config.collection_name + ".csv"
            )
            dataframe.to_csv(feature_store_file_path, index=False)
            return feature_store_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, 
                test_size=self.data_ingestion_config.train_test_split_ratio, 
                random_state=42
            )
            # Use the correct attribute for directory path (e.g., training_file_path)
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            train_file_path = self.data_ingestion_config.training_file_path
            test_file_path = self.data_ingestion_config.testing_file_path
            
            train_set.to_csv(train_file_path, index=False)
            test_set.to_csv(test_file_path, index=False)
            
            return train_file_path, test_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            # Export data to feature store and get file path
            feature_store_file_path = self.export_data_as_feature_store()
            
            # Read the dataframe for splitting
            dataframe = self.export_collection_as_dataframe()
            
            # Split data and get file paths
            train_file_path, test_file_path = self.split_data_as_train_test(dataframe)
            
            # Create artifact
            dataingestionartifact = DataIngestionArtifact(
                data_ingestion_dir=self.data_ingestion_config.data_ingestion_dir,
                training_file_path=train_file_path,
                testing_file_path=test_file_path,
                feature_store_file_path=feature_store_file_path
            )
            
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)