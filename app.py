import sys
import os
import certifi
import pymongo
import pandas as pd
import numpy as np
import json
from networksecurity.constant import training_pipeline
from networksecurity.pipeline.training_pipeline import NetworkSecurityTrainingPipeline
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,UploadFile,Request
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run
from fastapi.responses import RedirectResponse, Response
from starlette.responses import Response
from dotenv import load_dotenv
from networksecurity.utils.main_utils.utils import load_object 
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

ca=certifi.where()


load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)


client = pymongo.MongoClient(mongo_db_url,tlsCAFile=ca)
db = client[DATA_INGESTION_DATABASE_NAME]
collection = db[DATA_INGESTION_COLLECTION_NAME]



app=FastAPI()
templates = Jinja2Templates(directory="templates")
origins=["*"]

preprocessor = load_object("final_model/preprocessor.pkl")
model = load_object("final_model/model.pkl")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")



@app.get("/train")
async def train_route():
    try:
        training_pipeline_config = TrainingPipelineConfig()
        training_pipeline = NetworkSecurityTrainingPipeline(training_pipeline_config)
        training_pipeline.run_pipeline()
        return Response(content="Training successful", media_type="text/plain")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


@app.post("/predict")
def predict_route(request: Request, file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        network_data = preprocessor.transform(df.drop(columns=["Result"], errors="ignore"))
        y_pred = model.predict(network_data)
        df["predicted_column"] = np.where(y_pred == 1, "Legitimate", "Phishing")
        df.to_csv("prediction_output/output.csv", index=False)
        table = df.head(100).to_html(classes="table table-striped", index=False)
        return templates.TemplateResponse(
            "table.html",
            {"request": request, "table": table, "total_rows": len(df)},
        )
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000, timeout_keep_alive=300)