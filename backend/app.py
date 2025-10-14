from flask import Flask, jsonify, redirect, url_for
from models import db
from routes import register_routes
from flask_cors import CORS

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
