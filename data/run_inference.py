import joblib
import pandas as pd


def align_features(df, model):
    """
    Keeps ONLY model features.
    Adds missing ones as 0.
    Ignores extra ones completely.
    """

    model_features = list(model.feature_names_in_)

    # 1. DROP unknown features
    df = df[[col for col in df.columns if col in model_features]]

    # 2. ADD missing features
    for col in model_features:
        if col not in df.columns:
            df[col] = 0

    # 3. enforce order
    df = df[model_features]

    # 4. safety fill
    df = df.fillna(0)

    return df


def run_inference():

    # =========================
    # LOAD DATA
    # =========================
    df = pd.read_csv("data/latest_inference.csv")

    # =========================
    # LOAD MODELS
    # =========================
    rainfall_model = joblib.load("models/best_rainfall_model.joblib")
    drought_model = joblib.load("models/best_drought_classifier.joblib")

    # =========================
    # ALIGN FEATURES PER MODEL
    # =========================
    df_rain = align_features(df.copy(), rainfall_model)
    df_drought = align_features(df.copy(), drought_model)

    # =========================
    # PREDICTIONS
    # =========================
    rainfall_pred = rainfall_model.predict(df_rain)[0]
    rainfall_pred = max(0.0, rainfall_pred)

    drought_prob = None
    drought_class = None

    # handle classifier safely
    if hasattr(drought_model, "predict_proba"):
        drought_prob = drought_model.predict_proba(df_drought)[0][1]

    drought_class = drought_model.predict(df_drought)[0]

    # =========================
    # OUTPUT
    # =========================
    result = {
        "predicted_rainfall": float(rainfall_pred),
        "drought_probability": float(drought_prob) if drought_prob is not None else None,
        "drought_class":(
            "HIGH" if str(drought_class) == "1" else "LOW")
    }

    print(result)

    return result


if __name__ == "__main__":
    run_inference()