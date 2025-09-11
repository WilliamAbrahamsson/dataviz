import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin


# 24/25



import requests
import json
import time
from typing import Dict, List, Any

# Configuration
squad_endpoint = "https://tmapi-alpha.transfermarkt.technology/club/{club_id}/squad?season=2024-25"
premier_league_teams = {
    "arsenal": 11,
    "man city": 281,
    "liverpool": 31,
    "chelsea": 631,
    "man united": 985,
    "tottenham": 148,
    "aston villa": 405,
    "newcastle united": 762,
    "brighton & hove albion": 1237,
    "crystal palace": 873,
    "afc bournemouth": 989,
    "leicester": 1003,
    "ipswich": 677,
    "southampton": 180,
    "fulham": 931,
    "everton": 29,
    "west ham": 379,
    "brentford": 1148,
    "wolves": 543,
    "nottingham": 703
}

def fetch_team_squad(team_name: str, club_id: int) -> Dict[str, Any]:
    """
    Fetch squad data for a specific team
    
    Args:
        team_name: Name of the team
        club_id: Transfermarkt club ID
        
    Returns:
        Dictionary containing team info and squad data
    """
    url = squad_endpoint.format(club_id=club_id)
    
    try:
        print(f"Fetching squad data for {team_name} (ID: {club_id})...")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') and 'data' in data:
            squad = data['data'].get('squad', [])
            
            team_data = {
                'team_name': team_name,
                'team_id': club_id,
                'squad_count': len(squad),
                'squad': squad
            }
            
            print(f"✓ Successfully fetched {len(squad)} players for {team_name}")
            return team_data
            
        else:
            print(f"✗ No valid data returned for {team_name}")
            return {
                'team_name': team_name,
                'team_id': club_id,
                'squad_count': 0,
                'squad': [],
                'error': 'No valid data returned'
            }
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed for {team_name}: {e}")
        return {
            'team_name': team_name,
            'team_id': club_id,
            'squad_count': 0,
            'squad': [],
            'error': str(e)
        }
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error for {team_name}: {e}")
        return {
            'team_name': team_name,
            'team_id': club_id,
            'squad_count': 0,
            'squad': [],
            'error': f'JSON decode error: {str(e)}'
        }
    except Exception as e:
        print(f"✗ Unexpected error for {team_name}: {e}")
        return {
            'team_name': team_name,
            'team_id': club_id,
            'squad_count': 0,
            'squad': [],
            'error': f'Unexpected error: {str(e)}'
        }

def fetch_all_squads() -> Dict[str, Any]:
    """
    Fetch squad data for all Premier League teams
    
    Returns:
        Dictionary containing all teams' squad data
    """
    all_teams_data = {
        'season': '2024-25',
        'league': 'Premier League',
        'total_teams': len(premier_league_teams),
        'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'teams': []
    }
    
    successful_fetches = 0
    
    for team_name, club_id in premier_league_teams.items():
        team_data = fetch_team_squad(team_name, club_id)
        all_teams_data['teams'].append(team_data)
        
        if 'error' not in team_data:
            successful_fetches += 1
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(1)
    
    all_teams_data['successful_fetches'] = successful_fetches
    all_teams_data['failed_fetches'] = len(premier_league_teams) - successful_fetches
    
    return all_teams_data

def save_to_json(data: Dict[str, Any], filename: str = 'premier_league_squads_2024_25.json'):
    """
    Save the data to a JSON file
    
    Args:
        data: Data to save
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to {filename}")
        
        # Print summary
        total_players = sum(team.get('squad_count', 0) for team in data['teams'])
        print(f"\nSUMMARY:")
        print(f"Total teams: {data['total_teams']}")
        print(f"Successful fetches: {data['successful_fetches']}")
        print(f"Failed fetches: {data['failed_fetches']}")
        print(f"Total players: {total_players}")
        
    except Exception as e:
        print(f"✗ Error saving to JSON: {e}")

def main():
    """Main function to orchestrate the data fetching"""
    print("Starting Premier League squad data collection for 2024-25 season...\n")
    
    # Fetch all squad data
    all_data = fetch_all_squads()
    
    # Save to JSON file
    save_to_json(all_data)
    
    print("\n" + "="*50)
    print("Data collection complete!")

if __name__ == "__main__":
    main()