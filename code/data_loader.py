"""
Data Loader for European Soccer Dataset
Converts SQLite database to MongoDB collections
"""

import sqlite3
import pymongo
from pymongo import MongoClient
from datetime import datetime
import json
from tqdm import tqdm

class SoccerDataLoader:
    def __init__(self, sqlite_path, mongo_uri='mongodb://localhost:27017/', db_name='soccer_db'):
        """Initialize connections to SQLite and MongoDB"""
        self.sqlite_path = sqlite_path
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        
        print(f"Connected to SQLite: {sqlite_path}")
        print(f"Connected to MongoDB: {db_name}")
    
    def clean_date(self, date_str):
        """Convert date string to ISO 8601 timestamp"""
        if not date_str:
            return None
        try:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def load_countries(self):
        """Load country data"""
        print("\nLoading countries...")
        cursor = self.sqlite_conn.execute("SELECT * FROM Country")
        countries = []
        
        for row in cursor:
            country = {
                'country_id': row['id'],
                'name': row['name']
            }
            countries.append(country)
        
        if countries:
            self.db.countries.delete_many({})
            self.db.countries.insert_many(countries)
            self.db.countries.create_index('country_id', unique=True)
            print(f"Loaded {len(countries)} countries")
        
        return len(countries)
    
    def load_leagues(self):
        """Load league data"""
        print("\nLoading leagues...")
        cursor = self.sqlite_conn.execute("""
            SELECT l.*, c.name as country_name 
            FROM League l 
            LEFT JOIN Country c ON l.country_id = c.id
        """)
        leagues = []
        
        for row in cursor:
            league = {
                'league_id': row['id'],
                'country_id': row['country_id'],
                'name': row['name'],
                'country_name': row['country_name']
            }
            leagues.append(league)
        
        if leagues:
            self.db.leagues.delete_many({})
            self.db.leagues.insert_many(leagues)
            self.db.leagues.create_index('league_id', unique=True)
            self.db.leagues.create_index('name')
            print(f"Loaded {len(leagues)} leagues")
        
        return len(leagues)
    
    def load_teams(self):
        """Load team data"""
        print("\nLoading teams...")
        cursor = self.sqlite_conn.execute("SELECT * FROM Team")
        teams = []
        
        for row in cursor:
            team = {
                'team_api_id': row['team_api_id'],
                'team_fifa_api_id': row['team_fifa_api_id'],
                'team_long_name': row['team_long_name'],
                'team_short_name': row['team_short_name']
            }
            teams.append(team)
        
        if teams:
            self.db.teams.delete_many({})
            self.db.teams.insert_many(teams)
            self.db.teams.create_index('team_api_id', unique=True)
            self.db.teams.create_index('team_long_name')
            self.db.teams.create_index('team_short_name')
            print(f"Loaded {len(teams)} teams")
        
        return len(teams)
    
    def load_players(self):
        """Load player data"""
        print("\nLoading players...")
        cursor = self.sqlite_conn.execute("SELECT * FROM Player")
        players = []
        
        for row in cursor:
            player = {
                'player_api_id': row['player_api_id'],
                'player_fifa_api_id': row['player_fifa_api_id'],
                'player_name': row['player_name'],
                'birthday': self.clean_date(row['birthday']),
                'height': row['height'],
                'weight': row['weight']
            }
            players.append(player)
        
        if players:
            self.db.players.delete_many({})
            self.db.players.insert_many(players)
            self.db.players.create_index('player_api_id', unique=True)
            self.db.players.create_index('player_name')
            print(f"Loaded {len(players)} players")
        
        return len(players)
    
    def load_matches(self):
        """Load match data with team and league information"""
        print("\nLoading matches...")
        cursor = self.sqlite_conn.execute("""
            SELECT m.*, 
                   l.name as league_name,
                   ht.team_long_name as home_team_name,
                   at.team_long_name as away_team_name,
                   c.name as country_name
            FROM Match m
            LEFT JOIN League l ON m.league_id = l.id
            LEFT JOIN Team ht ON m.home_team_api_id = ht.team_api_id
            LEFT JOIN Team at ON m.away_team_api_id = at.team_api_id
            LEFT JOIN Country c ON m.country_id = c.id
        """)
        
        matches = []
        batch_size = 1000
        count = 0
        
        for row in cursor:
            match = {
                'match_api_id': row['match_api_id'],
                'country_id': row['country_id'],
                'country_name': row['country_name'],
                'league_id': row['league_id'],
                'league_name': row['league_name'],
                'season': row['season'],
                'stage': row['stage'],
                'date': self.clean_date(row['date']),
                'home_team_api_id': row['home_team_api_id'],
                'home_team_name': row['home_team_name'],
                'away_team_api_id': row['away_team_api_id'],
                'away_team_name': row['away_team_name'],
                'home_team_goal': row['home_team_goal'],
                'away_team_goal': row['away_team_goal'],
                'result': self._determine_result(row['home_team_goal'], row['away_team_goal'])
            }
            matches.append(match)
            count += 1
            
            if len(matches) >= batch_size:
                self.db.matches.insert_many(matches)
                matches = []
                print(f"  Inserted {count} matches...", end='\r')
        
        if matches:
            self.db.matches.insert_many(matches)
        
        self.db.matches.create_index('match_api_id', unique=True)
        self.db.matches.create_index('league_name')
        self.db.matches.create_index('season')
        self.db.matches.create_index('home_team_name')
        self.db.matches.create_index('away_team_name')
        self.db.matches.create_index('date')
        
        print(f"\nLoaded {count} matches")
        return count
    
    def _determine_result(self, home_goals, away_goals):
        """Determine match result from home team perspective"""
        if home_goals is None or away_goals is None:
            return 'unknown'
        if home_goals > away_goals:
            return 'home_win'
        elif home_goals < away_goals:
            return 'away_win'
        else:
            return 'draw'
    
    def load_player_attributes(self, limit=None):
        """Load player attributes"""
        print("\nLoading player attributes...")
        
        query = "SELECT * FROM Player_Attributes"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = self.sqlite_conn.execute(query)
        attributes = []
        batch_size = 1000
        count = 0
        
        for row in cursor:
            attr = {
                'player_fifa_api_id': row['player_fifa_api_id'],
                'player_api_id': row['player_api_id'],
                'date': self.clean_date(row['date']),
                'overall_rating': row['overall_rating'],
                'potential': row['potential'],
                'preferred_foot': row['preferred_foot'],
                'attacking_work_rate': row['attacking_work_rate'],
                'defensive_work_rate': row['defensive_work_rate'],
                'crossing': row['crossing'],
                'finishing': row['finishing'],
                'heading_accuracy': row['heading_accuracy'],
                'short_passing': row['short_passing'],
                'volleys': row['volleys'],
                'dribbling': row['dribbling'],
                'curve': row['curve'],
                'free_kick_accuracy': row['free_kick_accuracy'],
                'long_passing': row['long_passing'],
                'ball_control': row['ball_control'],
                'acceleration': row['acceleration'],
                'sprint_speed': row['sprint_speed'],
                'agility': row['agility'],
                'reactions': row['reactions'],
                'balance': row['balance'],
                'shot_power': row['shot_power'],
                'jumping': row['jumping'],
                'stamina': row['stamina'],
                'strength': row['strength'],
                'long_shots': row['long_shots'],
                'aggression': row['aggression'],
                'interceptions': row['interceptions'],
                'positioning': row['positioning'],
                'vision': row['vision'],
                'penalties': row['penalties'],
                'marking': row['marking'],
                'standing_tackle': row['standing_tackle'],
                'sliding_tackle': row['sliding_tackle'],
                'gk_diving': row['gk_diving'],
                'gk_handling': row['gk_handling'],
                'gk_kicking': row['gk_kicking'],
                'gk_positioning': row['gk_positioning'],
                'gk_reflexes': row['gk_reflexes']
            }
            attributes.append(attr)
            count += 1
            
            if len(attributes) >= batch_size:
                self.db.player_attributes.insert_many(attributes)
                attributes = []
                print(f"  Inserted {count} player attributes...", end='\r')
        
        if attributes:
            self.db.player_attributes.insert_many(attributes)
        
        self.db.player_attributes.create_index('player_api_id')
        self.db.player_attributes.create_index('date')
        self.db.player_attributes.create_index([('player_api_id', 1), ('date', -1)])
        
        print(f"\nLoaded {count} player attributes")
        return count
    
    def load_all(self, load_player_attrs=True, player_attr_limit=None):
        """Load all data into MongoDB"""
        print("="*60)
        print("Starting data import to MongoDB")
        print("="*60)
        
        print("\nDropping existing collections...")
        for collection in ['countries', 'leagues', 'teams', 'players', 'matches', 'player_attributes']:
            self.db[collection].drop()
        
        self.load_countries()
        self.load_leagues()
        self.load_teams()
        self.load_players()
        self.load_matches()
        
        if load_player_attrs:
            self.load_player_attributes(limit=player_attr_limit)
        
        print("\n" + "="*60)
        print("Data import complete!")
        print("="*60)
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary of loaded data"""
        print("\nDatabase Summary:")
        print(f"  Countries: {self.db.countries.count_documents({})}")
        print(f"  Leagues: {self.db.leagues.count_documents({})}")
        print(f"  Teams: {self.db.teams.count_documents({})}")
        print(f"  Players: {self.db.players.count_documents({})}")
        print(f"  Matches: {self.db.matches.count_documents({})}")
        print(f"  Player Attributes: {self.db.player_attributes.count_documents({})}")
    
    def close(self):
        """Close database connections"""
        self.sqlite_conn.close()
        self.mongo_client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_loader.py <path_to_sqlite_database>")
        print("Example: python data_loader.py data/database.sqlite")
        sys.exit(1)
    
    sqlite_path = sys.argv[1]
    
    loader = SoccerDataLoader(sqlite_path)
    loader.load_all(load_player_attrs=True, player_attr_limit=None)
    loader.close()
