import pandas as pd


def build_monthly_baselines():

    print("Loading historical dataset...")

    df = pd.read_csv(
        "data/master_dataset_with_edge_nans.csv"
    )

    # =====================================
    # DATE HANDLING
    # =====================================

    df["date"] = pd.to_datetime(df["date"])

    # If month column doesn't exist,
    # regenerate it from date

    if "month" not in df.columns:
        df["month"] = df["date"].dt.month

    # =====================================
    # MONTHLY CLIMATE BASELINES
    # =====================================

    monthly = (

        df.groupby("month")

        .agg({

            "rainfall": ["mean", "std"],

            "rainfall_nasa": ["mean", "std"],

            "rainfall_openmeteo": ["mean", "std"],

            "temp_mean": ["mean", "std"],

            "ndvi": ["mean", "std"]

        })

        .reset_index()

    )

    # =====================================
    # FLATTEN COLUMN NAMES
    # =====================================

    monthly.columns = [

        "month",

        "rainfall_avg",
        "rainfall_std",

        "rainfall_nasa_avg",
        "rainfall_nasa_std",

        "rainfall_openmeteo_avg",
        "rainfall_openmeteo_std",

        "temp_avg",
        "temp_std",

        "ndvi_avg",
        "ndvi_std"

    ]

    # =====================================
    # ROUND VALUES
    # =====================================

    monthly = monthly.round(3)

    # =====================================
    # SAVE OUTPUT
    # =====================================

    monthly.to_csv(
        "data/monthly_baselines.csv",
        index=False
    )

    print("\nMonthly baselines created successfully.\n")

    print(monthly)

    print(
        "\nSaved to: data/monthly_baselines.csv"
    )

    return monthly


if __name__ == "__main__":

    build_monthly_baselines()