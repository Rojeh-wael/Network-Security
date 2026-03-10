# NetShield AI — Network Security Phishing Detection

An end-to-end machine learning web application that detects phishing websites using network and URL-based features. Built with a modular, production-ready architecture — from data ingestion and model training to a professional dark-themed web dashboard served by FastAPI.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikit-learn)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow)

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [ML Pipeline Stages](#ml-pipeline-stages)
- [Web Application](#web-application)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Data Ingestion to MongoDB](#data-ingestion-to-mongodb)
- [Running the Application](#running-the-application)
- [Docker Deployment](#docker-deployment)
- [Artifacts](#artifacts)
- [Author](#author)

---

## Overview

This project builds a complete machine learning system to classify URLs as **phishing** or **legitimate** using 30 network-derived features. It includes:

- **Full ML pipeline** — Data ingestion from MongoDB → schema validation → drift detection → KNN imputation → model training with GridSearchCV across 6 classifiers
- **Professional web interface** — Dark cybersecurity-themed dashboard with landing page, prediction upload, training controls, and interactive results
- **REST API** — FastAPI backend with Swagger docs for programmatic access
- **Experiment tracking** — MLflow integration via DagsHub for metric logging
- **Cloud-ready** — Dockerized with S3 artifact syncing

---

## Screenshots

| Page | Description |
|---|---|
| **Home** (`/`) | Hero section with animated shield, pipeline overview, model arsenal, and stats |
| **Predict** (`/predict-page`) | Drag-and-drop CSV upload with feature guide and output info |
| **Results** (`/predict`) | Summary cards (counts, phishing rate) + color-coded results table with download |
| **Train** (`/train-page`) | Visual pipeline stepper, config sidebar, async training trigger |
| **API Docs** (`/docs`) | Auto-generated Swagger UI from FastAPI |

---

## Project Structure

```
Network Security Project/
│
├── app.py                           # FastAPI web application entry point
├── main.py                          # CLI pipeline entry point
├── push_data.py                     # Upload CSV data to MongoDB
├── setup.py                         # Package setup (pip install -e .)
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container definition
├── .env                             # Environment variables (not committed)
│
├── templates/                       # Jinja2 HTML templates
│   ├── base.html                    # Shared layout (navbar, footer, CDN links)
│   ├── index.html                   # Landing / home page
│   ├── predict.html                 # CSV upload & prediction page
│   ├── table.html                   # Prediction results with summary stats
│   └── train.html                   # Model training dashboard
│
├── static/                          # Static assets
│   ├── css/style.css                # Custom dark cybersecurity theme
│   └── js/main.js                   # Frontend interactions
│
├── data_schema/
│   └── schema.yaml                  # Column names, types & schema definition
│
├── Network_Data/
│   └── phisingData.csv              # Raw source dataset
│
├── final_model/                     # Production model & preprocessor
│   ├── model.pkl                    # Best trained classifier
│   └── preprocessor.pkl             # Fitted KNN Imputer pipeline
│
├── prediction_output/
│   └── output.csv                   # Latest prediction results
│
├── artifacts/                       # Pipeline run outputs (timestamped)
│   └── <timestamp>/
│       ├── data_ingestion/
│       │   ├── feature_store/       # Full dataset from MongoDB
│       │   └── ingested/            # train.csv / test.csv splits
│       ├── data_validation/
│       │   ├── valid/               # Validated train/test CSVs
│       │   └── report.yaml          # Drift report
│       ├── data_transformation/
│       │   └── transformed/         # train.npy / test.npy arrays
│       └── model_trainer/
│           └── trained_model/       # Best model pickle
│
├── notebooks/                       # Jupyter notebooks for exploration
├── logs/                            # Application logs
│
└── networksecurity/                 # Core Python package
    ├── __init__.py
    ├── components/                  # Pipeline stage implementations
    │   ├── data_ingestion.py        # MongoDB → CSV → train/test split
    │   ├── data_validation.py       # Schema check & KS drift test
    │   ├── data_transformation.py   # KNN Imputer + StandardScaler
    │   └── model_trainer.py         # GridSearchCV across 6 models
    ├── entity/
    │   ├── config_entity.py         # Config dataclasses per stage
    │   └── artifacts_entity.py      # Artifact dataclasses per stage
    ├── constant/
    │   └── training_pipeline/       # All pipeline constants & hyperparams
    ├── pipeline/
    │   ├── training_pipeline.py     # Orchestrates all 4 stages + S3 sync
    │   └── batch_prediction.py      # Batch inference pipeline
    ├── cloud/
    │   └── s3_syncer.py             # AWS S3 artifact synchronization
    ├── utils/
    │   ├── main_utils/utils.py      # YAML, numpy, pickle, GridSearchCV helpers
    │   └── ml_utils/
    │       └── metric/
    │           └── classification_metric.py  # Accuracy, precision, recall, F1
    ├── exception/exception.py       # Custom exception with traceback
    └── logging/logger.py            # Centralized rotating logger
```

---

## Dataset

The dataset contains **30 numerical features** plus a target column, extracted from URLs and web pages to classify sites as phishing (`-1`) or legitimate (`1`).

| Feature Category | Examples |
|---|---|
| URL Properties | `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix` |
| Domain Info | `having_IP_Address`, `having_Sub_Domain`, `Domain_registeration_length`, `age_of_domain`, `DNSRecord` |
| SSL & Security | `SSLfinal_State`, `HTTPS_token`, `Favicon` |
| Page Content | `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email`, `Iframe`, `popUpWidnow` |
| Web Metrics | `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report` |
| Behaviour | `Redirect`, `on_mouseover`, `RightClick`, `Abnormal_URL`, `port` |
| **Target** | `Result` (`1` = Legitimate, `-1` = Phishing) |

- **MongoDB Database**: `NetworkSecurity`
- **Collection**: `PhishingData`
- **Schema**: `data_schema/schema.yaml`

---

## ML Pipeline Stages

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
- Builds a `sklearn.Pipeline` preprocessing object
- Saves transformed arrays as `.npy` files and the fitted preprocessor as `preprocessor.pkl`
- Output: `DataTransformationArtifact`

### 4. Model Training & Evaluation
- Trains **6 classifiers** with hyperparameter tuning via **GridSearchCV** (3-fold CV):

| Model | Key Hyperparameters |
|---|---|
| Logistic Regression | Default |
| Decision Tree | `criterion`, `max_depth`, `min_samples_split/leaf` |
| K-Nearest Neighbors | `n_neighbors`, `weights`, `metric` |
| Random Forest | `n_estimators`, `criterion`, `max_depth` |
| AdaBoost | `n_estimators`, `learning_rate` |
| Gradient Boosting | `n_estimators`, `learning_rate`, `max_depth` |

- Selects the **best model** by accuracy score
- Logs metrics (accuracy, precision, recall, F1) to **MLflow** via DagsHub
- Saves the trained model to `final_model/model.pkl`
- Output: `ModelTrainerArtifact`

---

## Web Application

The project includes a professional, dark-themed web interface built with **Jinja2**, **Bootstrap 5**, and **Font Awesome**:

### Pages

#### Home (`/`)
- Hero section with animated cybersecurity shield visual
- Stats strip: 30+ features, 6 models, 97%+ accuracy, <1s prediction
- "How It Works" — 4-step pipeline overview cards
- ML Models Arsenal — visual grid of all 6 classifiers
- Call-to-action section

#### Predict (`/predict-page`)
- Drag-and-drop file upload zone with live file preview
- Expected features reference panel (all 30 feature names)
- Output description panel

#### Results (`/predict` POST response)
- Summary cards: total rows, legitimate count, phishing count, phishing rate %
- Color-coded results table (green = Legitimate, red = Phishing badges)
- Download CSV button
- "New Prediction" link

#### Train Model (`/train-page`)
- Visual 5-step pipeline stepper with animated active/complete states
- Configuration sidebar (split ratio, KNN neighbors, CV folds, thresholds)
- Async "Start Training" button with spinner and success/error alerts

### Design
- **Theme**: Dark cybersecurity with glassmorphism effects
- **Colors**: `#00d4aa` accent on `#0a0e17` background
- **Typography**: Inter font family
- **Animations**: Orbiting dots, pulsing glow, hover transforms
- **Responsive**: Mobile-first Bootstrap grid

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home page (landing dashboard) |
| `GET` | `/predict-page` | Prediction upload page |
| `POST` | `/predict` | Upload CSV → run prediction → return results table |
| `GET` | `/train-page` | Training dashboard page |
| `GET` | `/train` | Trigger full ML training pipeline |
| `GET` | `/download-results` | Download latest `prediction_output/output.csv` |
| `GET` | `/docs` | FastAPI auto-generated Swagger UI |
| `GET` | `/redoc` | FastAPI ReDoc documentation |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.10** | Core language |
| **FastAPI** | Web framework & REST API |
| **Uvicorn** | ASGI server |
| **Jinja2** | HTML templating |
| **Bootstrap 5** | Responsive UI framework |
| **Font Awesome 6** | Icon library |
| **pandas / numpy** | Data manipulation |
| **scikit-learn** | ML models, preprocessing, GridSearchCV |
| **pymongo** | MongoDB Atlas connectivity |
| **MLflow + DagsHub** | Experiment tracking & metric logging |
| **scipy** | Kolmogorov–Smirnov drift detection |
| **python-dotenv** | Environment variable management |
| **dill / pickle** | Object serialization |
| **PyYAML** | Schema & config parsing |
| **certifi** | TLS certificate handling |
| **Docker** | Containerization |
| **AWS S3** | Artifact cloud storage |

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
conda activate ./venv

# Or using venv
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
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

## Running the Application

### Option A: Web Application (recommended)

```bash
python app.py
```

Open **http://localhost:8000** in your browser. From the web UI you can:
- Browse the landing page and project overview
- Upload a CSV file for phishing prediction
- Trigger model training from the dashboard
- Download prediction results as CSV
- Access the Swagger API docs at `/docs`

### Option B: CLI Pipeline

```bash
python main.py
```

Runs all 4 pipeline stages sequentially (ingestion → validation → transformation → training) and saves timestamped artifacts.

---

## Docker Deployment

### Build the image

```bash
docker build -t netshield-ai .
```

### Run the container

```bash
docker run -p 8000:8000 --env-file .env netshield-ai
```

Open **http://localhost:8000** to access the application.

---

## Artifacts

Each pipeline run creates a timestamped folder under `artifacts/`:

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
    ├── data_transformation/
    │   └── transformed/
    │       ├── train.npy
    │       └── test.npy
    └── model_trainer/
        └── trained_model/
            └── model.pkl
```

The production model and preprocessor are also saved to `final_model/` for use by the web app.

---

## Author

**Rojeh Wael**  
rojehwael@yahoo.com
