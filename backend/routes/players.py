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
        "short_name": p.short_name,
        "birth_year": p.birth_year,
        "transfermarkt_player_id": p.transfermarkt_player_id,
        "nationality_iso2": p.nationality_iso2,
        "nationality_fifa": p.nationality_fifa,
        "valuations": [
            {
                "id": v.id,
                "date": v.date.isoformat() if v.date else None,
                "amount": v.amount,  # FLOAT in DB; serialized as number
            }
            for v in sorted(p.valuations, key=lambda v: v.date or "", reverse=True)
        ],
        "seasons": [
            {
                "id": s.id,
                "year_code": s.year_code,
                "nation": s.nation,
                "position": s.position,
                "club": s.club,
                "age": s.age,
                "born_year": s.born_year,
                "matches_played": s.matches_played,
                "matches_started": s.matches_started,
                "minutes_played": s.minutes_played,
                "goals_scored": s.goals_scored,
                "assists_made": s.assists_made,
                "goals_plus_assists": s.goals_plus_assists,
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
                "passes_completed": s.passes_completed,
                "passes_attempted": s.passes_attempted,
                "pass_completion_pct": s.pass_completion_pct,
                "pass_total_distance": s.pass_total_distance,
                "pass_progressive_distance": s.pass_progressive_distance,
                "short_passes_completed": s.short_passes_completed,
                "short_passes_attempted": s.short_passes_attempted,
                "medium_passes_completed": s.medium_passes_completed,
                "medium_passes_attempted": s.medium_passes_attempted,
                "long_passes_completed": s.long_passes_completed,
                "long_passes_attempted": s.long_passes_attempted,
                "key_passes": s.key_passes,
                "passes_into_final_third": s.passes_into_final_third,
                "passes_into_penalty_area": s.passes_into_penalty_area,
                "crosses_into_pa": s.crosses_into_pa,
                "tackles": s.tackles,
                "tackles_won": s.tackles_won,
                "tackles_def_3rd": s.tackles_def_3rd,
                "tackles_mid_3rd": s.tackles_mid_3rd,
                "tackles_att_3rd": s.tackles_att_3rd,
                "challenges_tackles": s.challenges_tackles,
                "challenges_attempted": s.challenges_attempted,
                "challenges_tackle_pct": s.challenges_tackle_pct,
                "challenges_lost": s.challenges_lost,
                "blocks": s.blocks,
                "blocks_shots": s.blocks_shots,
                "blocks_passes": s.blocks_passes,
                "interceptions": s.interceptions,
                "tackles_plus_interceptions": s.tackles_plus_interceptions,
                "clearances": s.clearances,
                "errors_leading_to_shot": s.errors_leading_to_shot,
            }
            for s in sorted(p.seasons, key=lambda s: s.year_code or "", reverse=True)
        ],
    }
