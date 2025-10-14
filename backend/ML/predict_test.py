import pandas as pd
import tensorflow as tf
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

file_path = "../FBref_data/stats_standard_2025.csv"
df = pd.read_csv(file_path)

# only include numerical features
df = df.select_dtypes(include=['number'])

# drop row with a missing value or inf
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

X = df.drop("Per 90 Minutes npxG+xAG", axis=1).values

scaler = joblib.load("models/scaler.pkl")
model = tf.keras.models.load_model("models/regression_model.keras")

x = X[0].reshape(1, -1) # 2D
x = scaler.transform(x)
pred = model.predict(x)
print("Single prediction:", float(pred[0, 0]))