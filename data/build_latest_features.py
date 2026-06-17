import pandas as pd
import numpy as np


def build_latest_features():

    # =====================================
    # LOAD DATA
    # =====================================
    nasa = pd.read_csv("data/nasa_latest.csv")
    meteo = pd.read_csv("data/openmeteo_latest.csv")
    ndvi = pd.read_csv("data/ndvi_latest.csv")

    nasa["date"] = pd.to_datetime(nasa["date"])
    meteo["date"] = pd.to_datetime(meteo["date"])
    ndvi["date"] = pd.to_datetime(ndvi["date"])

    # =====================================
    # SORT
    # =====================================
    nasa = nasa.sort_values("date")
    meteo = meteo.sort_values("date")
    ndvi = ndvi.sort_values("date")

    # =====================================
    # MERGE
    # =====================================
    df = pd.merge(nasa, meteo, on="date", how="outer")
    df = pd.merge(df, ndvi, on="date", how="outer")

    df = df.sort_values("date").reset_index(drop=True)

    # =====================================
    # CLEAN / FILL
    # =====================================
    numeric_cols = [
        "rainfall_nasa",
        "temp_nasa",
        "rainfall_openmeteo",
        "temp_max",
        "temp_min",
        "ndvi"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # rainfall missing -> assume zero
    df["rainfall_nasa"] = df["rainfall_nasa"].fillna(0)
    df["rainfall_openmeteo"] = df["rainfall_openmeteo"].fillna(0)

    # temperatures -> interpolate
    df["temp_nasa"] = df["temp_nasa"].interpolate().ffill().bfill()
    df["temp_max"] = df["temp_max"].interpolate().ffill().bfill()
    df["temp_min"] = df["temp_min"].interpolate().ffill().bfill()

    # NDVI -> carry forward between MODIS acquisitions
    df["ndvi"] = df["ndvi"].interpolate().ffill().bfill()

    # =====================================
    # BASE FEATURES
    # =====================================
    df["rainfall"] = df["rainfall_openmeteo"]

    df["temp_mean"] = (
        df["temp_max"] +
        df["temp_min"]
    ) / 2

    # =====================================
    # CALENDAR FEATURES
    # =====================================
    df["day_of_year"] = df["date"].dt.dayofyear
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    # =====================================
    # ROLLING FEATURES
    # =====================================
    df["rainfall_7d_avg"] = (
        df["rainfall"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    df["rainfall_30d_avg"] = (
        df["rainfall"]
        .rolling(window=30, min_periods=1)
        .mean()
    )

    df["temp_7d_avg"] = (
        df["temp_mean"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    df["temp_30d_avg"] = (
        df["temp_mean"]
        .rolling(window=30, min_periods=1)
        .mean()
    )

    df["ndvi_7d_avg"] = (
        df["ndvi"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    df["ndvi_30d_avg"] = (
        df["ndvi"]
        .rolling(window=30, min_periods=1)
        .mean()
    )

    # =====================================
    # LAG FEATURES
    # =====================================
    for lag in [1, 7, 30]:
        df[f"rainfall_lag_{lag}"] = df["rainfall"].shift(lag)
        df[f"temp_lag_{lag}"] = df["temp_mean"].shift(lag)
        df[f"ndvi_lag_{lag}"] = df["ndvi"].shift(lag)

    # =====================================
    # FILL LAG NaNs
    # =====================================
    lag_cols = [
        "rainfall_lag_1", "rainfall_lag_7", "rainfall_lag_30",
        "temp_lag_1", "temp_lag_7", "temp_lag_30",
        "ndvi_lag_1", "ndvi_lag_7", "ndvi_lag_30"
    ]

    for col in lag_cols:
        df[col] = df[col].ffill().bfill()

    # =====================================
    # PLACEHOLDER TARGETS
    # =====================================
    df["rainfall_t+7"] = np.nan
    df["drought_label"] = np.nan

    # =====================================
    # USE ONLY THE LATEST COMPLETE ROW
    # =====================================
    latest = df.tail(1).copy()

    latest.to_csv(
        "data/latest_inference.csv",
        index=False
    )

    print("[OK] latest_inference.csv generated")
    print(latest.T)


if __name__ == "__main__":
    build_latest_features()