"""
Demo Script - Showcase All Queries
Run this to see all queries in action with sample data
"""

from queries import SoccerQueries
import json
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_subsection(title):
    """Print a formatted subsection"""
    print(f"\n--- {title} ---")

def demo_query_1():
    """Demo: High Scoring Matches"""
    print_section("Query 1: High Scoring Matches")
    
    queries = SoccerQueries()
    
    # Try different teams
    teams = ["FC Barcelona", "Real Madrid CF", "Bayern Munich"]
    
    for team in teams:
        results = queries.query_1_high_scoring_matches(team, 4)
        print(f"\n{team} matches with 4+ goals: {len(results)}")
        
        if results:
            print("Sample matches:")
            for match in results[:3]:
                date = match['date'].strftime('%Y-%m-%d') if match['date'] else 'N/A'
                print(f"  {date}: {match['home_team_name']} {match['scoreline']} {match['away_team_name']}")
    
    queries.close()

def demo_query_2():
    """Demo: Team Season Records"""
    print_section("Query 2: Team Season Records")
    
    queries = SoccerQueries()
    
    teams = [
        ("FC Barcelona", "2015/2016"),
        ("Real Madrid CF", "2015/2016"),
        ("Manchester United", "2015/2016")
    ]
    
    for team, season in teams:
        record = queries.query_2_team_season_record(team, season)
        if record:
            print(f"\n{team} ({season}):")
            print(f"  Record: {record['wins']}W-{record['draws']}D-{record['losses']}L")
            print(f"  Goals: {record['goals_scored']} for, {record['goals_conceded']} against")
            print(f"  Points: {record['points']}")
            print(f"  Goal Difference: {record['goal_difference']:+d}")
    
    queries.close()

def demo_query_3():
    """Demo: Top Players"""
    print_section("Query 3: Top Players by Rating")
    
    queries = SoccerQueries()
    
    # Overall top players
    print_subsection("Top 10 Players Overall")
    players = queries.query_3_top_players_by_rating(limit=10)
    
    for i, player in enumerate(players, 1):
        print(f"{i:2d}. {player['player_name']:25s} - Rating: {player['avg_rating']} "
              f"(Max: {player['max_rating']}) - {player['preferred_foot'] or 'N/A'} footed")
    
    queries.close()

def demo_query_4():
    """Demo: League Statistics"""
    print_section("Query 4: Average Goals per League")
    
    queries = SoccerQueries()
    
    stats = queries.query_4_avg_goals_per_league()
    
    print(f"\n{'League':<30} {'Matches':>8} {'Avg Goals':>10} {'Home':>6} {'Away':>6}")
    print("-" * 70)
    
    for league in stats:
        print(f"{league['league_name']:<30} {league['total_matches']:>8} "
              f"{league['avg_goals_per_match']:>10.2f} "
              f"{league['avg_home_goals']:>6.2f} {league['avg_away_goals']:>6.2f}")
    
    queries.close()

def demo_query_5():
    """Demo: Player Attributes Over Time"""
    print_section("Query 5: Player Attributes Over Time")
    
    queries = SoccerQueries()
    
    players_to_check = ["Lionel Messi", "Cristiano Ronaldo"]
    
    for player_name in players_to_check:
        print_subsection(f"{player_name}")
        
        attrs = queries.query_5_player_attributes_over_time(player_name)
        
        if attrs:
            print(f"Total attribute records: {len(attrs)}")
            print("\nSample progression (first 5 and last 5):")
            
            print(f"\n{'Date':<12} {'Overall':>7} {'Potential':>9} {'Finishing':>9} {'Speed':>7}")
            print("-" * 50)
            
            # Show first 5
            for attr in attrs[:5]:
                date = attr['date'].strftime('%Y-%m-%d') if attr['date'] else 'N/A'
                print(f"{date:<12} {attr['overall_rating']:>7} {attr['potential']:>9} "
                      f"{attr['finishing'] or 'N/A':>9} {attr['sprint_speed'] or 'N/A':>7}")
            
            if len(attrs) > 10:
                print("...")
                # Show last 5
                for attr in attrs[-5:]:
                    date = attr['date'].strftime('%Y-%m-%d') if attr['date'] else 'N/A'
                    print(f"{date:<12} {attr['overall_rating']:>7} {attr['potential']:>9} "
                          f"{attr['finishing'] or 'N/A':>9} {attr['sprint_speed'] or 'N/A':>7}")
    
    queries.close()

def demo_query_6():
    """Demo: Common Scorelines"""
    print_section("Query 6: Most Common Scorelines")
    
    queries = SoccerQueries()
    
    scorelines = queries.query_6_common_scorelines(15)
    
    print(f"\n{'Rank':<6} {'Scoreline':<12} {'Occurrences':>12}")
    print("-" * 35)
    
    for i, score in enumerate(scorelines, 1):
        print(f"{i:<6} {score['scoreline']:<12} {score['occurrences']:>12}")
    
    queries.close()

def demo_query_8():
    """Demo: League Standings"""
    print_section("Query 8: League Standings")
    
    queries = SoccerQueries()
    
    leagues = [
        ("Spain LIGA BBVA", "2015/2016"),
        ("England Premier League", "2015/2016")
    ]
    
    for league_name, season in leagues:
        print_subsection(f"{league_name} - {season}")
        
        standings = queries.query_8_league_standings(league_name, season)
        
        if standings:
            print(f"\n{'Pos':<4} {'Team':<25} {'Pts':>4} {'W':>3} {'D':>3} {'L':>3} "
                  f"{'GF':>4} {'GA':>4} {'GD':>5}")
            print("-" * 70)
            
            for team in standings[:10]:  # Top 10
                print(f"{team['position']:<4} {team['team']:<25} {team['points']:>4} "
                      f"{team['wins']:>3} {team['draws']:>3} {team['losses']:>3} "
                      f"{team['goals_scored']:>4} {team['goals_conceded']:>4} "
                      f"{team['goal_difference']:>+5}")
    
    queries.close()

def demo_query_9():
    """Demo: Head-to-Head"""
    print_section("Query 9: Head-to-Head Records")
    
    queries = SoccerQueries()
    
    matchups = [
        ("FC Barcelona", "Real Madrid CF"),
        ("Manchester United", "Manchester City"),
        ("Bayern Munich", "Borussia Dortmund")
    ]
    
    for team1, team2 in matchups:
        record = queries.query_9_head_to_head(team1, team2)
        
        if record:
            print(f"\n{team1} vs {team2}:")
            print(f"  Total Matches: {record['total_matches']}")
            print(f"  {team1}: {record['team1_wins']} wins")
            print(f"  Draws: {record['draws']}")
            print(f"  {team2}: {record['team2_wins']} wins")
    
    queries.close()

def run_all_demos():
    """Run all demo queries"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "EUROPEAN SOCCER DATABASE DEMO" + " "*24 + "║")
    print("║" + " "*20 + "All Queries in Action" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    
    demos = [
        demo_query_1,
        demo_query_2,
        demo_query_3,
        demo_query_4,
        demo_query_5,
        demo_query_6,
        demo_query_8,
        demo_query_9
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error in {demo.__name__}: {e}")
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("\nNext steps:")
    print("  • Start the Flask app: python app.py")
    print("  • Visit http://localhost:5000 for the interactive dashboard")
    print("  • Import Soccer_API.postman_collection.json into Postman for API testing")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_demos()
