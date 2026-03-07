from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    """Data Ingestion Artifact"""

    data_ingestion_dir: str
    feature_store_file_path: str
    training_file_path: str
    testing_file_path: str


@dataclass
class DataValidationArtifact:

    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str


@dataclass
class DataTransformationArtifact:

    transformed_train_file_path: str
    transformed_test_file_path: str
    preprocessor_object_file_path: str



@dataclass
class ClassificationMetricArtifact:

    model_name: str
    model_accuracy: float
    precision_score: float
    recall_score: float
    f1_score: float
    
@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact