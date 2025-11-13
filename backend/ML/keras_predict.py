import pandas as pd
import tensorflow as tf
import numpy as np
import joblib
import shap
import DB_queries as db
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

conn = db.get_conn()
df = db.labeled_seasons()

features = ["age", "minutes_played", "goals_scored", "assists_made", "goals_excluding_penalties", "progressive_carries", "progressive_passes", "passes_completed", "key_passes", "tackles", "blocks"]
use_columns = features.copy()
use_columns.append("valuation_amount")

df = df[use_columns]
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

y = df["valuation_amount"].values
X = df.drop("valuation_amount", axis=1).values

scaler = joblib.load("models/scaler.pkl")
model = tf.keras.models.load_model("models/regression_model.keras")

x = X[0].reshape(1, -1) # 2D
x_scaled = scaler.transform(x)
pred = model.predict(x_scaled)
print("Single prediction:", float(pred[0, 0]))


# -------- SHAP: Single prediction importance --------
# background set
rng = np.random.default_rng(42)
bg_size = 300 #The higher the better
bg_idx = rng.choice(X.shape[0], size=bg_size, replace=False)
X_bg_scaled = scaler.transform(X[bg_idx])

explainer = shap.Explainer(model, X_bg_scaled)

# Explain the prediction
shap_values = explainer(x_scaled)

local_df = pd.DataFrame({
    "feature": features,
    "feature_value (scaled)": x_scaled.flatten(),
    "shap_value": shap_values.values.flatten()
}).sort_values("shap_value", key=np.abs, ascending=False)

# higher |value| means more important
print("\nTop contributing features for the prediction:")
print(local_df.head(10).to_string(index=False))