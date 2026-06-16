from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load .env in local dev; Railway injects env vars in production

from data.fetch_nasa import fetch_nasa
from data.fetch_openmeteo import fetch_openmeteo
from data.fetch_nvdi import fetch_ndvi

from data.build_latest_features import build_latest_features
from data.run_inference import run_inference

from data.fetch_community import fetch_community
from data.environment_score import environmental_score

# Optional
from data.send_email import send_report

app = FastAPI(
    title="TINHLE-AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# WEIGHTS
# =====================================

MODEL_WEIGHT = 0.50
ENVIRONMENT_WEIGHT = 0.30
COMMUNITY_WEIGHT = 0.20


# =====================================
# HOME
# =====================================

@app.get("/")
def home():
    return {
        "service": "TINHLE-AI",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health():
    """Health check endpoint for uptime monitoring."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# =====================================
# CORE PREDICTION LOGIC
# =====================================

def run_tinhle_pipeline():

    # -----------------------------
    # FETCH ENVIRONMENTAL DATA
    # -----------------------------

    fetch_nasa()
    fetch_openmeteo()
    fetch_ndvi()

    # -----------------------------
    # FETCH COMMUNITY DATA
    # -----------------------------

    community_result = fetch_community()

    # -----------------------------
    # BUILD FEATURES
    # -----------------------------

    build_latest_features()

    # -----------------------------
    # RUN ML MODELS
    # -----------------------------

    prediction = run_inference()

    # -----------------------------
    # ENVIRONMENTAL SCORE
    # -----------------------------

    environmental_result = environmental_score()

    # -----------------------------
    # EXTRACT VALUES
    # -----------------------------

    drought_probability = (
        prediction["drought_probability"]
    )

    community_risk = (
        community_result["community_risk"]
    )

    environmental_score_value = (
        environmental_result["environmental_score"]
    )

    # -----------------------------
    # TINHLE FUSION ENGINE
    # -----------------------------

    tinhle_risk = (

        MODEL_WEIGHT * drought_probability +

        ENVIRONMENT_WEIGHT * environmental_score_value +

        COMMUNITY_WEIGHT * community_risk

    )

    # -----------------------------
    # FINAL LABEL
    # -----------------------------

    if tinhle_risk < 0.30:

        tinhle_risk_class = "LOW"

    elif tinhle_risk < 0.60:

        tinhle_risk_class = "MODERATE"

    else:

        tinhle_risk_class = "HIGH"

    # -----------------------------
    # RESPONSE
    # -----------------------------

    response = {

        "location": "Ruwa",

        "timestamp":
            datetime.now().isoformat(),

        # Rainfall Model

        "predicted_rainfall":
            prediction["predicted_rainfall"],

        # Drought Model

        "drought_probability":
            prediction["drought_probability"],

        "drought_class":
            prediction["drought_class"],

        # Environmental Engine

        "environmental_score":
            round(
                environmental_score_value,
                3
            ),

        "environmental_label":
            environmental_result[
                "environmental_label"
            ],

        # Community Intelligence

        "community_risk":
            round(
                community_risk,
                3
            ),

        "reports_used":
            community_result[
                "reports_used"
            ],

        # Final TINHLE Risk

        "tinhle_risk":
            round(
                tinhle_risk,
                3
            ),

        "tinhle_risk_class":
            tinhle_risk_class

    }

    return response


# =====================================
# PREDICT
# =====================================

@app.get("/predict")
def predict():

    return run_tinhle_pipeline()


# =====================================
# SEND EMAIL REPORT
# =====================================

@app.get("/send-report")
def send_report_endpoint():

    report = run_tinhle_pipeline()

    # Uncomment when send_email.py exists

    send_report(report)

    return {

        "status": "report_sent",

        "report": report

    }