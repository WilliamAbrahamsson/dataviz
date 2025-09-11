import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

class TransfermarktScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_premier_league_teams(self):
        """Get all Premier League teams and their squad URLs"""
        # Try multiple approaches to get all teams
        teams = []
        
        # Method 1: From league table page
        pl_table_url = "https://www.transfermarkt.com/premier-league/tabelle/wettbewerb/GB1/saison_id/2024"
        teams.extend(self._get_teams_from_table(pl_table_url))
        
        # Method 2: From clubs page
        if len(teams) < 20:
            pl_clubs_url = "https://www.transfermarkt.com/premier-league/vereine/wettbewerb/GB1/saison_id/2024"
            teams.extend(self._get_teams_from_clubs_page(pl_clubs_url))
        
        # Method 3: Manual fallback with all current PL teams
        if len(teams) < 20:
            teams = self._get_all_pl_teams_manual()
        
        # Remove duplicates
        unique_teams = []
        seen_ids = set()
        for team in teams:
            team_id = self._extract_team_id(team['squad_url'])
            if team_id and team_id not in seen_ids:
                unique_teams.append(team)
                seen_ids.add(team_id)
        
        print(f"Found {len(unique_teams)} Premier League teams")
        return unique_teams[:20]  # Ensure exactly 20 teams
    
    def _extract_team_id(self, url):
        """Extract team ID from URL"""
        match = re.search(r'/verein/(\d+)', url)
        return match.group(1) if match else None
    
    def _get_teams_from_table(self, table_url):
        """Get teams from league table"""
        teams = []
        try:
            response = self.session.get(table_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find team links in the table
            team_links = soup.find_all('a', href=re.compile(r'/[\w-]+/startseite/verein/\d+'))
            
            for link in team_links:
                team_name = link.get('title') or link.text.strip()
                if team_name and len(team_name) > 2:  # Filter out short/invalid names
                    team_id = re.search(r'/verein/(\d+)', link.get('href', ''))
                    if team_id:
                        squad_url = f"https://www.transfermarkt.com/{link.get('href').split('/')[1]}/kader/verein/{team_id.group(1)}/saison_id/2025"
                        teams.append({
                            'name': team_name,
                            'squad_url': squad_url
                        })
        except Exception as e:
            print(f"Error getting teams from table: {e}")
        
        return teams
    
    def _get_teams_from_clubs_page(self, clubs_url):
        """Get teams from clubs page"""
        teams = []
        try:
            response = self.session.get(clubs_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find club links
            club_links = soup.find_all('a', href=re.compile(r'/[\w-]+/startseite/verein/\d+'))
            
            for link in club_links:
                team_name = link.get('title') or link.text.strip()
                if team_name and len(team_name) > 2:
                    team_id = re.search(r'/verein/(\d+)', link.get('href', ''))
                    if team_id:
                        squad_url = f"https://www.transfermarkt.com/{link.get('href').split('/')[1]}/kader/verein/{team_id.group(1)}/saison_id/2025"
                        teams.append({
                            'name': team_name,
                            'squad_url': squad_url
                        })
        except Exception as e:
            print(f"Error getting teams from clubs page: {e}")
        
        return teams
    
    def _get_all_pl_teams_manual(self):
        """Manual fallback with all 2024-25 Premier League teams"""
        return [
            {'name': 'Arsenal FC', 'squad_url': 'https://www.transfermarkt.com/fc-arsenal/kader/verein/11/saison_id/2025'},
            {'name': 'Aston Villa', 'squad_url': 'https://www.transfermarkt.com/aston-villa/kader/verein/405/saison_id/2025'},
            {'name': 'AFC Bournemouth', 'squad_url': 'https://www.transfermarkt.com/afc-bournemouth/kader/verein/989/saison_id/2025'},
            {'name': 'Brentford FC', 'squad_url': 'https://www.transfermarkt.com/brentford-fc/kader/verein/1148/saison_id/2025'},
            {'name': 'Brighton & Hove Albion', 'squad_url': 'https://www.transfermarkt.com/brighton-amp-hove-albion/kader/verein/1237/saison_id/2025'},
            {'name': 'Chelsea FC', 'squad_url': 'https://www.transfermarkt.com/fc-chelsea/kader/verein/631/saison_id/2025'},
            {'name': 'Crystal Palace', 'squad_url': 'https://www.transfermarkt.com/crystal-palace/kader/verein/873/saison_id/2025'},
            {'name': 'Everton FC', 'squad_url': 'https://www.transfermarkt.com/fc-everton/kader/verein/29/saison_id/2025'},
            {'name': 'Fulham FC', 'squad_url': 'https://www.transfermarkt.com/fc-fulham/kader/verein/931/saison_id/2025'},
            {'name': 'Ipswich Town', 'squad_url': 'https://www.transfermarkt.com/ipswich-town/kader/verein/677/saison_id/2025'},
            {'name': 'Leicester City', 'squad_url': 'https://www.transfermarkt.com/leicester-city/kader/verein/1003/saison_id/2025'},
            {'name': 'Liverpool FC', 'squad_url': 'https://www.transfermarkt.com/fc-liverpool/kader/verein/31/saison_id/2025'},
            {'name': 'Manchester City', 'squad_url': 'https://www.transfermarkt.com/manchester-city/kader/verein/281/saison_id/2025'},
            {'name': 'Manchester United', 'squad_url': 'https://www.transfermarkt.com/manchester-united/kader/verein/985/saison_id/2025'},
            {'name': 'Newcastle United', 'squad_url': 'https://www.transfermarkt.com/newcastle-united/kader/verein/762/saison_id/2025'},
            {'name': 'Nottingham Forest', 'squad_url': 'https://www.transfermarkt.com/nottingham-forest/kader/verein/703/saison_id/2025'},
            {'name': 'Southampton FC', 'squad_url': 'https://www.transfermarkt.com/fc-southampton/kader/verein/180/saison_id/2025'},
            {'name': 'Tottenham Hotspur', 'squad_url': 'https://www.transfermarkt.com/tottenham-hotspur/kader/verein/148/saison_id/2025'},
            {'name': 'West Ham United', 'squad_url': 'https://www.transfermarkt.com/west-ham-united/kader/verein/379/saison_id/2025'},
            {'name': 'Wolverhampton Wanderers', 'squad_url': 'https://www.transfermarkt.com/wolverhampton-wanderers/kader/verein/543/saison_id/2025'}
        ]
    
    def extract_player_id(self, player_url):
        """Extract player ID from player URL"""
        if player_url:
            match = re.search(r'/profil/spieler/(\d+)', player_url)
            if match:
                return match.group(1)
        return None
    
    def scrape_team_players(self, team_name, squad_url):
        """Scrape all players from a team's squad page"""
        print(f"Scraping {team_name}...")
        
        try:
            response = self.session.get(squad_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            players = []
            
            # Find the squad table
            squad_table = soup.find('table', class_='items')
            if not squad_table:
                print(f"No squad table found for {team_name}")
                return players
            
            # Find all player rows
            player_rows = squad_table.find_all('tr', class_=['odd', 'even'])
            
            for row in player_rows:
                try:
                    # Find player name and link
                    player_cell = row.find('td', class_='posrela')
                    if not player_cell:
                        continue
                    
                    player_link = player_cell.find('a', href=re.compile(r'/profil/spieler/\d+'))
                    if not player_link:
                        continue
                    
                    player_name = player_link.get('title') or player_link.text.strip()
                    player_url = urljoin(self.base_url, player_link.get('href'))
                    player_id = self.extract_player_id(player_url)
                    
                    if player_name and player_id:
                        players.append({
                            'name': player_name,
                            'club': team_name,
                            'id': player_id
                        })
                
                except Exception as e:
                    print(f"Error processing player row: {e}")
                    continue
            
            print(f"Found {len(players)} players for {team_name}")
            return players
            
        except Exception as e:
            print(f"Error scraping {team_name}: {e}")
            return []
    
    def scrape_all_premier_league_players(self):
        """Scrape all Premier League players"""
        print("Getting Premier League teams...")
        teams = self.get_premier_league_teams()

        
        print(f"Found {len(teams)} teams")
        
        all_players = []
        
        for i, team in enumerate(teams):
            try:
                players = self.scrape_team_players(team['name'], team['squad_url'])
                all_players.extend(players)
                
                # Be respectful to the server
                if i < len(teams) - 1:  # Don't sleep after the last request
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Failed to scrape {team['name']}: {e}")
                continue
        
        return all_players
    
    def save_to_json(self, players, filename='premier_league_players_2025.json'):
        """Save players data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(players, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
            print(f"Total players scraped: {len(players)}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

def main():
    scraper = TransfermarktScraper()
    
    print("Starting Premier League player scraper...")
    print("This may take a few minutes due to rate limiting...")
    
    players = scraper.scrape_all_premier_league_players()
    
    if players:
        scraper.save_to_json(players)
        
        # Print sample of results
        print("\nSample of scraped data:")
        for player in players[:5]:
            print(f"Name: {player['name']}, Club: {player['club']}, ID: {player['id']}")
    else:
        print("No players were scraped successfully")

if __name__ == "__main__":
    main()