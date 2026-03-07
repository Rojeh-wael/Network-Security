from sklearn.model_selection import GridSearchCV
import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os,sys
import numpy as np
import pandas as pd
import dill
import pickle   
from sklearn.metrics import accuracy_score


def read_yaml_file(file_path:str)->dict:
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    


def write_yaml_file(file_path:str,data:dict):
    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,"w") as yaml_file:
            yaml.dump(data,yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    

def save_numpy_array_data(file_path:str,array:np.array):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path,"wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def load_numpy_array_data(file_path:str)->np.array:
    try:
        with open(file_path,"rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    

def evaluate_models(x_train,y_train,x_test,y_test,models:dict,params:dict)->dict:
    try:
        model_report:dict = {}
        for model_name,model in models.items():
            logging.info(f"Training {model_name} model")
            if model_name in params:
                gs=GridSearchCV(model,params[model_name],cv=3,n_jobs=-1,verbose=1)
                gs.fit(x_train,y_train)
                models[model_name] = gs.best_estimator_
            else:
                model.fit(x_train,y_train)
                models[model_name] = model
            y_test_pred = models[model_name].predict(x_test)
            test_score = accuracy_score(y_test,y_test_pred)
            model_report[model_name] = test_score
        return model_report
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e


def save_object(file_path:str,obj:object) -> None:
    try:
        logging.info(f"Saving object to file: {file_path}")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path,"wb") as file_obj:
            pickle.dump(obj,file_obj)
        logging.info(f"Object saved successfully to file: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def load_object(file_path:str)->object:
    try:
        logging.info(f"Loading object from file: {file_path}")
        with open(file_path,"rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e