import pandas as pd
import numpy as np
import joblib
import shap
import xgboost as xgb
import DB_queries as db

conn = db.get_conn()
df = db.labeled_seasons()

features = ["age", "minutes_played", "goals_scored", "assists_made", "goals_excluding_penalties", "progressive_carries", "progressive_passes", "passes_completed", "key_passes", "tackles", "blocks"]
use_columns = features.copy()
use_columns.append("valuation_amount")

df = df[use_columns]
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

y = df["valuation_amount"]
X = df.drop("valuation_amount", axis=1)

model = xgb.XGBRegressor()
model.load_model("models/XGBoost_model.json")

# -------- SHAP: Single prediction importance --------

x_df = X.iloc[[0]]

# Reference sample
rng = np.random.default_rng(42)
bg_size = 200
bg_idx = rng.choice(len(X), size=bg_size, replace=False)
X_bg = X.iloc[bg_idx]

explainer = shap.Explainer(model.predict, X_bg)
sv = explainer(x_df)

local_df = pd.DataFrame({
    "feature": x_df.columns,
    "feature_value": x_df.iloc[0].values,
    "shap_value": sv.values.flatten()
}).sort_values("shap_value", key=np.abs, ascending=False)

print("\nTop contributing features for THIS prediction:")
print(local_df.head(10).to_string(index=False))