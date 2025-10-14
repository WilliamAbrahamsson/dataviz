import requests
import json
import time
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

# Configuration
PLAYER_VALUE_ENDPOINT = "https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history"
INPUT_FILE = "premier_league_squads_2024_25_with_names.json"
OUTPUT_FILE = "premier_league_squads_2024_25_complete.json"

def load_squad_data(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load the existing squad data with names from JSON file
    
    Args:
        filename: Path to the input JSON file
        
    Returns:
        Dictionary containing squad data or None if error
    """
    try:
        if not os.path.exists(filename):
            print(f"✗ Input file '{filename}' not found!")
            print(f"Please make sure you have run the previous script to generate the file with player names.")
            return None
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        total_players = sum(len(team.get('squad', [])) for team in data.get('teams', []))
        print(f"✓ Loaded squad data with {len(data.get('teams', []))} teams and {total_players} players")
        return data
        
    except json.JSONDecodeError as e:
        print(f"✗ Error reading JSON file: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error loading file: {e}")
        return None

def fetch_player_market_value(player_id: str) -> Dict[str, Any]:
    """
    Fetch player market value history from Transfermarkt API
    
    Args:
        player_id: Transfermarkt player ID
        
    Returns:
        Dictionary containing market value information
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
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') and 'data' in data:
            market_data = data['data']
            
            # Extract current market value
            current_value = market_data.get('current', {})
            history = market_data.get('history', [])
            
            # Calculate additional metrics
            values = [entry.get('marketValue', {}).get('value', 0) for entry in history if entry.get('marketValue')]
            peak_value = max(values) if values else 0
            
            # Find peak value details
            peak_entry = None
            for entry in history:
                if entry.get('marketValue', {}).get('value', 0) == peak_value:
                    peak_entry = entry
                    break
            
            valuation_info = {
                'current_market_value': {
                    'value': current_value.get('marketValue', {}).get('value', 0),
                    'currency': current_value.get('marketValue', {}).get('currency', 'EUR'),
                    'compact_display': current_value.get('marketValue', {}).get('compact', {}),
                    'determined_date': current_value.get('marketValue', {}).get('determined'),
                    'age_at_valuation': current_value.get('age')
                },
                'peak_market_value': {
                    'value': peak_value,
                    'currency': peak_entry.get('marketValue', {}).get('currency', 'EUR') if peak_entry else 'EUR',
                    'compact_display': peak_entry.get('marketValue', {}).get('compact', {}) if peak_entry else {},
                    'determined_date': peak_entry.get('marketValue', {}).get('determined') if peak_entry else None,
                    'age_at_peak': peak_entry.get('age') if peak_entry else None
                },
                'value_history_summary': {
                    'total_valuations': len(history),
                    'highest_value': peak_value,
                    'lowest_value': min(values) if values else 0,
                    'average_value': round(sum(values) / len(values)) if values else 0
                },
                'complete_market_value_history': history,  # COMPLETE historical timeline with all valuations
                'raw_api_response': {
                    'history': history,
                    'current': current_value,
                    'player_ids': market_data.get('playerIds', []),
                    'club_ids': market_data.get('clubIds', [])
                }
            }
            
            return valuation_info
            
        else:
            return {
                'current_market_value': {
                    'value': 0,
                    'currency': 'EUR',
                    'error': 'No valid data returned'
                },
                'error': 'No valid market value data returned'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'current_market_value': {
                'value': 0,
                'currency': 'EUR',
                'error': f'Request failed: {str(e)}'
            },
            'error': f'Request failed: {str(e)}'
        }
    except json.JSONDecodeError as e:
        return {
            'current_market_value': {
                'value': 0,
                'currency': 'EUR',
                'error': f'JSON decode error: {str(e)}'
            },
            'error': f'JSON decode error: {str(e)}'
        }
    except Exception as e:
        return {
            'current_market_value': {
                'value': 0,
                'currency': 'EUR',
                'error': f'Unexpected error: {str(e)}'
            },
            'error': f'Unexpected error: {str(e)}'
        }

def format_market_value(value: int, currency: str = 'EUR') -> str:
    """
    Format market value for display
    
    Args:
        value: Market value in base currency
        currency: Currency code
        
    Returns:
        Formatted string representation
    """
    if value == 0:
        return f"{currency} 0"
    elif value >= 1000000:
        return f"{currency} {value/1000000:.1f}M"
    elif value >= 1000:
        return f"{currency} {value/1000:.0f}K"
    else:
        return f"{currency} {value:,}"

def augment_squad_with_valuations(squad_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Augment squad data with market valuations
    
    Args:
        squad_data: Squad data with player names
        
    Returns:
        Augmented squad data with market valuations
    """
    augmented_data = squad_data.copy()
    augmented_data['valuation_augmented_at'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    total_players = 0
    successful_fetches = 0
    failed_fetches = 0
    total_squad_value = {}  # Track by team
    
    # Count total players first
    for team in augmented_data['teams']:
        total_players += len(team.get('squad', []))
    
    print(f"\nStarting market valuation augmentation for {total_players} players...\n")
    
    current_player = 0
    
    for team_idx, team in enumerate(augmented_data['teams']):
        team_name = team.get('team_name', 'Unknown')
        squad = team.get('squad', [])
        team_total_value = 0
        team_successful_valuations = 0
        
        print(f"Processing {team_name} ({len(squad)} players)...")
        
        for player_idx, player in enumerate(squad):
            current_player += 1
            player_id = player.get('playerId', '')
            player_name = player.get('player_info', {}).get('name', 'Unknown Player')
            
            if not player_id:
                print(f"  ✗ No player ID for {player_name}")
                player['market_valuation'] = {
                    'current_market_value': {
                        'value': 0,
                        'currency': 'EUR',
                        'error': 'No player ID provided'
                    },
                    'error': 'No player ID provided'
                }
                failed_fetches += 1
                continue
            
            print(f"  [{current_player}/{total_players}] Fetching valuation for {player_name} (ID: {player_id})")
            
            # Fetch market valuation
            valuation_info = fetch_player_market_value(player_id)
            
            # Add market valuation to the player object
            player['market_valuation'] = valuation_info
            
            if 'error' in valuation_info:
                failed_fetches += 1
                print(f"    ✗ Failed: {valuation_info.get('error', 'Unknown error')}")
            else:
                successful_fetches += 1
                current_value = valuation_info.get('current_market_value', {}).get('value', 0)
                formatted_value = format_market_value(current_value)
                peak_value = valuation_info.get('peak_market_value', {}).get('value', 0)
                formatted_peak = format_market_value(peak_value)
                
                team_total_value += current_value
                team_successful_valuations += 1
                
                print(f"    ✓ Current: {formatted_value} | Peak: {formatted_peak}")
            
            # Add delay to avoid overwhelming the API
            time.sleep(0.7)  # Slightly longer delay for market value endpoint
        
        # Add team valuation summary
        team['team_valuation_summary'] = {
            'total_squad_value': team_total_value,
            'formatted_total_value': format_market_value(team_total_value),
            'average_player_value': round(team_total_value / team_successful_valuations) if team_successful_valuations > 0 else 0,
            'players_with_valuations': team_successful_valuations,
            'players_without_valuations': len(squad) - team_successful_valuations
        }
        
        total_squad_value[team_name] = team_total_value
        
        print(f"  Team total value: {format_market_value(team_total_value)}")
        print()
    
    # Update global statistics
    augmented_data['valuation_stats'] = {
        'total_players': total_players,
        'successful_valuations': successful_fetches,
        'failed_valuations': failed_fetches,
        'success_rate': round((successful_fetches / total_players) * 100, 2) if total_players > 0 else 0,
        'league_total_value': sum(total_squad_value.values()),
        'formatted_league_value': format_market_value(sum(total_squad_value.values())),
        'team_rankings_by_value': sorted(total_squad_value.items(), key=lambda x: x[1], reverse=True)
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
        
        print(f"✓ Complete squad data saved to {filename}")
        
        # Print comprehensive summary
        stats = data.get('valuation_stats', {})
        print(f"\nVALUATION AUGMENTATION SUMMARY:")
        print(f"Total players: {stats.get('total_players', 0)}")
        print(f"Successful valuations: {stats.get('successful_valuations', 0)}")
        print(f"Failed valuations: {stats.get('failed_valuations', 0)}")
        print(f"Success rate: {stats.get('success_rate', 0)}%")
        print(f"Total league value: {stats.get('formatted_league_value', 'N/A')}")
        
        # Show top 5 most valuable teams
        rankings = stats.get('team_rankings_by_value', [])
        if rankings:
            print(f"\nTOP 5 MOST VALUABLE SQUADS:")
            for i, (team, value) in enumerate(rankings[:5], 1):
                print(f"{i}. {team.title()}: {format_market_value(value)}")
        
        # Show file sizes
        if os.path.exists(INPUT_FILE):
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
        "playerId": "337082",
        "clubId": "11",
        "shirtNumber": 1,
        "isCaptain": False,
        "type": "historical",
        "player_info": {
            "name": "David Raya",
            "short_name": "D. Raya",
            "age": 29
        },
        "market_valuation": {
            "current_market_value": {
                "value": 30000000,
                "currency": "EUR",
                "compact_display": {
                    "prefix": "€",
                    "content": "30.00",
                    "suffix": "M"
                },
                "determined_date": "2024-06-15",
                "age_at_valuation": 29
            },
            "peak_market_value": {
                "value": 35000000,
                "currency": "EUR",
                "determined_date": "2023-12-20",
                "age_at_peak": 28
            },
            "value_history_summary": {
                "total_valuations": 15,
                "highest_value": 35000000,
                "lowest_value": 500000,
                "average_value": 18500000
            }
        }
    }
    
    print("Example of final augmented data structure:")
    print(json.dumps(sample, indent=2))

def main():
    """Main function to orchestrate the valuation augmentation"""
    print("Premier League Squad Market Valuation Augmentation")
    print("=" * 60)
    
    # Load existing squad data with names
    squad_data = load_squad_data(INPUT_FILE)
    if squad_data is None:
        print(f"\n✗ Cannot proceed without input data.")
        print(f"Please ensure '{INPUT_FILE}' exists (run the previous script first).")
        return
    
    # Show what the output will look like
    print("\n" + "-" * 40)
    create_sample_output()
    print("-" * 40)
    
    # Confirm before starting (this will take even longer)
    total_players = sum(len(team.get('squad', [])) for team in squad_data.get('teams', []))
    estimated_time = (total_players * 0.7) / 60  # 0.7 seconds per request
    
    print(f"\nThis will fetch market valuations for {total_players} players.")
    print(f"Estimated time: {estimated_time:.1f} minutes")
    print("Note: Market value endpoint may be slower than player info endpoint.")
    
    response = input("\nProceed with valuation augmentation? (y/n): ").strip().lower()
    if response != 'y':
        print("Valuation augmentation cancelled.")
        return
    
    # Augment the data with market valuations
    augmented_data = augment_squad_with_valuations(squad_data)
    
    # Save the final augmented data
    save_augmented_data(augmented_data, OUTPUT_FILE)
    
    print("\n" + "=" * 60)
    print("Complete data augmentation finished!")
    print(f"Final file: '{OUTPUT_FILE}' contains:")
    print("• Team information")
    print("• Complete squad rosters") 
    print("• Player names and details")
    print("• Current and historical market valuations")
    print("• Team valuation summaries")
    print("• League-wide statistics")

if __name__ == "__main__":
    main()