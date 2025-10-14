from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite database in project root
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    transfermarkt_player_id = db.Column(db.Integer, unique=True, nullable=True)

    seasons = db.relationship('PlayerSeason', backref='player', lazy=True)
    valuations = db.relationship('PlayerValuation', backref='player', lazy=True)


class PlayerValuation(db.Model):
    __tablename__ = 'player_valuation'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    date = db.Column(db.Date, nullable=True)
    amount = db.Column(db.Float, nullable=True)


class PlayerSeason(db.Model):
    __tablename__ = 'player_season'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    year_code = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Float, nullable=True)
    position = db.Column(db.String(10), nullable=True)
    club = db.Column(db.String(100), nullable=True)

    matches_played = db.Column(db.Float, nullable=True)
    matches_started = db.Column(db.Float, nullable=True)
    minutes_played = db.Column(db.Float, nullable=True)

    goals_scored = db.Column(db.Float, nullable=True)
    assists_made = db.Column(db.Float, nullable=True)
    goals_plus_assists = db.Column(db.Float, nullable=True)
    goals_excluding_penalties = db.Column(db.Float, nullable=True)
    penalty_goals = db.Column(db.Float, nullable=True)
    penalty_attempts = db.Column(db.Float, nullable=True)
    yellow_cards = db.Column(db.Float, nullable=True)
    red_cards = db.Column(db.Float, nullable=True)

    expected_goals = db.Column(db.Float, nullable=True)
    non_penalty_expected_goals = db.Column(db.Float, nullable=True)
    expected_assists = db.Column(db.Float, nullable=True)
    combined_non_penalty_expected_goal_contributions = db.Column(db.Float, nullable=True)

    progressive_carries = db.Column(db.Float, nullable=True)
    progressive_passes = db.Column(db.Float, nullable=True)
    progressive_receptions = db.Column(db.Float, nullable=True)


# ------------------------------
# Create Tables
# ------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database and tables created successfully in mydatabase.db")
