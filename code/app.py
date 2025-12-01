"""
Flask REST API for European Soccer Database
Provides endpoints for querying MongoDB data
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from queries import SoccerQueries
from pymongo import MongoClient
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Initialize queries
queries = SoccerQueries()

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = DateTimeEncoder

@app.route('/')
def index():
    """Home page with API documentation"""
    return render_template('index.html')

@app.route('/api/info')
def api_info():
    """Return API information and available endpoints"""
    endpoints = {
        'endpoints': [
            {
                'path': '/api/team/<team_name>',
                'method': 'GET',
                'description': 'Get team info and recent match results',
                'example': '/api/team/FC Barcelona'
            },
            {
                'path': '/api/player/<player_name>',
                'method': 'GET',
                'description': 'Get player stats and attributes',
                'example': '/api/player/Lionel Messi'
            },
            {
                'path': '/api/league/<league_name>/top-teams',
                'method': 'GET',
                'description': 'Get top 5 teams by points in a league for a season',
                'parameters': 'season (query param, e.g., 2015/2016)',
                'example': '/api/league/Spain LIGA BBVA/top-teams?season=2015/2016'
            },
            {
                'path': '/api/matches/high-scoring',
                'method': 'GET',
                'description': 'Find matches where a team scored 3+ goals',
                'parameters': 'team (required), min_goals (optional, default=3)',
                'example': '/api/matches/high-scoring?team=FC Barcelona&min_goals=3'
            },
            {
                'path': '/api/team/<team_name>/season/<season>',
                'method': 'GET',
                'description': 'Get team statistics for a specific season',
                'example': '/api/team/FC Barcelona/season/2015/2016'
            },
            {
                'path': '/api/players/top',
                'method': 'GET',
                'description': 'Get top players by rating',
                'parameters': 'league (optional), limit (optional, default=10)',
                'example': '/api/players/top?limit=20'
            },
            {
                'path': '/api/leagues/stats',
                'method': 'GET',
                'description': 'Get statistics for all leagues',
                'example': '/api/leagues/stats'
            },
            {
                'path': '/api/scorelines/common',
                'method': 'GET',
                'description': 'Get most common scorelines',
                'parameters': 'limit (optional, default=10)',
                'example': '/api/scorelines/common?limit=15'
            },
            {
                'path': '/api/league/<league_name>/standings',
                'method': 'GET',
                'description': 'Get complete league standings for a season',
                'parameters': 'season (required)',
                'example': '/api/league/Spain LIGA BBVA/standings?season=2015/2016'
            },
            {
                'path': '/api/head-to-head',
                'method': 'GET',
                'description': 'Get head-to-head record between two teams',
                'parameters': 'team1 (required), team2 (required)',
                'example': '/api/head-to-head?team1=FC Barcelona&team2=Real Madrid CF'
            }
        ]
    }
    return jsonify(endpoints)

@app.route('/api/team/<team_name>')
def get_team_info(team_name):
    """
    GET /api/team/<team_name>
    Returns team info and recent match results
    """
    try:
        # Get team from database
        team = queries.db.teams.find_one({'team_long_name': team_name})
        
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Get recent matches (last 10)
        recent_matches = list(queries.db.matches.find(
            {
                '$or': [
                    {'home_team_name': team_name},
                    {'away_team_name': team_name}
                ]
            },
            {
                '_id': 0,
                'date': 1,
                'league_name': 1,
                'season': 1,
                'home_team_name': 1,
                'away_team_name': 1,
                'home_team_goal': 1,
                'away_team_goal': 1,
                'result': 1
            }
        ).sort('date', -1).limit(10))
        
        # Calculate overall statistics
        all_matches = list(queries.db.matches.find({
            '$or': [
                {'home_team_name': team_name},
                {'away_team_name': team_name}
            ]
        }))
        
        total_goals = sum(
            m['home_team_goal'] if m['home_team_name'] == team_name else m['away_team_goal']
            for m in all_matches
        )
        
        result = {
            'team_name': team_name,
            'team_info': {
                'team_api_id': team.get('team_api_id'),
                'short_name': team.get('team_short_name'),
                'long_name': team.get('team_long_name')
            },
            'statistics': {
                'total_matches': len(all_matches),
                'total_goals_scored': total_goals
            },
            'recent_matches': recent_matches
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<player_name>')
def get_player_info(player_name):
    """
    GET /api/player/<player_name>
    Returns player stats and attributes
    """
    try:
        # Get player from database
        player = queries.db.players.find_one({'player_name': player_name})
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        # Get latest attributes
        latest_attrs = queries.db.player_attributes.find_one(
            {'player_api_id': player['player_api_id']},
            sort=[('date', -1)]
        )
        
        # Get attribute history
        attr_history = queries.query_5_player_attributes_over_time(player_name)
        
        result = {
            'player_name': player_name,
            'basic_info': {
                'player_api_id': player.get('player_api_id'),
                'birthday': player.get('birthday'),
                'height': player.get('height'),
                'weight': player.get('weight')
            },
            'current_attributes': {
                'overall_rating': latest_attrs.get('overall_rating') if latest_attrs else None,
                'potential': latest_attrs.get('potential') if latest_attrs else None,
                'preferred_foot': latest_attrs.get('preferred_foot') if latest_attrs else None,
                'finishing': latest_attrs.get('finishing') if latest_attrs else None,
                'dribbling': latest_attrs.get('dribbling') if latest_attrs else None,
                'sprint_speed': latest_attrs.get('sprint_speed') if latest_attrs else None
            } if latest_attrs else None,
            'attribute_history_count': len(attr_history)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/league/<league_name>/top-teams')
def get_league_top_teams(league_name):
    """
    GET /api/league/<league_name>/top-teams
    Returns top 5 teams by points/goals in the league
    """
    try:
        season = request.args.get('season', '2015/2016')
        
        # Get league standings
        standings = queries.query_8_league_standings(league_name, season)
        
        # Return top 5
        top_teams = standings[:5]
        
        result = {
            'league_name': league_name,
            'season': season,
            'top_teams': top_teams
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matches/high-scoring')
def get_high_scoring_matches():
    """
    GET /api/matches/high-scoring?team=<team_name>&min_goals=<number>
    Find matches where a team scored 3+ goals
    """
    try:
        team = request.args.get('team')
        min_goals = int(request.args.get('min_goals', 3))
        
        if not team:
            return jsonify({'error': 'Team parameter required'}), 400
        
        matches = queries.query_1_high_scoring_matches(team, min_goals)
        
        result = {
            'team': team,
            'min_goals': min_goals,
            'total_matches': len(matches),
            'matches': matches[:20]  # Limit to 20 for response size
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/<team_name>/season/<season>')
def get_team_season_stats(team_name, season):
    """
    GET /api/team/<team_name>/season/<season>
    Get team statistics for a specific season
    """
    try:
        # Replace URL-friendly season format (2015/2016 becomes 2015-2016 in URL)
        season = season.replace('-', '/')
        
        record = queries.query_2_team_season_record(team_name, season)
        
        if not record:
            return jsonify({'error': 'No data found for team/season'}), 404
        
        return jsonify(record)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/top')
def get_top_players():
    """
    GET /api/players/top?league=<league_name>&limit=<number>
    Get top players by rating
    """
    try:
        league = request.args.get('league')
        limit = int(request.args.get('limit', 10))
        
        players = queries.query_3_top_players_by_rating(league, limit)
        
        result = {
            'league': league if league else 'All leagues',
            'limit': limit,
            'players': players
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leagues/stats')
def get_league_stats():
    """
    GET /api/leagues/stats
    Get statistics for all leagues
    """
    try:
        stats = queries.query_4_avg_goals_per_league()
        
        result = {
            'total_leagues': len(stats),
            'leagues': stats
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scorelines/common')
def get_common_scorelines():
    """
    GET /api/scorelines/common?limit=<number>
    Get most common scorelines
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        scorelines = queries.query_6_common_scorelines(limit)
        
        result = {
            'limit': limit,
            'scorelines': scorelines
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/league/<league_name>/standings')
def get_league_standings(league_name):
    """
    GET /api/league/<league_name>/standings?season=<season>
    Get complete league standings
    """
    try:
        season = request.args.get('season')
        
        if not season:
            return jsonify({'error': 'Season parameter required'}), 400
        
        standings = queries.query_8_league_standings(league_name, season)
        
        result = {
            'league_name': league_name,
            'season': season,
            'standings': standings
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/head-to-head')
def get_head_to_head():
    """
    GET /api/head-to-head?team1=<team1>&team2=<team2>
    Get head-to-head record between two teams
    """
    try:
        team1 = request.args.get('team1')
        team2 = request.args.get('team2')
        
        if not team1 or not team2:
            return jsonify({'error': 'Both team1 and team2 parameters required'}), 400
        
        record = queries.query_9_head_to_head(team1, team2)
        
        if not record:
            return jsonify({'error': 'No matches found between these teams'}), 404
        
        return jsonify(record)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/list')
def list_teams():
    """
    GET /api/teams/list
    List all teams in the database
    """
    try:
        teams = list(queries.db.teams.find(
            {},
            {'_id': 0, 'team_long_name': 1, 'team_short_name': 1}
        ).sort('team_long_name', 1))
        
        return jsonify({'total_teams': len(teams), 'teams': teams})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leagues/list')
def list_leagues():
    """
    GET /api/leagues/list
    List all leagues in the database
    """
    try:
        leagues = list(queries.db.leagues.find(
            {},
            {'_id': 0, 'name': 1, 'country_name': 1}
        ).sort('name', 1))
        
        return jsonify({'total_leagues': len(leagues), 'leagues': leagues})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
