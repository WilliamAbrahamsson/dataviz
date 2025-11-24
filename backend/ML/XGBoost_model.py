import pandas as pd
import tensorflow as tf
import joblib
import shap
import numpy as np
import DB_queries as db
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import shap

conn = db.get_conn()
df = db.labeled_seasons()
drop_cols = ["id", "player_id", "year_code", "nation", "position", "club", "born_year"]
target_col = "valuation_amount"
features = [c for c in df.columns if c not in drop_cols + [target_col]]

df = df.replace([np.inf, -np.inf], np.nan).dropna()
df = df[df[target_col] != 0]

y = df[target_col].values
X = df.drop(columns=[target_col] + drop_cols).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

# Model
model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.03,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,     
    gamma=0.1,              
    reg_lambda=1.0,         
    reg_alpha=0.0,          
    random_state=42,
    tree_method="hist"      
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print("MAE:", mae)

# remove comment to save model
#model.save_model("models/XGBoost_model.json")

exit(1)
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