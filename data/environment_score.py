import pandas as pd


def environmental_score():

    try:

        # =====================================
        # LOAD MONTHLY BASELINES
        # =====================================

        baselines = pd.read_csv(
            "data/monthly_baselines.csv"
        )

        # =====================================
        # LOAD CURRENT INFERENCE DATA
        # =====================================

        current = pd.read_csv(
            "data/latest_inference.csv"
        )

        current = current.iloc[-1]

        # =====================================
        # CURRENT MONTH
        # =====================================

        month = int(current["month"])

        baseline = baselines[
            baselines["month"] == month
        ].iloc[0]

        # =====================================
        # CURRENT CONDITIONS
        # =====================================

        current_rain = float(
            current["rainfall_30d_avg"]
        )

        current_ndvi = float(
            current["ndvi"]
        )

        current_temp = float(
            current["temp_mean"]
        )

        # =====================================
        # BASELINE CONDITIONS
        # =====================================

        baseline_rain = float(
            baseline["rainfall_avg"]
        )

        baseline_ndvi = float(
            baseline["ndvi_avg"]
        )

        baseline_temp = float(
            baseline["temp_avg"]
        )

        # =====================================
        # RAINFALL RATIO
        # =====================================

        if baseline_rain > 0:

            rain_ratio = (
                current_rain /
                baseline_rain
            )

        else:

            rain_ratio = 1.0

        # =====================================
        # NDVI RATIO
        # =====================================

        if baseline_ndvi > 0:

            ndvi_ratio = (
                current_ndvi /
                baseline_ndvi
            )

        else:

            ndvi_ratio = 1.0

        # =====================================
        # TEMPERATURE ANOMALY
        # =====================================

        temp_anomaly = (
            current_temp -
            baseline_temp
        )

        # =====================================
        # RAINFALL RISK
        # DRY-SEASON AWARE
        # =====================================

        if baseline_rain < 1:

            # Naturally dry month: risk is lower but dynamically responds to anomalies
            if rain_ratio >= 0.80:

                rainfall_risk = 0.1  # Better moisture than normal dry season

            elif rain_ratio >= 0.30:

                rainfall_risk = 0.2  # Normal dry season conditions

            else:

                rainfall_risk = 0.4  # Unusually dry/drought conditions even for dry season

        else:

            if rain_ratio >= 0.90:

                rainfall_risk = 0.0

            elif rain_ratio >= 0.70:

                rainfall_risk = 0.3

            elif rain_ratio >= 0.50:

                rainfall_risk = 0.6

            else:

                rainfall_risk = 1.0

        # =====================================
        # NDVI RISK
        # =====================================

        if ndvi_ratio >= 0.90:

            ndvi_risk = 0.0

        elif ndvi_ratio >= 0.70:

            ndvi_risk = 0.3

        elif ndvi_ratio >= 0.50:

            ndvi_risk = 0.6

        else:

            ndvi_risk = 1.0

        # =====================================
        # TEMPERATURE RISK
        # =====================================

        if temp_anomaly <= 1:

            temp_risk = 0.0

        elif temp_anomaly <= 3:

            temp_risk = 0.5

        else:

            temp_risk = 1.0

        # =====================================
        # FINAL ENVIRONMENTAL SCORE
        # =====================================

        env_score = (

            0.45 * rainfall_risk +

            0.35 * ndvi_risk +

            0.20 * temp_risk

        )

        # =====================================
        # LABEL
        # =====================================

        if env_score < 0.30:

            env_label = "LOW"

        elif env_score < 0.60:

            env_label = "MODERATE"

        else:

            env_label = "HIGH"

        result = {

            "month": month,

            "baseline_rain":
                round(baseline_rain, 1),

            "environmental_score":
                round(env_score, 3),

            "environmental_label":
                env_label,

            "rainfall_risk":
                round(rainfall_risk, 3),

            "ndvi_risk":
                round(ndvi_risk, 3),

            "temp_risk":
                round(temp_risk, 3),

            "rain_ratio":
                round(rain_ratio, 3),

            "ndvi_ratio":
                round(ndvi_ratio, 3),

            "temp_anomaly":
                round(temp_anomaly, 3)

        }

        print("\nEnvironmental Score\n")
        print(result)

        return result

    except Exception as e:

        print(
            f"Environmental Score Error: {e}"
        )

        return {

            "status": "error",

            "message": str(e)

        }


if __name__ == "__main__":

    environmental_score()