from pathlib import Path
import pandas as pd
import tensorflow as tf
import joblib
import shap
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import DB_queries as db
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.metrics import make_scorer, mean_absolute_error


conn = db.get_conn()
df = db.labeled_seasons()
midfielder_positions = {"MF", "MF/DF", "MF/FW"}
df = df[df["position"].isin(midfielder_positions)].copy()
drop_cols = ["id", "player_id", "year_code","born_year", "nation", "position", "club",
            "matches_played",
            "matches_started",]

target_col = "valuation_amount"

# Convert counting stats into per-minute rates so the attacker model trains
# on comparable production regardless of total playing time.
rate_exclusions = set(drop_cols + [
    target_col,
    "age",
    "born_year"
])
minutes = df["minutes_played"].replace(0, np.nan)
numeric_cols = df.select_dtypes(include=[np.number]).columns
rate_cols = [
    col for col in numeric_cols
    if col not in rate_exclusions and not col.endswith("_pct")
]
df[rate_cols] = df[rate_cols].div(minutes, axis=0)

feature_cols = df.drop(columns=drop_cols + [target_col], errors="ignore").columns.tolist()
features = feature_cols

df = df.replace([np.inf, -np.inf], np.nan).dropna()
df = df[df[target_col] != 0]

y = df[target_col].values
X = df[feature_cols].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='mae',
    metrics=[
        tf.keras.metrics.MeanAbsoluteError(name='mae'),
        tf.keras.metrics.RootMeanSquaredError(name='rmse')
    ]
)

lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_mae',     # what to watch (can also be 'val_mae')
    factor=0.5,             # how much to reduce the LR (new_lr = lr * factor)
    patience=5,             # epochs with no improvement before reducing
    min_lr=1e-6,            # lower bound for learning rate
    verbose=1               # print updates
)

model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=200,
    batch_size=32,
    callbacks=[lr_scheduler],
    verbose=1
)

loss, mae, rmse = model.evaluate(X_test, y_test)
print(f"Test MAE: {mae:.3f}")

models_dir = Path(__file__).resolve().parents[1] / "models"
models_dir.mkdir(parents=True, exist_ok=True)

model.save(models_dir / "regression_model_midfielders.keras")
joblib.dump(scaler, models_dir / "scaler_midfielders.pkl")


## -------- FEATURE IMPORTANCE -------

## ---- Permutation importance -----
# scorer = make_scorer(mean_absolute_error, greater_is_better=False)

# pi = permutation_importance(
#     model,        
#     X_test,       
#     y_test,
#     scoring=scorer,
#     n_repeats=10,
#     random_state=42
# )

# importances = np.abs(pi.importances_mean)
# importance_df = pd.DataFrame({
#     "feature": features,
#     "importance": importances
# }).sort_values("importance", ascending=False)

# print("Permutation Importance")
# print(importance_df.head(4))

# ## ----- SHAP values -------

# rng = np.random.default_rng(42)
# bg_size = 250
# bg_idx = rng.choice(X_train.shape[0], size=bg_size, replace=False)
# X_bg = X_train[bg_idx]

# explainer = shap.Explainer(model, X_bg)
# sv = explainer(X_test[:200])

# global_imp = np.mean(np.abs(sv.values), axis=0)
# shap_global_df = (
#     pd.DataFrame({"feature": features, "mean_abs_shap": global_imp})
#       .sort_values("mean_abs_shap", ascending=False)
#       .reset_index(drop=True)
# )
# print("{\nSHAP importance")
# print(shap_global_df.head(4))


# ## --------- PLOTS -------------

# top_perm = importance_df.sort_values("importance", ascending=False).head(6)
# top_shap = shap_global_df.sort_values("mean_abs_shap", ascending=False).head(6)
# fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# axes[0].bar(top_perm["feature"], top_perm["importance"])
# axes[0].set_title("Permutation Importance")
# axes[0].set_xticklabels(top_perm["feature"], rotation=45, ha='right')
# axes[0].set_ylabel("Importance (MAE increase)")

# axes[1].bar(top_shap["feature"], top_shap["mean_abs_shap"])
# axes[1].set_title("SHAP")
# axes[1].set_xticklabels(top_shap["feature"], rotation=45, ha='right')
# axes[1].set_ylabel("Mean |SHAP|")

# plt.tight_layout()
# plt.show()
