from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import NetworkSecurityModelTrainer
from networksecurity.entity.config_entity import ModelTrainerConfig, TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig
from networksecurity.logging.logger import logging

if __name__ == "__main__":
    try:
        logging.info("Starting the training pipeline")
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        logging.info("Initiating data ingestion")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data initiation completed successfully")
        print(data_ingestion_artifact)
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_validation_config,data_ingestion_artifact)
        logging.info("Initiating data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed successfully")
        print(data_validation_artifact)
        logging.info("Data transformation started successfully")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(data_transformation_config,data_validation_artifact)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed successfully")
        print(data_transformation_artifact)

        logging.info("Model training started successfully")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = NetworkSecurityModelTrainer(model_trainer_config,data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed successfully")   
        print(model_trainer_artifact)
    except Exception as e:
        logging.error(f"Error occurred in the training pipeline: {e}")