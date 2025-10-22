from __future__ import annotations

from datetime import date
from flask_sqlalchemy import SQLAlchemy

# Flask-SQLAlchemy instance used across the app
db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))               # VARCHAR(100)
    birth_year = db.Column(db.Integer)             # INTEGER
    transfermarkt_player_id = db.Column(db.Integer, unique=True)  # INTEGER, UNIQUE
    short_name = db.Column(db.String(100))         # VARCHAR(100)
    nationality_iso2 = db.Column(db.Text)          # TEXT
    nationality_fifa = db.Column(db.Text)          # TEXT

    # Relationships
    seasons = db.relationship(
        "PlayerSeason",
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="select",
    )
    valuations = db.relationship(
        "PlayerValuation",
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="select",
    )


class PlayerSeason(db.Model):
    __tablename__ = "player_season"

    id = db.Column(db.Integer, primary_key=True)   # INTEGER PRIMARY KEY
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("player.id", ondelete="CASCADE"),
        nullable=False,                             # INTEGER NOT NULL
    )
    year_code = db.Column(db.Text, nullable=False) # TEXT NOT NULL

    nation = db.Column(db.Text)                    # TEXT
    position = db.Column(db.Text)                  # TEXT
    club = db.Column(db.Text)                      # TEXT
    age = db.Column(db.REAL)                       # REAL
    born_year = db.Column(db.REAL)                 # REAL
    matches_played = db.Column(db.REAL)            # REAL
    matches_started = db.Column(db.REAL)           # REAL
    minutes_played = db.Column(db.REAL)            # REAL
    ninety_min_equivalents = db.Column(db.REAL)    # REAL
    goals_scored = db.Column(db.REAL)              # REAL
    assists_made = db.Column(db.REAL)              # REAL
    goals_plus_assists = db.Column(db.REAL)        # REAL
    goals_excluding_penalties = db.Column(db.REAL) # REAL
    penalty_goals = db.Column(db.REAL)             # REAL
    penalty_attempts = db.Column(db.REAL)          # REAL
    yellow_cards = db.Column(db.REAL)              # REAL
    red_cards = db.Column(db.REAL)                 # REAL
    expected_goals = db.Column(db.REAL)            # REAL
    non_penalty_expected_goals = db.Column(db.REAL)  # REAL
    expected_assists = db.Column(db.REAL)          # REAL
    combined_non_penalty_expected_goal_contributions = db.Column(db.REAL)  # REAL
    progressive_carries = db.Column(db.REAL)       # REAL
    progressive_passes = db.Column(db.REAL)        # REAL
    progressive_receptions = db.Column(db.REAL)    # REAL
    passes_completed = db.Column(db.REAL)          # REAL
    passes_attempted = db.Column(db.REAL)          # REAL
    pass_completion_pct = db.Column(db.REAL)       # REAL
    pass_total_distance = db.Column(db.REAL)       # REAL
    pass_progressive_distance = db.Column(db.REAL) # REAL
    short_passes_completed = db.Column(db.REAL)    # REAL
    short_passes_attempted = db.Column(db.REAL)    # REAL
    short_passes_completion_pct = db.Column(db.REAL) # REAL
    medium_passes_completed = db.Column(db.REAL)   # REAL
    medium_passes_attempted = db.Column(db.REAL)   # REAL
    medium_passes_completion_pct = db.Column(db.REAL) # REAL
    long_passes_completed = db.Column(db.REAL)     # REAL
    long_passes_attempted = db.Column(db.REAL)     # REAL
    long_passes_completion_pct = db.Column(db.REAL) # REAL
    key_passes = db.Column(db.REAL)                # REAL
    passes_into_final_third = db.Column(db.REAL)   # REAL
    passes_into_penalty_area = db.Column(db.REAL)  # REAL
    crosses_into_pa = db.Column(db.REAL)           # REAL
    tackles = db.Column(db.REAL)                   # REAL
    tackles_won = db.Column(db.REAL)               # REAL
    tackles_def_3rd = db.Column(db.REAL)           # REAL
    tackles_mid_3rd = db.Column(db.REAL)           # REAL
    tackles_att_3rd = db.Column(db.REAL)           # REAL
    challenges_tackles = db.Column(db.REAL)        # REAL
    challenges_attempted = db.Column(db.REAL)      # REAL
    challenges_tackle_pct = db.Column(db.REAL)     # REAL
    challenges_lost = db.Column(db.REAL)           # REAL
    blocks = db.Column(db.REAL)                    # REAL
    blocks_shots = db.Column(db.REAL)              # REAL
    blocks_passes = db.Column(db.REAL)             # REAL
    interceptions = db.Column(db.REAL)             # REAL
    tackles_plus_interceptions = db.Column(db.REAL) # REAL
    clearances = db.Column(db.REAL)                # REAL
    errors_leading_to_shot = db.Column(db.REAL)    # REAL

    __table_args__ = (db.UniqueConstraint("player_id", "year_code"),)

    player = db.relationship("Player", back_populates="seasons")


class PlayerValuation(db.Model):
    __tablename__ = "player_valuation"

    id = db.Column(db.Integer, primary_key=True)   # INTEGER PRIMARY KEY
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)  # INTEGER NOT NULL
    date = db.Column(db.Date)                      # DATE
    amount = db.Column(db.Float)                   # FLOAT (exactly as in your schema)

    player = db.relationship("Player", back_populates="valuations")
