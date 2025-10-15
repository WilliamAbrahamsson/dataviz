import pandas as pd
import tensorflow as tf
import numpy as np
import joblib
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

file_path = "../FBref_data/stats_standard_2025.csv"
df = pd.read_csv(file_path)

# only include numerical features
df = df.select_dtypes(include=['number'])

# drop row with a missing value or inf
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

TARGET = "Per 90 Minutes npxG+xAG"
features = df.drop(columns=[TARGET]).columns
X = df.drop(TARGET, axis=1).values

scaler = joblib.load("models/scaler.pkl")
model = tf.keras.models.load_model("models/regression_model.keras")

x = X[0].reshape(1, -1) # 2D
x = scaler.transform(x)
pred = model.predict(x)
print("Single prediction:", float(pred[0, 0]))

# Build a background set (needed by SHAP for reference baseline)
rng = np.random.default_rng(42)
bg_idx = rng.choice(X.shape[0], size=200, replace=False)
X_bg = scaler.transform(X[bg_idx])


explainer = shap.Explainer(model, X_bg)
sv = explainer(x_scaled)  # explain THIS one prediction

# Convert to readable dataframe
local_df = pd.DataFrame({
    "feature": features,
    "feature_value (scaled)": x_scaled.flatten(),
    "shap_value": sv.values.flatten()
}).sort_values("shap_value", key=np.abs, ascending=False)

print("\n🔍 Top contributing features for THIS prediction:")
print(local_df.head(10))