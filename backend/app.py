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
