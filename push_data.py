import os
import sys
import json
from dotenv import load_dotenv
import pandas as pd 
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import certifi


load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

print(f"MongoDB URL: {MONGO_DB_URL}")


ca=certifi.where()





class PushData():




    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            logging.info("MongoDB client initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing MongoDB client: {e}")
            raise NetworkSecurityException(e, sys)
    
    def csv_to_json(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df.reset_index(drop=True, inplace=True)
            records=list(json.loads(df.T.to_json()).values())
            logging.info(f"CSV file '{file_path}' converted to JSON successfully.")
            return records
        except Exception as e:
            logging.error(f"Error converting CSV to JSON: {e}")
            raise NetworkSecurityException(e, sys)
        
    def push_data_to_mongodb(self, records,database, collection):
        try:
            self.database=database
            self.collection=collection
            self.records=records

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.db=self.mongo_client[self.database]
            db_collection=self.db[self.collection]
            db_collection.insert_many(self.records)
            logging.info(f"Data pushed to MongoDB collection '{self.collection}' in database '{self.database}' successfully.")
            return len(self.records)
        except Exception as e:
            logging.error(f"Error pushing data to MongoDB: {e}")
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH="E:\\Network Security Project\\Network_Data\\phisingData.csv"
    DATABASE="NetworkSecurity"
    COLLECTION="PhishingData"
    networkobj=PushData()
    records=networkobj.csv_to_json(FILE_PATH)
    print(records)
    no_of_records=networkobj.push_data_to_mongodb(records,DATABASE,COLLECTION)
    print(f"{no_of_records} records inserted successfully into MongoDB collection '{COLLECTION}' in database '{DATABASE}'.")