from flask import Blueprint, jsonify, request
from models import db, Player, PlayerSeason, PlayerValuation

players_bp = Blueprint('players', __name__, url_prefix='/api/players')


# ------------------------------
# GET all players
# ------------------------------
@players_bp.route('/', methods=['GET'])
def get_players():
    players = Player.query.all()
    data = [serialize_player(p) for p in players]
    return jsonify(data)


# ------------------------------
# GET specific player by ID
# ------------------------------
@players_bp.route('/<int:player_id>', methods=['GET'])
def get_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(serialize_player(player))


# ------------------------------
# POST: add a player
# ------------------------------
@players_bp.route('/add', methods=['POST'])
def add_player():
    data = request.json
    player = Player(
        name=data.get("name"),
        nationality=data.get("nationality"),
        birth_year=data.get("birth_year"),
        transfermarkt_player_id=data.get("transfermarkt_player_id")
    )
    db.session.add(player)
    db.session.commit()
    return jsonify({"message": "Player added successfully", "player_id": player.id})


# ------------------------------
# POST: add a player season
# ------------------------------
@players_bp.route('/add_season', methods=['POST'])
def add_season():
    data = request.json
    player_id = data.get("player_id")
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    season = PlayerSeason(
        player_id=player_id,
        year_code=data.get("year_code"),
        age=data.get("age"),
        position=data.get("position"),
        club=data.get("club"),
        matches_played=data.get("matches_played"),
        matches_started=data.get("matches_started"),
        minutes_played=data.get("minutes_played"),
        goals_scored=data.get("goals_scored"),
        assists_made=data.get("assists_made"),
        goals_plus_assists=data.get("goals_plus_assists"),
        goals_excluding_penalties=data.get("goals_excluding_penalties"),
        penalty_goals=data.get("penalty_goals"),
        penalty_attempts=data.get("penalty_attempts"),
        yellow_cards=data.get("yellow_cards"),
        red_cards=data.get("red_cards"),
        expected_goals=data.get("expected_goals"),
        non_penalty_expected_goals=data.get("non_penalty_expected_goals"),
        expected_assists=data.get("expected_assists"),
        combined_non_penalty_expected_goal_contributions=data.get("combined_non_penalty_expected_goal_contributions"),
        progressive_carries=data.get("progressive_carries"),
        progressive_passes=data.get("progressive_passes"),
        progressive_receptions=data.get("progressive_receptions")
    )
    db.session.add(season)
    db.session.commit()

    return jsonify({"message": "Season added successfully", "season_id": season.id})


# ------------------------------
# POST: add a player valuation
# ------------------------------
@players_bp.route('/add_valuation', methods=['POST'])
def add_valuation():
    data = request.json
    player_id = data.get("player_id")
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    valuation = PlayerValuation(
        player_id=player_id,
        date=data.get("date"),  # Expecting 'YYYY-MM-DD'
        amount=data.get("amount")
    )
    db.session.add(valuation)
    db.session.commit()

    return jsonify({"message": "Valuation added successfully", "valuation_id": valuation.id})


# ------------------------------
# Helper: serialize player with nested data
# ------------------------------
def serialize_player(p: Player):
    return {
        "id": p.id,
        "name": p.name,
        "nationality": p.nationality,
        "birth_year": p.birth_year,
        "transfermarkt_player_id": p.transfermarkt_player_id,
        "valuations": [
            {
                "id": v.id,
                "date": v.date.isoformat() if v.date else None,
                "amount": v.amount
            } for v in p.valuations
        ],
        "seasons": [
            {
                "id": s.id,
                "year_code": s.year_code,
                "age": s.age,
                "position": s.position,
                "club": s.club,
                "matches_played": s.matches_played,
                "matches_started": s.matches_started,
                "minutes_played": s.minutes_played,
                "goals_scored": s.goals_scored,
                "assists_made": s.assists_made,
                "goals_plus_assists": s.goals_plus_assists,
                "goals_excluding_penalties": s.goals_excluding_penalties,
                "penalty_goals": s.penalty_goals,
                "penalty_attempts": s.penalty_attempts,
                "yellow_cards": s.yellow_cards,
                "red_cards": s.red_cards,
                "expected_goals": s.expected_goals,
                "non_penalty_expected_goals": s.non_penalty_expected_goals,
                "expected_assists": s.expected_assists,
                "combined_non_penalty_expected_goal_contributions": s.combined_non_penalty_expected_goal_contributions,
                "progressive_carries": s.progressive_carries,
                "progressive_passes": s.progressive_passes,
                "progressive_receptions": s.progressive_receptions,
            } for s in p.seasons
        ]
    }
