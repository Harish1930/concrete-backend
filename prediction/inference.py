import pandas as pd
import joblib
import numpy as np
import os

# -----------------------------
# LOAD MODELS
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

strength_model = joblib.load(
    os.path.join(BASE_DIR, "models", "strength_model.pkl")
)

anomaly_model = joblib.load(
    os.path.join(BASE_DIR, "models", "anomaly_model.pkl")
)

TOLERANCE = 3.0  # ±3 MPa


# -----------------------------
# REFERENCE MIX FUNCTION
# -----------------------------
def get_reference_mix(target_strength, tolerance=3):

    ref_path = os.path.join(BASE_DIR, "models", "reference_data.csv")
    ref_df = pd.read_csv(ref_path)

    lower = target_strength - tolerance
    upper = target_strength + tolerance

    # Step 1: strict match
    candidates = ref_df[
        (ref_df["Strength_28 (Mpa)"] >= lower) &
        (ref_df["Strength_28 (Mpa)"] <= upper)
    ].copy()

    # Step 2: fallback
    if candidates.empty:
        ref_df["diff"] = abs(ref_df["Strength_28 (Mpa)"] - target_strength)
        min_diff = ref_df["diff"].min()
        candidates = ref_df[ref_df["diff"] == min_diff]

    # Step 3: minimum cement
    best_mix = candidates.sort_values(
        by="Cement (Kg/m^3)"
    ).iloc[0]

    return best_mix.to_dict()


# -----------------------------
# MAIN PREDICTION FUNCTION (API READY)
# -----------------------------
def predict_strength(data: dict):

    try:
        # Map API keys to training column names
        key_mapping = {
            "cement": "Cement (Kg/m^3)",
            "fa": "FA (Kg/m^3)",
            "ca": "CA (Kg/m^3)",
            "water": "Water (Kg/m^3)",
            "wc_ratio": "W/C ratio",
            "strength_7": "Strength_7 (Mpa)"
        }

        # FIXED FEATURE ORDER (CRITICAL)
        feature_order = [
            "Cement (Kg/m^3)",
            "FA (Kg/m^3)",
            "CA (Kg/m^3)",
            "Water (Kg/m^3)",
            "W/C ratio",
            "Strength_7 (Mpa)"
        ]

        # Validate input
        for api_key, train_key in key_mapping.items():
            if api_key not in data:
                raise ValueError(f"Missing input: {api_key}")

        X = np.array([[data[api_key] for api_key in key_mapping.keys()]])

        predicted_28 = float(strength_model.predict(X)[0])

        target_strength = data.get("target_strength")
        if target_strength is None:
            target_strength = predicted_28

        # QC STATUS
        if predicted_28 >= target_strength + TOLERANCE:
            qc_status = "Overdesigned"
        elif predicted_28 >= target_strength - TOLERANCE:
            qc_status = "Safe"
        else:
            qc_status = "Unsafe"

        # ABNORMALITY CHECK
        expected_7 = predicted_28 * 0.65
        residual = data["strength_7"] - expected_7

        abnormal = anomaly_model.predict([[residual]])[0]
        abnormality = "Abnormal" if abnormal == -1 else "Normal"

        result = {
            "predicted_strength_28": round(predicted_28, 2),
            "qc_status": qc_status,
            "abnormality": abnormality
        }

        # Add recommendation if abnormal
        if abnormality == "Abnormal":
            result["recommended_mix"] = get_reference_mix(target_strength)

        return result

    except Exception as e:
        return {"error": str(e)}