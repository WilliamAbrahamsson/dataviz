from flask import Blueprint

# Import blueprints from route files
from .players import players_bp

# Export a list of all route blueprints
def register_routes(app):
    app.register_blueprint(players_bp)
