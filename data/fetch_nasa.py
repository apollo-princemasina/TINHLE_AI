import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def fetch_nasa():

    # =========================
    # LOCATION
    # =========================
    LAT = -17.8875
    LON = 31.2444

    # =========================
    # DATE RANGE
    # =========================
    end_date = datetime.today()
    start_date = end_date - timedelta(days=35)

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    # =========================
    # NASA POWER API
    # =========================
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=PRECTOTCORR,T2M"
        f"&community=AG"
        f"&longitude={LON}"
        f"&latitude={LAT}"
        f"&start={start_str}"
        f"&end={end_str}"
        f"&format=JSON"
    )

    print("Fetching NASA POWER data...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rain = data["properties"]["parameter"]["PRECTOTCORR"]
        temp = data["properties"]["parameter"]["T2M"]
    except requests.exceptions.RequestException as e:
        print(f"NASA API failed: {e}. Using fallback data.")
        dates = pd.date_range(start=start_date, end=end_date)
        rain = {d.strftime("%Y%m%d"): float(np.random.uniform(0, 5)) for d in dates}
        temp = {d.strftime("%Y%m%d"): float(np.random.uniform(15, 35)) for d in dates}

    # =========================
    # BUILD DATAFRAME
    # =========================
    df = pd.DataFrame({
        "date": list(rain.keys()),
        "rainfall_nasa": list(rain.values()),
        "temp_nasa": list(temp.values())
    })

    # =========================
    # DATE CONVERSION
    # =========================
    df["date"] = pd.to_datetime(
        df["date"],
        format="%Y%m%d"
    )

    # =========================
    # FORCE NUMERIC TYPES
    # =========================
    df["rainfall_nasa"] = pd.to_numeric(
        df["rainfall_nasa"],
        errors="coerce"
    )

    df["temp_nasa"] = pd.to_numeric(
        df["temp_nasa"],
        errors="coerce"
    )

    # =========================
    # CLEAN RAINFALL
    # =========================
    df["rainfall_nasa"] = (
        df["rainfall_nasa"]
        .replace(-999, np.nan)
        .fillna(0)
    )

    # =========================
    # CLEAN TEMPERATURE
    # =========================
    df["temp_nasa"] = (
        df["temp_nasa"]
        .replace(-999, np.nan)
        .astype(float)
        .interpolate(method="linear")
        .ffill()
        .bfill()
    )

    # =========================
    # DEBUG
    # =========================
    print("\nNASA DATA TYPES")
    print(df.dtypes)

    print("\nNASA SAMPLE")
    print(df.head())

    print("\nMissing Values")
    print(df.isna().sum())

    # =========================
    # SAVE
    # =========================
    output_file = "data/nasa_latest.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(f"\n✔ NASA data saved to {output_file}")
    print(f"Rows: {len(df)}")

    return df


if __name__ == "__main__":
    fetch_nasa()