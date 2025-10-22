import pandas as pd
import numpy as np
import joblib
import shap
import xgboost as xgb


file_path = "../old/FBref_data/stats_standard_2025.csv"
df = pd.read_csv(file_path)

# only include numerical features
df = df.select_dtypes(include=['number'])

# drop row with a missing value or inf
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

TARGET = "Per 90 Minutes npxG+xAG"
features = df.drop(columns=[TARGET]).columns
X = df.drop(TARGET, axis=1).values

model = xgb.XGBRegressor()
model.load_model("models/XGBoost_model.json")

# -------- SHAP: Single prediction importance --------

X_df = pd.DataFrame(df.drop(columns=[TARGET]), columns=features)
x_df = X_df.iloc[[0]]

# Reference sample
rng = np.random.default_rng(42)
bg_size = 200
bg_idx = rng.choice(len(X_df), size=bg_size, replace=False)
X_bg = X_df.iloc[bg_idx]

explainer = shap.Explainer(model.predict, X_bg)
sv = explainer(x_df)

local_df = pd.DataFrame({
    "feature": x_df.columns,
    "feature_value": x_df.iloc[0].values,
    "shap_value": sv.values.flatten()
}).sort_values("shap_value", key=np.abs, ascending=False)

print("\nTop contributing features for THIS prediction:")
print(local_df.head(10).to_string(index=False))