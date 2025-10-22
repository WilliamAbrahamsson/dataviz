from flask import Blueprint

from .players import players_bp
from .map_positions import map_bp

def register_routes(app):
    app.register_blueprint(players_bp)
    app.register_blueprint(map_bp)
