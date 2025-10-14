from flask import Blueprint, jsonify, request
from models import db, Player, PlayerSeason, PlayerValuation
from sqlalchemy.orm import joinedload

players_bp = Blueprint("players", __name__, url_prefix="/api/players")


@players_bp.route("/", methods=["GET"])
def get_players():
    name = request.args.get("name", type=str)
    club = request.args.get("club", type=str)
    year_code = request.args.get("year_code", type=str)

    query = Player.query.options(
        joinedload(Player.seasons),
        joinedload(Player.valuations)
    )

    # Apply dynamic filters
    if club or year_code:
        query = query.join(PlayerSeason)

        if club:
            query = query.filter(PlayerSeason.club.ilike(f"%{club}%"))

        if year_code:
            query = query.filter(PlayerSeason.year_code == year_code)

    if name:
        # Match partial player names (case-insensitive)
        query = query.filter(Player.name.ilike(f"%{name}%"))

    players = query.distinct().limit(100).all()  # Limit for performance
    data = [serialize_player(p) for p in players]

    return jsonify(data), 200



@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = (
        Player.query.options(
            joinedload(Player.seasons),
            joinedload(Player.valuations)
        )
        .filter(Player.id == player_id)
        .first()
    )

    if not player:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(serialize_player(player)), 200




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
            }
            for v in sorted(p.valuations, key=lambda v: v.date or "", reverse=True)
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
            }
            for s in sorted(p.seasons, key=lambda s: s.year_code or "", reverse=True)
        ],
    }
