import pandas as pd
import tensorflow as tf
import joblib
import shap
import numpy as np
import DB_queries as db
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, r2_score
import shap

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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

# Model
model = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# remove comment to save model
#model.save_model("models/XGBoost_model.json")

# --------- FEATURE IMPORTANCE -----------

# XGBoost built in feature importance
gain = model.get_booster().get_score(importance_type="gain")  # gain: average improvement in model loss
importance_df = (
    pd.DataFrame({"feature": list(gain.keys()), "gain": list(gain.values())})
      .set_index("feature")
      .reindex(features)           
      .fillna(0)
      .sort_values("gain", ascending=False)
      .reset_index()
)

print("\nGlobal Feature Importance (XGBoost gain):")
print(importance_df.head(15).to_string(index=False))


# Global SHAP feature importance
explainer = shap.Explainer(model.predict, X_train) 
sv = explainer(X_test)                            

mean_abs_shap = np.abs(sv.values).mean(axis=0)
importance_df = (
    pd.DataFrame({"feature": features, "mean_abs_shap": mean_abs_shap})
      .sort_values("mean_abs_shap", ascending=False)
)

print("\nGlobal Feature Importance (mean |SHAP|):")
print(importance_df.head(15).to_string(index=False))