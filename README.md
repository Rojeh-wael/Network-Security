# Network Security — Phishing URL Detection

An end-to-end machine learning pipeline for detecting phishing websites using network and URL-based features. The project follows a modular, production-ready architecture with clearly separated stages for data ingestion, validation, and transformation.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Pipeline Stages](#pipeline-stages)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Data Ingestion to MongoDB](#data-ingestion-to-mongodb)
- [Running the Pipeline](#running-the-pipeline)
- [Artifacts](#artifacts)
- [Author](#author)

---

## Overview

This project builds a machine learning pipeline to classify URLs as **phishing** or **legitimate**. Raw data is stored in a **MongoDB Atlas** database and flows through a series of automated stages — ingestion, schema validation, drift detection, and feature transformation — before being used to train a classifier.

The codebase is structured as an installable Python package (`networksecurity`) with dedicated modules for configuration, entities, exceptions, logging, utilities, and pipeline components.

---

## Project Structure

```
Network Security Project/
├── main.py                          # Pipeline entry point
├── push_data.py                     # Utility to upload CSV data to MongoDB
├── setup.py                         # Package setup
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container definition
│
├── data_schema/
│   └── schema.yaml                  # Column names, types & schema definition
│
├── Network_Data/
│   └── phisingData.csv              # Raw source dataset
│
├── artifacts/                       # Pipeline run outputs (timestamped)
│   └── <timestamp>/
│       ├── data_ingestion/
│       │   ├── feature_store/       # Full dataset exported from MongoDB
│       │   └── ingested/            # train.csv / test.csv splits
│       ├── data_validation/
│       │   ├── valid/               # Validated train/test CSVs
│       │   └── report.yaml          # Column & drift validation report
│       └── data_transformation/
│           └── transformed/         # train.npy / test.npy arrays
│
├── notebooks/                       # Jupyter notebooks for exploration
│
└── networksecurity/                 # Core package
    ├── components/
    │   ├── data_ingestion.py
    │   ├── data_validation.py
    │   └── data_transformation.py
    ├── entity/
    │   ├── config_entity.py         # Config dataclasses for each stage
    │   └── artifacts_entity.py      # Artifact dataclasses for each stage
    ├── constant/
    │   └── training_pipeline/       # All pipeline constants & hyperparameters
    ├── pipeline/                    # High-level pipeline orchestration
    ├── utils/
    │   └── main_utils/utils.py      # YAML, numpy, pickle helpers
    ├── exception/exception.py       # Custom exception with traceback info
    └── logging/logger.py            # Centralized logger
```

---

## Dataset

The dataset contains **31 numerical features** extracted from URLs and web pages, used to classify a site as phishing (`-1`) or legitimate (`1`).

| Feature Category | Examples |
|---|---|
| URL Properties | `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix` |
| Domain Info | `having_IP_Address`, `having_Sub_Domain`, `Domain_registeration_length`, `age_of_domain`, `DNSRecord` |
| SSL & Security | `SSLfinal_State`, `HTTPS_token`, `Favicon` |
| Page Content | `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email`, `Iframe`, `popUpWidnow` |
| Web Metrics | `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report` |
| Behaviour | `Redirect`, `on_mouseover`, `RightClick`, `Abnormal_URL`, `port` |
| **Target** | `Result` |

- **MongoDB Database**: `NetworkSecurity`
- **Collection**: `PhishingData`
- **Schema file**: `data_schema/schema.yaml`

---

## Pipeline Stages

### 1. Data Ingestion
- Connects to MongoDB Atlas using `MONGO_DB_URL` from `.env`
- Exports the full collection as a CSV to the **feature store**
- Splits data into **train (80%)** and **test (20%)** sets
- Output: `DataIngestionArtifact`

### 2. Data Validation
- Validates that the number of columns matches the schema (`schema.yaml`)
- Detects **data drift** between the train and test sets using the Kolmogorov–Smirnov test (`scipy.stats.ks_2samp`) with a threshold of `p < 0.05`
- Saves a drift report as `report.yaml`
- Output: `DataValidationArtifact`

### 3. Data Transformation
- Handles missing values using **KNN Imputer** (`n_neighbors=3`, `weights="uniform"`)
- Scales features with **StandardScaler**
- Builds a `sklearn.Pipeline` object (`imputer → scaler`)
- Saves transformed arrays as `.npy` files and the fitted preprocessor as `preprocessor.pkl`
- Output: `DataTransformationArtifact`

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| pandas / numpy | Data manipulation |
| scikit-learn | ML preprocessing & pipeline |
| pymongo | MongoDB connectivity |
| certifi | TLS certificate handling |
| scipy | Statistical drift detection |
| python-dotenv | Environment variable management |
| dill / pickle | Object serialization |
| PyYAML | Schema & config file parsing |

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd "Network Security Project"
```

### 2. Create and activate a virtual environment

```bash
# Using conda
conda create -p venv python=3.10 -y
conda activate "e:\Network Security Project\venv"

# Or using venv
python -m venv venv
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
MONGO_DB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

> The `MONGO_DB_URL` is loaded automatically by `python-dotenv` at runtime.

---

## Data Ingestion to MongoDB

Before running the pipeline, upload the raw dataset to MongoDB:

```bash
python push_data.py
```

This script:
1. Reads `Network_Data/phisingData.csv`
2. Converts each row to a JSON record
3. Inserts all records into the `PhishingData` collection in the `NetworkSecurity` database

---

## Running the Pipeline

```bash
python main.py
```

This executes all three pipeline stages sequentially:
1. Data Ingestion
2. Data Validation
3. Data Transformation

Timestamped output artifacts are saved under the `artifacts/` directory.

---

## Artifacts

Each pipeline run creates a timestamped folder under `artifacts/` with the following structure:

```
artifacts/
└── MM-DD-YYYY-HH-MM-SS/
    ├── data_ingestion/
    │   ├── feature_store/PhishingData.csv
    │   └── ingested/
    │       ├── train.csv
    │       └── test.csv
    ├── data_validation/
    │   ├── valid/
    │   │   ├── train.csv
    │   │   └── test.csv
    │   └── report.yaml
    └── data_transformation/
        └── transformed/
            ├── train.npy
            └── test.npy
```

---

## Author

**Rojeh Wael**  
rojehwael@yahoo.com
