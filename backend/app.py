from flask import Flask, jsonify, redirect, url_for, request
from models import db
from routes import register_routes
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
register_routes(app)


@app.route('/')
def home():
    # Redirect to the players list endpoint
    return redirect(url_for('players.get_players'))


@app.route('/api/estimate', methods=['POST', 'OPTIONS'])
def estimate():
    if request.method == 'OPTIONS':
        return ('', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
        })

    new_val = predict(request.get_json(silent=True) or {})

    response = jsonify({'estimated_value': new_val})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def predict(payload):
    featureValues = payload.get('featureValues') or {}

    df = pd.json_normalize(featureValues) if featureValues else pd.DataFrame()
    pos = df["position"].values
    pos = str(pos[0])

    if pos in {"FW", "FW/MF"}:
        print("attackers")
        drop_cols = ["position", "club",
                    "matches_played",
                    "matches_started",
                    "tackles",
                    "tackles_won",
                    "tackles_def_3rd",
                    "tackles_mid_3rd", 
                    "challenges_tackles",
                    "challenges_attempted",
                    "challenges_tackle_pct",
                    "challenges_lost",
                    "blocks",
                    "blocks_shots",
                    "blocks_passes",
                    "interceptions",
                    "tackles_plus_interceptions",
                    "clearances",
                    "errors_leading_to_shot"]

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        df = df.replace(r'^\s*$', 0, regex=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        # Drop only the columns that actually exist in the frame.
        cols_to_drop = [col for col in drop_cols if col in df.columns]
        X = df.drop(columns=cols_to_drop)
        X = X.values

        print(X)
        scaler = joblib.load("ML/models/scaler_attackers.pkl")
        model = tf.keras.models.load_model("ML/models/regression_model_attackers.keras")

        x = X[0].reshape(1, -1) # 2D
        x_scaled = scaler.transform(x)
        pred = model.predict(x_scaled)
        print(float(np.asarray(pred)))
        return float(np.asarray(pred))
    
    elif pos in {"MF", "MF/DF", "MF/FW"}:
        drop_cols = ["position", "club",
                    "matches_played",
                    "matches_started"]

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        df = df.replace(r'^\s*$', 0, regex=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        # Drop only the columns that actually exist in the frame.
        cols_to_drop = [col for col in drop_cols if col in df.columns]
        X = df.drop(columns=cols_to_drop)
        X = X.values

        print(X)
        scaler = joblib.load("ML/models/scaler_midfielders.pkl")
        model = tf.keras.models.load_model("ML/models/regression_model_midfielders.keras")

        x = X[0].reshape(1, -1) # 2D
        x_scaled = scaler.transform(x)
        pred = model.predict(x_scaled)
        print(float(np.asarray(pred)))

        return float(np.asarray(pred))
    
    elif pos in {"DF", "DF/MF"}:
        drop_cols = ["position", "club",
            "matches_played",
            "matches_started",
            "goals_scored",
            "goal_plus_assists",
            "penalty_goals",
            "penalty_attempts",
            "expected_goals",
            "non_penalty_expected_goals",
            "combined_non_penalty_expected_goal_contributions"]

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        df = df.replace(r'^\s*$', 0, regex=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        # Drop only the columns that actually exist in the frame.
        cols_to_drop = [col for col in drop_cols if col in df.columns]
        X = df.drop(columns=cols_to_drop)
        X = X.values

        print(X)
        scaler = joblib.load("ML/models/scaler_defenders.pkl")
        model = tf.keras.models.load_model("ML/models/regression_model_defenders.keras")

        x = X[0].reshape(1, -1) # 2D
        x_scaled = scaler.transform(x)
        pred = model.predict(x_scaled)
        print(float(np.asarray(pred)))
        return float(np.asarray(pred))
    
    else:
    
        drop_cols = ["position", "club"]

        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        df = df.replace(r'^\s*$', 0, regex=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        # Drop only the columns that actually exist in the frame.
        cols_to_drop = [col for col in drop_cols if col in df.columns]
        X = df.drop(columns=cols_to_drop)
        X = X.values

        print(X)
        scaler = joblib.load("ML/models/scaler.pkl")
        model = tf.keras.models.load_model("ML/models/regression_model.keras")

        x = X[0].reshape(1, -1) # 2D
        x_scaled = scaler.transform(x)
        pred = model.predict(x_scaled)
        return float(np.asarray(pred))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
