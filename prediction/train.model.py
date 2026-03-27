import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os


# Load data
# Use the reference data
df = pd.read_csv(os.path.join("models", "reference_data.csv"))

# Fix typo safely
df.rename(columns={"Srength_28 (Mpa)": "Strength_28 (Mpa)"}, inplace=True)

# Drop serial number
df.drop(columns=["S.no"], inplace=True, errors="ignore")

# Remove missing values
required_cols = [
    "Cement (Kg/m^3)", "FA (Kg/m^3)", "CA (Kg/m^3)",
    "Water (Kg/m^3)", "W/C ratio",
    "Strength_7 (Mpa)", "Strength_28 (Mpa)"
]
df = df.dropna(subset=required_cols)

# Features & target
X = df[
    ["Cement (Kg/m^3)", "FA (Kg/m^3)", "CA (Kg/m^3)",
     "Water (Kg/m^3)", "W/C ratio", "Strength_7 (Mpa)"]
]
y = df["Strength_28 (Mpa)"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X.values, y.values, test_size=0.2, random_state=42
)

# Train model
strength_model = RandomForestRegressor(
    n_estimators=300, max_depth=10, random_state=42
)
strength_model.fit(X_train, y_train)

# Evaluation
y_pred = strength_model.predict(X_test)
print("R2 Score:", round(r2_score(y_test, y_pred), 3))
print("MAE (MPa):", round(mean_absolute_error(y_test, y_pred), 2))

# Abnormality model
residuals = y_train - strength_model.predict(X_train)
anomaly_model = IsolationForest(contamination=0.08, random_state=42)
anomaly_model.fit(residuals.reshape(-1, 1))

# Save models
os.makedirs("models", exist_ok=True)
joblib.dump(strength_model, "models/strength_model.pkl")
joblib.dump(anomaly_model, "models/anomaly_model.pkl")

print("Training completed & models saved.")
df.to_csv("models/reference_data.csv", index=False)