import pandas as pd
from datetime import datetime


# =====================================================
# DROUGHT KEYWORDS
# =====================================================

DROUGHT_KEYWORDS = {

    # Vegetation
    "dry": 0.2,
    "drying": 0.3,
    "brown": 0.3,
    "yellow": 0.2,
    "wilting": 0.4,
    "wilted": 0.4,
    "dying": 0.5,
    "dead": 0.5,
    "curling": 0.3,

    # Crops
    "crop failure": 0.7,
    "poor harvest": 0.5,
    "stunted": 0.4,

    # Water
    "water shortage": 0.6,
    "stream dry": 0.7,
    "river dry": 0.7,
    "dam low": 0.6,
    "dam empty": 0.8,
    "borehole dry": 0.8,

    # Livestock
    "livestock dying": 1.0,
    "animal deaths": 1.0,
    "no grazing": 0.7,

    # Community
    "food shortage": 0.8,
    "hunger": 1.0,
    "water crisis": 1.0
}


POSITIVE_KEYWORDS = {

    "green": -0.2,
    "healthy": -0.2,
    "good rainfall": -0.3,
    "full dam": -0.4,
    "good harvest": -0.5
}


# =====================================================
# NOTES ANALYSIS
# =====================================================

def calculate_keyword_score(text):

    if pd.isna(text):
        return 0

    text = str(text).lower()

    score = 0

    for keyword, weight in DROUGHT_KEYWORDS.items():

        if keyword in text:
            score += weight

    for keyword, weight in POSITIVE_KEYWORDS.items():

        if keyword in text:
            score += weight

    score = max(0, score)

    return min(score, 1.0)


# =====================================================
# MAIN FUNCTION
# =====================================================

def fetch_community():

    import os
    SHEET_URL = os.environ.get(
        "COMMUNITY_SHEET_URL",
        "https://docs.google.com/spreadsheets/d/"
        "101wlyOmjbchCJuhvFVT5SPq89OILTpj_z2AWXGaUCd4"
        "/export?format=csv"
    )

    try:

        print("\nFetching community reports...")

        # =====================================================
        # LOAD GOOGLE SHEET
        # =====================================================

        df = pd.read_csv(SHEET_URL)

        # Local backup
        df.to_csv(
            "data/community_reports.csv",
            index=False
        )

        print(f"Loaded {len(df)} community reports")

        # =====================================================
        # DEBUG COLUMN NAMES
        # =====================================================

        print("\nAvailable columns:")
        print(df.columns.tolist())

        # =====================================================
        # UPDATE THESE TO MATCH YOUR SHEET
        # =====================================================

        community_col = "Which community are you reporting for?"

        rainfall_col = "Has there been useful rainfall during the last 7 days?"

        crop_col = "What is the level of crop water stress?"

        water_col = "What is the condition of local water sources?"

        livestock_col = "Are livestock experiencing water or grazing stress?"

        concern_col = "What is the level of concern among local farmers?"

        notes_col = "Additional observations"

        # =====================================================
        # SCORING MAPS
        # =====================================================

        rainfall_map = {
            "Yes": 0.0,
            "No": 1.0
        }

        stress_map = {
            "None": 0.0,
            "Low": 0.33,
            "Moderate": 0.66,
            "High": 1.0
        }

        water_map = {
            "Normal": 0.0,
            "Low": 0.5,
            "Critical": 1.0
        }

        # =====================================================
        # STRUCTURED SCORES
        # =====================================================

        df["rainfall_score"] = (
            df[rainfall_col]
            .map(rainfall_map)
            .fillna(0.0)
        )

        df["crop_score"] = (
            df[crop_col]
            .map(stress_map)
            .fillna(0.0)
        )

        df["water_score"] = (
            df[water_col]
            .map(water_map)
            .fillna(0.0)
        )

        df["livestock_score"] = (
            df[livestock_col]
            .map(stress_map)
            .fillna(0.0)
        )

        df["concern_score"] = (
            df[concern_col]
            .map(stress_map)
            .fillna(0.0)
        )

        # =====================================================
        # STRUCTURED COMMUNITY SCORE
        # =====================================================

        df["structured_score"] = (

            df["rainfall_score"] +
            df["crop_score"] +
            df["water_score"] +
            df["livestock_score"] +
            df["concern_score"]

        ) / 5

        # =====================================================
        # NOTES ANALYSIS
        # =====================================================

        df["keyword_score"] = (
            df[notes_col]
            .apply(calculate_keyword_score)
        )

        # =====================================================
        # FINAL COMMUNITY RISK
        # =====================================================

        df["community_risk"] = (

            0.85 * df["structured_score"] +

            0.15 * df["keyword_score"]

        )

        # =====================================================
        # TIMESTAMP
        # =====================================================

        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"]
        )

        # =====================================================
        # USE MOST RECENT REPORTS
        # =====================================================

        latest_reports = (

            df.sort_values("Timestamp")
              .tail(4)

        )

        community_risk = (
            latest_reports["community_risk"]
            .mean()
        )

        # =====================================================
        # SAVE COMMUNITY SUMMARY
        # =====================================================

        summary = pd.DataFrame({

            "date": [datetime.now()],

            "community_risk": [community_risk],

            "reports_used": [len(latest_reports)]

        })

        summary.to_csv(
            "data/community_latest.csv",
            index=False
        )

        print(
            f"\nCommunity Risk Score: "
            f"{community_risk:.3f}"
        )

        return {

            "status": "success",

            "community_risk": float(
                round(community_risk, 3)
            ),

            "reports_used": int(
                len(latest_reports)
            )

        }

    except Exception as e:

        print(
            f"\nCommunity Fetch Error: {e}"
        )

        return {

            "status": "error",

            "message": str(e)

        }


if __name__ == "__main__":

    result = fetch_community()

    print("\nResult:")
    print(result)