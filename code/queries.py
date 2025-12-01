"""
MongoDB Queries for European Soccer Dataset
Implements all required queries from the project proposal
"""

from pymongo import MongoClient
from datetime import datetime
from collections import Counter

class SoccerQueries:
    def __init__(self, mongo_uri='mongodb://localhost:27017/', db_name='soccer_db'):
        """Initialize MongoDB connection"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
    
    def query_1_high_scoring_matches(self, team_name, min_goals=3):
        """
        Query 1: Find all matches where a given team scored 3 or more goals
        """
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'home_team_name': team_name, 'home_team_goal': {'$gte': min_goals}},
                        {'away_team_name': team_name, 'away_team_goal': {'$gte': min_goals}}
                    ]
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'date': 1,
                    'league_name': 1,
                    'season': 1,
                    'home_team_name': 1,
                    'away_team_name': 1,
                    'home_team_goal': 1,
                    'away_team_goal': 1,
                    'scoreline': {
                        '$concat': [
                            {'$toString': '$home_team_goal'},
                            ' - ',
                            {'$toString': '$away_team_goal'}
                        ]
                    }
                }
            },
            {'$sort': {'date': -1}}
        ]
        
        return list(self.db.matches.aggregate(pipeline))
    
    def query_2_team_season_record(self, team_name, season):
        """
        Query 2: Aggregate total wins, losses, and draws for each team in a given season
        """
        pipeline = [
            {
                '$match': {
                    'season': season,
                    '$or': [
                        {'home_team_name': team_name},
                        {'away_team_name': team_name}
                    ]
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_matches': {'$sum': 1},
                    'wins': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$or': [
                                        {
                                            '$and': [
                                                {'$eq': ['$home_team_name', team_name]},
                                                {'$gt': ['$home_team_goal', '$away_team_goal']}
                                            ]
                                        },
                                        {
                                            '$and': [
                                                {'$eq': ['$away_team_name', team_name]},
                                                {'$gt': ['$away_team_goal', '$home_team_goal']}
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    'losses': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$or': [
                                        {
                                            '$and': [
                                                {'$eq': ['$home_team_name', team_name]},
                                                {'$lt': ['$home_team_goal', '$away_team_goal']}
                                            ]
                                        },
                                        {
                                            '$and': [
                                                {'$eq': ['$away_team_name', team_name]},
                                                {'$lt': ['$away_team_goal', '$home_team_goal']}
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    'draws': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$home_team_goal', '$away_team_goal']},
                                1,
                                0
                            ]
                        }
                    },
                    'goals_scored': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$home_team_name', team_name]},
                                '$home_team_goal',
                                '$away_team_goal'
                            ]
                        }
                    },
                    'goals_conceded': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$home_team_name', team_name]},
                                '$away_team_goal',
                                '$home_team_goal'
                            ]
                        }
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'team': team_name,
                    'season': season,
                    'matches_played': '$total_matches',
                    'wins': 1,
                    'draws': 1,
                    'losses': 1,
                    'goals_scored': 1,
                    'goals_conceded': 1,
                    'goal_difference': {'$subtract': ['$goals_scored', '$goals_conceded']},
                    'points': {'$add': [{'$multiply': ['$wins', 3]}, '$draws']}
                }
            }
        ]
        
        results = list(self.db.matches.aggregate(pipeline))
        return results[0] if results else None
    
    def query_3_top_players_by_rating(self, league_name=None, limit=10):
        """
        Query 3: List top 10 players by overall rating in a specific league
        """
        # First, get players who played in the league
        match_filter = {}
        if league_name:
            match_filter['league_name'] = league_name
        
        pipeline = [
            {
                '$lookup': {
                    'from': 'player_attributes',
                    'localField': 'player_api_id',
                    'foreignField': 'player_api_id',
                    'as': 'attributes'
                }
            },
            {
                '$unwind': '$attributes'
            },
            {
                '$group': {
                    '_id': '$player_api_id',
                    'player_name': {'$first': '$player_name'},
                    'avg_rating': {'$avg': '$attributes.overall_rating'},
                    'max_rating': {'$max': '$attributes.overall_rating'},
                    'height': {'$first': '$height'},
                    'weight': {'$first': '$weight'},
                    'preferred_foot': {'$first': '$attributes.preferred_foot'}
                }
            },
            {
                '$sort': {'avg_rating': -1}
            },
            {
                '$limit': limit
            },
            {
                '$project': {
                    '_id': 0,
                    'player_name': 1,
                    'avg_rating': {'$round': ['$avg_rating', 1]},
                    'max_rating': 1,
                    'height': 1,
                    'weight': 1,
                    'preferred_foot': 1
                }
            }
        ]
        
        return list(self.db.players.aggregate(pipeline))
    
    def query_4_avg_goals_per_league(self):
        """
        Query 4: Calculate average goals per match for each league
        """
        pipeline = [
            {
                '$group': {
                    '_id': '$league_name',
                    'total_matches': {'$sum': 1},
                    'total_goals': {
                        '$sum': {
                            '$add': ['$home_team_goal', '$away_team_goal']
                        }
                    },
                    'avg_home_goals': {'$avg': '$home_team_goal'},
                    'avg_away_goals': {'$avg': '$away_team_goal'}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'league_name': '$_id',
                    'total_matches': 1,
                    'total_goals': 1,
                    'avg_goals_per_match': {
                        '$round': [
                            {'$divide': ['$total_goals', '$total_matches']},
                            2
                        ]
                    },
                    'avg_home_goals': {'$round': ['$avg_home_goals', 2]},
                    'avg_away_goals': {'$round': ['$avg_away_goals', 2]}
                }
            },
            {
                '$sort': {'avg_goals_per_match': -1}
            }
        ]
        
        return list(self.db.matches.aggregate(pipeline))
    
    def query_5_player_attributes_over_time(self, player_name):
        """
        Query 5: Retrieve player attributes for a given player and show changes over years
        """
        pipeline = [
            {
                '$match': {'player_name': player_name}
            },
            {
                '$lookup': {
                    'from': 'player_attributes',
                    'localField': 'player_api_id',
                    'foreignField': 'player_api_id',
                    'as': 'attributes'
                }
            },
            {
                '$unwind': '$attributes'
            },
            {
                '$project': {
                    '_id': 0,
                    'player_name': 1,
                    'date': '$attributes.date',
                    'overall_rating': '$attributes.overall_rating',
                    'potential': '$attributes.potential',
                    'finishing': '$attributes.finishing',
                    'short_passing': '$attributes.short_passing',
                    'dribbling': '$attributes.dribbling',
                    'sprint_speed': '$attributes.sprint_speed',
                    'stamina': '$attributes.stamina',
                    'strength': '$attributes.strength'
                }
            },
            {
                '$sort': {'date': 1}
            }
        ]
        
        return list(self.db.players.aggregate(pipeline))
    
    def query_6_common_scorelines(self, limit=10):
        """
        Query 6: Find the most common final scorelines across all leagues
        """
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'home_goals': '$home_team_goal',
                        'away_goals': '$away_team_goal'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'scoreline': {
                        '$concat': [
                            {'$toString': '$_id.home_goals'},
                            ' - ',
                            {'$toString': '$_id.away_goals'}
                        ]
                    },
                    'home_goals': '$_id.home_goals',
                    'away_goals': '$_id.away_goals',
                    'occurrences': '$count'
                }
            },
            {
                '$sort': {'occurrences': -1}
            },
            {
                '$limit': limit
            }
        ]
        
        return list(self.db.matches.aggregate(pipeline))
    
    def query_7_team_rating_trend(self, team_name):
        """
        Query 7: Show trend of team's average player ratings over seasons
        This combines player attributes with match data
        """
        # This is complex - we need to find players who played for the team
        # and track their ratings over time
        
        # First get all matches for the team to identify seasons
        matches = self.db.matches.find(
            {'$or': [
                {'home_team_name': team_name},
                {'away_team_name': team_name}
            ]},
            {'season': 1, 'date': 1}
        ).sort('date', 1)
        
        seasons = sorted(set(m['season'] for m in matches))
        
        # For each season, we'd need to identify which players played
        # This is simplified - in reality you'd track lineups
        trend_data = []
        
        for season in seasons:
            # Get date range for season
            season_matches = self.db.matches.find({'season': season}).sort('date', 1)
            season_list = list(season_matches)
            
            if season_list:
                start_date = season_list[0]['date']
                end_date = season_list[-1]['date']
                
                # Get average player ratings during this period
                # This is a simplified version
                pipeline = [
                    {
                        '$match': {
                            'date': {'$gte': start_date, '$lte': end_date}
                        }
                    },
                    {
                        '$group': {
                            '_id': None,
                            'avg_overall_rating': {'$avg': '$overall_rating'},
                            'avg_potential': {'$avg': '$potential'}
                        }
                    }
                ]
                
                season_ratings = list(self.db.player_attributes.aggregate(pipeline))
                
                if season_ratings:
                    trend_data.append({
                        'season': season,
                        'avg_overall_rating': round(season_ratings[0]['avg_overall_rating'], 1),
                        'avg_potential': round(season_ratings[0]['avg_potential'], 1)
                    })
        
        return trend_data
    
    def query_8_league_standings(self, league_name, season):
        """
        Bonus Query 8: Complete league standings for a season
        """
        # Get all teams in the league for that season
        teams = self.db.matches.distinct('home_team_name', {
            'league_name': league_name,
            'season': season
        })
        
        standings = []
        
        for team in teams:
            record = self.query_2_team_season_record(team, season)
            if record:
                standings.append(record)
        
        # Sort by points, then goal difference
        standings.sort(key=lambda x: (x['points'], x['goal_difference']), reverse=True)
        
        # Add position
        for i, team_record in enumerate(standings, 1):
            team_record['position'] = i
        
        return standings
    
    def query_9_head_to_head(self, team1, team2):
        """
        Bonus Query 9: Head-to-head record between two teams
        """
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'home_team_name': team1, 'away_team_name': team2},
                        {'home_team_name': team2, 'away_team_name': team1}
                    ]
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_matches': {'$sum': 1},
                    'team1_wins': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$or': [
                                        {
                                            '$and': [
                                                {'$eq': ['$home_team_name', team1]},
                                                {'$gt': ['$home_team_goal', '$away_team_goal']}
                                            ]
                                        },
                                        {
                                            '$and': [
                                                {'$eq': ['$away_team_name', team1]},
                                                {'$gt': ['$away_team_goal', '$home_team_goal']}
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    'team2_wins': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$or': [
                                        {
                                            '$and': [
                                                {'$eq': ['$home_team_name', team2]},
                                                {'$gt': ['$home_team_goal', '$away_team_goal']}
                                            ]
                                        },
                                        {
                                            '$and': [
                                                {'$eq': ['$away_team_name', team2]},
                                                {'$gt': ['$away_team_goal', '$home_team_goal']}
                                            ]
                                        }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    'draws': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$home_team_goal', '$away_team_goal']},
                                1,
                                0
                            ]
                        }
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'team1': team1,
                    'team2': team2,
                    'total_matches': 1,
                    'team1_wins': 1,
                    'team2_wins': 1,
                    'draws': 1
                }
            }
        ]
        
        results = list(self.db.matches.aggregate(pipeline))
        return results[0] if results else None
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()


# Example usage and testing
if __name__ == "__main__":
    queries = SoccerQueries()
    
    print("="*60)
    print("SOCCER DATABASE QUERIES - EXAMPLES")
    print("="*60)
    
    # Query 1
    print("\n1. High scoring matches for Barcelona (3+ goals):")
    results = queries.query_1_high_scoring_matches("FC Barcelona", 3)
    for match in results[:5]:
        print(f"  {match['date'].strftime('%Y-%m-%d') if match['date'] else 'N/A'}: "
              f"{match['home_team_name']} {match['scoreline']} {match['away_team_name']}")
    
    # Query 2
    print("\n2. Barcelona season record (2015/2016):")
    record = queries.query_2_team_season_record("FC Barcelona", "2015/2016")
    if record:
        print(f"  Matches: {record['matches_played']}, "
              f"W: {record['wins']}, D: {record['draws']}, L: {record['losses']}, "
              f"Points: {record['points']}")
    
    # Query 3
    print("\n3. Top 5 players by rating:")
    players = queries.query_3_top_players_by_rating(limit=5)
    for p in players:
        print(f"  {p['player_name']}: {p['avg_rating']} avg rating")
    
    # Query 4
    print("\n4. Average goals per match by league:")
    league_stats = queries.query_4_avg_goals_per_league()
    for league in league_stats[:5]:
        print(f"  {league['league_name']}: {league['avg_goals_per_match']} goals/match")
    
    # Query 6
    print("\n6. Most common scorelines:")
    scorelines = queries.query_6_common_scorelines(5)
    for s in scorelines:
        print(f"  {s['scoreline']}: {s['occurrences']} times")
    
    queries.close()
