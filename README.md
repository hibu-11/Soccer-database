# European Soccer Insights with MongoDB

A comprehensive NoSQL database project analyzing European soccer data (2008-2016) from 11 leagues using MongoDB and Flask.

### Prerequisites

- Python 3.8+
- MongoDB installed and running locally (default port: 27017)
- European Soccer Database SQLite file from Kaggle

### Installation

1. **Clone or download this project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset**
   - Visit: https://www.kaggle.com/datasets/hugomathien/soccer
   - Download the SQLite database file (`database.sqlite`)
   - Place it in the `data/` folder

4. **Start MongoDB** (use the docker)
   ```bash
   docker-compose up -d
   ```

5. **Load data into MongoDB**
   ```bash
   python data_loader.py data/database.sqlite
   ```
   
   This will:
   - Connect to your SQLite database
   - Extract all data (countries, leagues, teams, players, matches, player attributes)
   - Transform and load into MongoDB
   - Create appropriate indexes
   - Takes 2-5 minutes depending on your system

6. **Start the Flask application**
   ```bash
   python app.py
   ```

7. **Access the dashboard**
   - Open your browser to: http://localhost:5001
   - Explore the interactive dashboard!

## Implemented Queries

All queries from the project proposal are implemented:

### Query 1: High Scoring Matches
Find all matches where a team scored 3+ goals
```python
queries.query_1_high_scoring_matches("FC Barcelona", min_goals=3)
```
**Endpoint:** `GET /api/matches/high-scoring?team=FC Barcelona&min_goals=3`

### Query 2: Team Season Record
Calculate wins, losses, draws, goals, and points for a team in a season
```python
queries.query_2_team_season_record("FC Barcelona", "2015/2016")
```
**Endpoint:** `GET /api/team/FC Barcelona/season/2015-2016`

### Query 3: Top Players by Rating
List top N players by overall rating
```python
queries.query_3_top_players_by_rating(league_name="Spain LIGA BBVA", limit=10)
```
**Endpoint:** `GET /api/players/top?league=Spain LIGA BBVA&limit=10`

### Query 4: League Goal Statistics
Calculate average goals per match for each league
```python
queries.query_4_avg_goals_per_league()
```
**Endpoint:** `GET /api/leagues/stats`

### Query 5: Player Attributes Over Time
Track how a player's attributes changed over the years
```python
queries.query_5_player_attributes_over_time("Lionel Messi")
```
**Endpoint:** `GET /api/player/Lionel Messi` (includes attribute history count)

### Query 6: Common Scorelines
Find the most frequent final scores across all matches
```python
queries.query_6_common_scorelines(limit=10)
```
**Endpoint:** `GET /api/scorelines/common?limit=10`

### Query 7: Team Rating Trend
Show trend of average player ratings over seasons
```python
queries.query_7_team_rating_trend("FC Barcelona")
```

### Bonus Query 8: League Standings
Complete league table with positions, points, goal difference
```python
queries.query_8_league_standings("Spain LIGA BBVA", "2015/2016")
```
**Endpoint:** `GET /api/league/Spain LIGA BBVA/standings?season=2015/2016`

### Bonus Query 9: Head-to-Head
Compare two teams' historical record against each other
```python
queries.query_9_head_to_head("FC Barcelona", "Real Madrid CF")
```
**Endpoint:** `GET /api/head-to-head?team1=FC Barcelona&team2=Real Madrid CF`

## REST API Endpoints

### Teams
- `GET /api/team/<team_name>` - Get team info and recent matches
- `GET /api/team/<team_name>/season/<season>` - Get season statistics
- `GET /api/teams/list` - List all teams

### Players
- `GET /api/player/<player_name>` - Get player stats and attributes
- `GET /api/players/top?limit=N` - Get top N players by rating

### Leagues
- `GET /api/leagues/list` - List all leagues
- `GET /api/leagues/stats` - Get statistics for all leagues
- `GET /api/league/<league_name>/standings?season=<season>` - Get league standings
- `GET /api/league/<league_name>/top-teams?season=<season>` - Get top 5 teams

### Matches
- `GET /api/matches/high-scoring?team=<name>&min_goals=N` - Find high-scoring matches
- `GET /api/head-to-head?team1=<name>&team2=<name>` - Head-to-head record

### Other
- `GET /api/scorelines/common?limit=N` - Most common scorelines
- `GET /api/info` - API documentation

## Dashboard Features

The Flask web dashboard provides:

1. **Overview Tab**
   - Database statistics
   - League comparison charts
   - Common scorelines visualization

2. **Teams Tab**
   - Team search and information
   - Season statistics
   - High-scoring matches filter
   - Head-to-head comparisons

3. **Players Tab**
   - Top players rankings
   - Player profile search
   - Detailed attribute display

4. **Leagues Tab**
   - Full league standings
   - Top teams by season
   - League-wide statistics

5. **API Documentation Tab**
   - Complete endpoint reference
   - Example usage
   - Parameter documentation

## Database Schema

### MongoDB Collections

**countries**
- country_id, name

**leagues**
- league_id, country_id, name, country_name

**teams**
- team_api_id, team_fifa_api_id, team_long_name, team_short_name

**players**
- player_api_id, player_fifa_api_id, player_name, birthday, height, weight

**matches**
- match_api_id, country_id, league_id, season, stage, date
- home_team_api_id, home_team_name, home_team_goal
- away_team_api_id, away_team_name, away_team_goal
- result (home_win/away_win/draw)

**player_attributes**
- player_api_id, date
- overall_rating, potential, preferred_foot
- 30+ skill attributes (finishing, dribbling, speed, etc.)

### Indexes

All collections have optimized indexes:
- `teams`: team_api_id (unique), team_long_name, team_short_name
- `matches`: match_api_id (unique), league_name, season, team names, date
- `players`: player_api_id (unique), player_name
- `player_attributes`: player_api_id, date, composite (player_api_id, date)

## Use Cases

1. **Sports Analytics**: Analyze team performance trends over seasons
2. **Player Scouting**: Identify top players and track attribute development
3. **Betting Insights**: Find patterns in scorelines and team matchups
4. **League Comparisons**: Compare goal-scoring trends across European leagues
5. **Historical Research**: Access detailed match data from 2008-2016

## Customization

### Modify Queries
Edit `queries.py` to add custom queries or modify existing ones.

### Add API Endpoints
Add new routes in `app.py` following the existing pattern.

### Customize Dashboard
- Edit `templates/index.html` for layout changes
- Modify `static/css/style.css` for styling
- Update `static/js/main.js` for new interactions

## Example API Usage with Python

```python
import requests

# Get top players
response = requests.get('http://localhost:5000/api/players/top?limit=5')
players = response.json()

# Get team season stats
response = requests.get('http://localhost:5000/api/team/FC Barcelona/season/2015-2016')
stats = response.json()
print(f"Barcelona 2015/16: {stats['wins']}W {stats['draws']}D {stats['losses']}L")

# Get league standings
response = requests.get('http://localhost:5000/api/league/Spain LIGA BBVA/standings?season=2015/2016')
standings = response.json()
for team in standings['standings'][:5]:
    print(f"{team['position']}. {team['team']}: {team['points']} pts")
```

## Testing Queries Standalone

You can test queries without running the Flask app:

```bash
python queries.py
```

This will run example queries and display results in the terminal.

## Sample Teams and Players

**Popular Teams:**
- FC Barcelona
- Real Madrid CF
- Manchester United
- Bayern Munich
- Chelsea
- Arsenal
- Liverpool
- Juventus
- Paris Saint-Germain

**Notable Players:**
- Lionel Messi
- Cristiano Ronaldo
- Neymar
- Wayne Rooney
- Zlatan Ibrahimović

## Configuration

Default MongoDB connection:
- URI: `mongodb://localhost:27017/`
- Database: `soccer_db`

To change these, edit the connection strings in:
- `data_loader.py` (for data loading)
- `queries.py` (for query execution)
- `app.py` (for Flask app)

## Troubleshooting

**MongoDB Connection Error:**
```
Make sure MongoDB is running:
- Linux/Mac: mongod
- Windows: Check Services for MongoDB
```

**Data Loading Issues:**
```
Ensure the SQLite file path is correct
Check that you have enough disk space (database is ~350MB)
```

**Missing Data in Queries:**
```
Verify data was loaded: check MongoDB Compass or use mongo shell
Run: db.matches.countDocuments() to verify data exists
```

**Port Already in Use:**
```
Change Flask port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

## Technologies Used

- **Database**: MongoDB (NoSQL document database)
- **Backend**: Python, Flask, PyMongo
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Visualization**: Chart.js
- **Data Source**: SQLite (converted to MongoDB)

## Academic Integrity

This project was completed for DS5760 NoSQL for Modern Data Science Applications at Vanderbilt University.

**GenAI Usage Disclosure**: This project implementation utilized GenAI assistance (Claude) for:
- Code structure and optimization
- MongoDB query formulation
- Flask API endpoint design
- Dashboard UI/UX implementation
- Documentation and comments

All code has been reviewed, tested, and understood by the project author.

## License

This project is for educational purposes as part of DS5760 coursework.
Dataset source: https://www.kaggle.com/datasets/hugomathien/soccer

## Acknowledgments

- Dataset: Hugo Mathien (Kaggle)
- Course: DS5760 NoSQL for Modern Data Science Applications
- Institution: Vanderbilt University

---

**Project by**: Ziyi Tao
**Course**: DS5760 - NoSQL for Modern Data Science Applications  
**Term**: Fall 2025
