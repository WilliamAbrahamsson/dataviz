import pandas as pd
import tensorflow as tf
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

file_path = "../FBref_data/stats_standard_2025.csv"
df = pd.read_csv(file_path)

print(df.head())

# only include numerical features
df = df.select_dtypes(include=['number'])

# drop row with a missing value or inf
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.dropna()

X = df.drop("Per 90 Minutes npxG+xAG", axis=1).values
y = df["Per 90 Minutes npxG+xAG"].values

print(X[0])
print(y[0])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=32)

loss, mae = model.evaluate(X_test, y_test)
print(f"Test MAE: {mae:.3f}")

model.save("models/regression_model.keras")
joblib.dump(scaler, "models/scaler.pkl")