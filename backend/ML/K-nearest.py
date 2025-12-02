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
from sklearn.neighbors import NearestNeighbors

conn = db.get_conn()
df = db.labeled_seasons()
defender_positions = {"FW"}
df = df[df["position"].isin(defender_positions)].copy()
feature_cols = [
    "minutes_played",
    "goals_scored",
    "passes_into_penalty_area",
    "age",
    "goals_plus_assists",
    "progressive_receptions",
    "pass_progressive_distance",
    "progressive_carries",
    "pass_completion_pct",
    "crosses_into_pa",
    "medium_passes_completed",
    "pass_total_distance",
    "passes_completed",
    "tackles_mid_3rd",
    "passes_into_final_third",
    "long_passes_completed",
    "tackles_won",
    "challenges_tackles",
    "assists_made"
]

# Clean
df = df.replace([np.inf, -np.inf], np.nan).dropna()

players_df = df.reset_index(drop=True)
X = df[feature_cols].values

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Nearest Neighbors model
nn_model = NearestNeighbors(
    n_neighbors=6,
    metric="minkowski",
    p=2
)
nn_model.fit(X_scaled)

joblib.dump(scaler, "models/player_similarity_scaler.pkl")
joblib.dump(nn_model, "models/player_similarity_knn.pkl")
joblib.dump(players_df, "models/player_similarity_players.pkl") 
joblib.dump(feature_cols, "models/player_similarity_features.pkl")

testrow = df.iloc[10]                       
test_features = testrow[feature_cols]      

# Rescale
x = np.array(test_features).reshape(1, -1)
x_scaled = scaler.transform(x)

# Find nearest neighbors
distances, indices = nn_model.kneighbors(x_scaled, n_neighbors=6)

# Get players
similar_players = df.iloc[indices[0]].copy()
similar_players["distance"] = distances[0]

print(similar_players)