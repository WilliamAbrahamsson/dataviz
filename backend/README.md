
FLASK BACKEND / SQLITE DB

Setup:
- "python3 -m venv venv" -- Creates virtual environment
- "source venv/bin/activate"
- "pip install -r requirements.txt"


DB:

To open database manager:
- "sqlite_web instance/mydatabase.db" -- launces web interface to manage db


Structure:

Player:
- int id
- str name
- str nationality
- date born -- year born
- int transfermarkt_player_id

Player_Valuation
- int id
- float player_id -- Player.id
- date date -- different from year_code ... This is just a date
- float amount -- actual amount of valuation

Player_Season:
- int id
- float player_id -- Player.id
- str year_code -- ie "2024/25"
- float age -- age during this season
- str position
- str club
- float matches_played
- float matches_started
- float minutes_played
- float goals_scored
- float assists_made
- float goals_plus_assists
- float goals_excluding_penalties
- float penalty_goals
- float penalty_attempts
- float yellow_cards
- float red_cards
- float expected_goals
- float non_penalty_expected_goals
- float axpected_assists
- float combined_non_penalty_expected_goal_contributions
- float progressive_carries
- float progressive_passes
- float progressive_receptions



