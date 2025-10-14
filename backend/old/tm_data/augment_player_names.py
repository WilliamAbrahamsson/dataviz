import requests
import json
import time
from typing import Dict, List, Any, Optional
import os

# Configuration
PLAYER_VALUE_ENDPOINT = "https://tmapi-alpha.transfermarkt.technology/player/{player_id}"
INPUT_FILE = "premier_league_squads_2024_25.json"
OUTPUT_FILE = "premier_league_squads_2024_25_with_names.json"

def load_squad_data(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load the existing squad data from JSON file
    
    Args:
        filename: Path to the input JSON file
        
    Returns:
        Dictionary containing squad data or None if error
    """
    try:
        if not os.path.exists(filename):
            print(f"✗ Input file '{filename}' not found!")
            return None
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"✓ Loaded squad data with {len(data.get('teams', []))} teams")
        return data
        
    except json.JSONDecodeError as e:
        print(f"✗ Error reading JSON file: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error loading file: {e}")
        return None

def fetch_player_info(player_id: str) -> Dict[str, Any]:
    """
    Fetch player information from Transfermarkt API
    
    Args:
        player_id: Transfermarkt player ID
        
    Returns:
        Dictionary containing player info
    """
    url = PLAYER_VALUE_ENDPOINT.format(player_id=player_id)
    
    try:
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
            player_data = data['data']
            
            # Extract relevant player information
            player_info = {
                'name': player_data.get('name', ''),
                'short_name': player_data.get('shortName', ''),
                'display_name': player_data.get('displayName', ''),
                'age': player_data.get('lifeDates', {}).get('age'),
                'date_of_birth': player_data.get('lifeDates', {}).get('dateOfBirth'),
                'place_of_birth': player_data.get('birthPlaceDetails', {}).get('placeOfBirth', ''),
                'country_of_birth_id': player_data.get('birthPlaceDetails', {}).get('countryOfBirthId'),
                'gender': player_data.get('birthPlaceDetails', {}).get('gender', ''),
            }
            
            return player_info
            
        else:
            return {
                'name': 'Unknown',
                'error': 'No valid data returned'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'name': 'Unknown',
            'error': f'Request failed: {str(e)}'
        }
    except json.JSONDecodeError as e:
        return {
            'name': 'Unknown',
            'error': f'JSON decode error: {str(e)}'
        }
    except Exception as e:
        return {
            'name': 'Unknown',
            'error': f'Unexpected error: {str(e)}'
        }

def augment_squad_with_names(squad_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Augment squad data with player names
    
    Args:
        squad_data: Original squad data
        
    Returns:
        Augmented squad data with player names
    """
    augmented_data = squad_data.copy()
    augmented_data['augmented_at'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    total_players = 0
    successful_fetches = 0
    failed_fetches = 0
    
    # Count total players first
    for team in augmented_data['teams']:
        total_players += len(team.get('squad', []))
    
    print(f"\nStarting player name augmentation for {total_players} players...\n")
    
    current_player = 0
    
    for team_idx, team in enumerate(augmented_data['teams']):
        team_name = team.get('team_name', 'Unknown')
        squad = team.get('squad', [])
        
        print(f"Processing {team_name} ({len(squad)} players)...")
        
        for player_idx, player in enumerate(squad):
            current_player += 1
            player_id = player.get('playerId', '')
            
            if not player_id:
                print(f"  ✗ No player ID for player {player_idx + 1}")
                player['player_info'] = {
                    'name': 'Unknown',
                    'error': 'No player ID provided'
                }
                failed_fetches += 1
                continue
            
            print(f"  [{current_player}/{total_players}] Fetching info for player ID: {player_id}")
            
            # Fetch player information
            player_info = fetch_player_info(player_id)
            
            # Add player info to the player object
            player['player_info'] = player_info
            
            if 'error' in player_info:
                failed_fetches += 1
                print(f"    ✗ Failed: {player_info.get('error', 'Unknown error')}")
            else:
                successful_fetches += 1
                player_name = player_info.get('name', 'Unknown')
                print(f"    ✓ {player_name}")
            
            # Add delay to avoid overwhelming the API
            time.sleep(0.5)  # 0.5 second delay between requests
    
    # Update statistics
    augmented_data['player_info_stats'] = {
        'total_players': total_players,
        'successful_fetches': successful_fetches,
        'failed_fetches': failed_fetches,
        'success_rate': round((successful_fetches / total_players) * 100, 2) if total_players > 0 else 0
    }
    
    return augmented_data

def save_augmented_data(data: Dict[str, Any], filename: str):
    """
    Save the augmented data to a JSON file
    
    Args:
        data: Augmented data to save
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Augmented data saved to {filename}")
        
        # Print summary
        stats = data.get('player_info_stats', {})
        print(f"\nAUGMENTATION SUMMARY:")
        print(f"Total players: {stats.get('total_players', 0)}")
        print(f"Successful fetches: {stats.get('successful_fetches', 0)}")
        print(f"Failed fetches: {stats.get('failed_fetches', 0)}")
        print(f"Success rate: {stats.get('success_rate', 0)}%")
        
        # Show file sizes
        input_size = os.path.getsize(INPUT_FILE) / 1024 / 1024
        output_size = os.path.getsize(filename) / 1024 / 1024
        print(f"\nFile sizes:")
        print(f"Input file: {input_size:.2f} MB")
        print(f"Output file: {output_size:.2f} MB")
        print(f"Size increase: {((output_size - input_size) / input_size * 100):.1f}%")
        
    except Exception as e:
        print(f"✗ Error saving augmented data: {e}")

def create_sample_output():
    """Show example of what the augmented data structure looks like"""
    sample = {
        "team_name": "arsenal",
        "team_id": 11,
        "squad_count": 25,
        "squad": [
            {
                "playerId": "337082",
                "clubId": "11",
                "shirtNumber": 1,
                "isCaptain": False,
                "type": "historical",
                "player_info": {
                    "name": "David Raya",
                    "short_name": "D. Raya",
                    "display_name": "",
                    "age": 29,
                    "date_of_birth": "1995-09-15",
                    "place_of_birth": "Barcelona",
                    "country_of_birth_id": 157,
                    "gender": "male"
                }
            }
        ]
    }
    
    print("Example of augmented data structure:")
    print(json.dumps(sample, indent=2))

def main():
    """Main function to orchestrate the data augmentation"""
    print("Premier League Squad Data Augmentation with Player Names")
    print("=" * 60)
    
    # Load existing squad data
    squad_data = load_squad_data(INPUT_FILE)
    if squad_data is None:
        print(f"\n✗ Cannot proceed without input data. Please ensure '{INPUT_FILE}' exists.")
        return
    
    # Show what the output will look like
    print("\n" + "-" * 40)
    create_sample_output()
    print("-" * 40)
    
    # Confirm before starting (this will take a while)
    total_players = sum(len(team.get('squad', [])) for team in squad_data.get('teams', []))
    estimated_time = (total_players * 0.5) / 60  # 0.5 seconds per request
    
    print(f"\nThis will fetch data for {total_players} players.")
    print(f"Estimated time: {estimated_time:.1f} minutes")
    
    response = input("\nProceed with augmentation? (y/n): ").strip().lower()
    if response != 'y':
        print("Augmentation cancelled.")
        return
    
    # Augment the data with player names
    augmented_data = augment_squad_with_names(squad_data)
    
    # Save the augmented data
    save_augmented_data(augmented_data, OUTPUT_FILE)
    
    print("\n" + "=" * 60)
    print("Data augmentation complete!")
    print(f"Check '{OUTPUT_FILE}' for the results with player names.")

if __name__ == "__main__":
    main()