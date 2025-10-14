from flask import Blueprint

from .players import players_bp

def register_routes(app):
    app.register_blueprint(players_bp)
