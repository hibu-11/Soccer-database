"""
Test Script for Soccer Database Queries
Run this after loading data to verify everything works
"""

from queries import SoccerQueries
from pymongo import MongoClient
import sys

def test_database_connection():
    """Test MongoDB connection"""
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def test_collections():
    """Test that all collections have data"""
    try:
        queries = SoccerQueries()
        
        collections = {
            'countries': queries.db.countries.count_documents({}),
            'leagues': queries.db.leagues.count_documents({}),
            'teams': queries.db.teams.count_documents({}),
            'players': queries.db.players.count_documents({}),
            'matches': queries.db.matches.count_documents({}),
            'player_attributes': queries.db.player_attributes.count_documents({})
        }
        
        print("\nCollection Counts:")
        all_good = True
        for collection, count in collections.items():
            status = "✓" if count > 0 else "✗"
            print(f"  {status} {collection}: {count:,}")
            if count == 0:
                all_good = False
        
        queries.close()
        return all_good
    except Exception as e:
        print(f"✗ Collection test failed: {e}")
        return False

def test_query_1():
    """Test high scoring matches query"""
    try:
        queries = SoccerQueries()
        results = queries.query_1_high_scoring_matches("FC Barcelona", 3)
        queries.close()
        
        if len(results) > 0:
            print(f"✓ Query 1 (High Scoring Matches): Found {len(results)} matches")
            return True
        else:
            print("✗ Query 1: No results found (try different team name)")
            return False
    except Exception as e:
        print(f"✗ Query 1 failed: {e}")
        return False

def test_query_2():
    """Test team season record query"""
    try:
        queries = SoccerQueries()
        result = queries.query_2_team_season_record("FC Barcelona", "2015/2016")
        queries.close()
        
        if result:
            print(f"✓ Query 2 (Team Season Record): {result['wins']}W {result['draws']}D {result['losses']}L")
            return True
        else:
            print("✗ Query 2: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 2 failed: {e}")
        return False

def test_query_3():
    """Test top players query"""
    try:
        queries = SoccerQueries()
        results = queries.query_3_top_players_by_rating(limit=5)
        queries.close()
        
        if len(results) > 0:
            print(f"✓ Query 3 (Top Players): Found {len(results)} players")
            return True
        else:
            print("✗ Query 3: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 3 failed: {e}")
        return False

def test_query_4():
    """Test league statistics query"""
    try:
        queries = SoccerQueries()
        results = queries.query_4_avg_goals_per_league()
        queries.close()
        
        if len(results) > 0:
            print(f"✓ Query 4 (League Stats): Found {len(results)} leagues")
            return True
        else:
            print("✗ Query 4: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 4 failed: {e}")
        return False

def test_query_6():
    """Test common scorelines query"""
    try:
        queries = SoccerQueries()
        results = queries.query_6_common_scorelines(10)
        queries.close()
        
        if len(results) > 0:
            print(f"✓ Query 6 (Common Scorelines): Found {len(results)} scorelines")
            print(f"  Most common: {results[0]['scoreline']} ({results[0]['occurrences']} times)")
            return True
        else:
            print("✗ Query 6: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 6 failed: {e}")
        return False

def test_query_8():
    """Test league standings query"""
    try:
        queries = SoccerQueries()
        results = queries.query_8_league_standings("Spain LIGA BBVA", "2015/2016")
        queries.close()
        
        if len(results) > 0:
            print(f"✓ Query 8 (League Standings): Found {len(results)} teams")
            return True
        else:
            print("✗ Query 8: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 8 failed: {e}")
        return False

def test_query_9():
    """Test head-to-head query"""
    try:
        queries = SoccerQueries()
        result = queries.query_9_head_to_head("FC Barcelona", "Real Madrid CF")
        queries.close()
        
        if result:
            print(f"✓ Query 9 (Head-to-Head): {result['team1_wins']} - {result['draws']} - {result['team2_wins']}")
            return True
        else:
            print("✗ Query 9: No results found")
            return False
    except Exception as e:
        print(f"✗ Query 9 failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("SOCCER DATABASE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Collections Data", test_collections),
        ("Query 1: High Scoring Matches", test_query_1),
        ("Query 2: Team Season Record", test_query_2),
        ("Query 3: Top Players", test_query_3),
        ("Query 4: League Statistics", test_query_4),
        ("Query 6: Common Scorelines", test_query_6),
        ("Query 8: League Standings", test_query_8),
        ("Query 9: Head-to-Head", test_query_9),
    ]
    
    print("\nRunning Tests...")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            failed += 1
    
    print("-" * 60)
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your database is ready to use.")
        print("\nNext steps:")
        print("  1. Run the Flask app: python app.py")
        print("  2. Open http://localhost:5000 in your browser")
        print("  3. Explore the dashboard!")
    else:
        print("\n⚠️  Some tests failed. Please check:")
        print("  1. MongoDB is running")
        print("  2. Data was loaded successfully (python data_loader.py)")
        print("  3. Collection names and indexes are correct")
    
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
