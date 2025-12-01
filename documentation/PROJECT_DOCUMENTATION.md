# DS5760 Final Project Documentation
## European Soccer Insights with MongoDB

**Student:** Ziyi Tao
**Course:** DS5760 - NoSQL for Modern Data Science Applications  
**Semester:** Fall 2025
**Institution:** Vanderbilt University

---

## Executive Summary

This project implements a comprehensive NoSQL database application using MongoDB to analyze European soccer data from 2008-2016. The system includes data loading, query implementations, a REST API, and an interactive web dashboard for exploring match results, player statistics, and league standings across 11 European leagues.

**Key Features:**
- Complete data pipeline from SQLite to MongoDB
- 9+ complex MongoDB aggregation queries
- RESTful API with 13+ endpoints
- Interactive web dashboard with data visualization
- Comprehensive documentation and testing suite

---

## 1. Dataset Description

**Source:** Kaggle - European Soccer Database  
**URL:** https://www.kaggle.com/datasets/hugomathien/soccer

**Data Coverage:**
- **Time Period:** 2008-2016 (8 seasons)
- **Geographic Scope:** 11 European leagues
- **Volume:**
  - ~25,000 match records
  - 299 teams
  - 11,060 players
  - 183,000+ player attribute records
  - 11 leagues across 11 countries

**Original Format:** SQLite relational database

**Key Leagues Included:**
- Spain LIGA BBVA (La Liga)
- England Premier League
- Germany 1. Bundesliga
- Italy Serie A
- France Ligue 1
- Netherlands Eredivisie
- Belgium Jupiler League
- Portugal Liga ZON Sagres
- Poland Ekstraklasa
- Scotland Premier League
- Switzerland Super League

---

## 2. Data Curation Process

### 2.1 Extraction
The data loader (`data_loader.py`) connects to the SQLite database and extracts data from 7 main tables:
- Country
- League
- Team
- Player
- Match
- Player_Attributes
- Team_Attributes (optional)

### 2.2 Transformation

**Date Normalization:**
- Converted all date strings to ISO 8601 datetime objects
- Handled multiple date formats: `YYYY-MM-DD HH:MM:SS` and `YYYY-MM-DD`

**Data Denormalization:**
- Embedded team names directly in match documents for faster queries
- Added league and country names to matches
- Computed derived fields (e.g., match result: home_win/away_win/draw)

**Data Cleaning:**
- Removed records with NULL critical fields
- Unified team naming conventions
- Validated data integrity across collections

### 2.3 Loading

**Batch Processing:**
- Implemented batch inserts (1,000 records at a time) for efficiency
- Progress tracking for large collections
- Total load time: 2-5 minutes

**Index Creation:**
- Created single-field indexes on frequently queried fields
- Compound indexes for complex queries
- Unique indexes on API IDs

**Final MongoDB Schema:**
```
soccer_db/
├── countries (11 documents)
├── leagues (11 documents)
├── teams (299 documents)
├── players (11,060 documents)
├── matches (25,979 documents)
└── player_attributes (183,978 documents)
```

---

## 3. MongoDB as the Optimal Choice

### 3.1 Why MongoDB?

**1. Natural Data Hierarchy**
Soccer data has inherent hierarchical relationships:
- Leagues → Matches → Teams → Players
- MongoDB's document model naturally represents this structure

**2. Flexible Schema**
- Player attributes vary by position (goalkeepers vs. forwards)
- Match data includes optional fields
- Schema evolution is straightforward

**3. Powerful Aggregation Pipeline**
- Complex analytical queries (averages, rankings, trends)
- Multi-stage transformations
- Native support for grouping and statistical operations

**4. Horizontal Scalability**
- Can easily scale to accommodate:
  - More leagues and seasons
  - Real-time match updates
  - Additional player metrics

**5. Developer-Friendly**
- Excellent Python integration (PyMongo)
- JSON-like documents align with web APIs
- Rich query language

### 3.2 MongoDB vs Alternatives

**vs. Neo4j (Graph Database):**
- While team relationships exist, our primary use case is analytical queries, not relationship traversal
- MongoDB's aggregation pipeline is more suitable for statistical analysis

**vs. Cassandra:**
- Our access patterns favor complex queries over write-heavy workloads
- MongoDB provides more flexible querying without requiring predefined query patterns

**vs. Redis:**
- Need persistent, complex data structures
- Analytical queries require more than key-value storage

---

## 4. Query Implementations

### 4.1 Query 1: High Scoring Matches
**Purpose:** Find matches where a team scored a minimum number of goals

**MongoDB Pipeline:**
```javascript
[
  {
    $match: {
      $or: [
        {home_team_name: "FC Barcelona", home_team_goal: {$gte: 3}},
        {away_team_name: "FC Barcelona", away_team_goal: {$gte: 3}}
      ]
    }
  },
  {$sort: {date: -1}}
]
```

**Use Case:** Identify dominant performances, analyze scoring patterns

### 4.2 Query 2: Team Season Record
**Purpose:** Calculate comprehensive season statistics for a team

**Complexity:** High - requires conditional aggregations to determine:
- Wins (different logic for home vs. away)
- Losses
- Draws
- Goals scored/conceded
- Points (3 for win, 1 for draw)
- Goal difference

**Key Features:**
- Handles team playing both home and away
- Calculates league points
- Provides complete season summary

### 4.3 Query 3: Top Players by Rating
**Purpose:** Rank players by average overall rating

**Pipeline Stages:**
1. Lookup player attributes
2. Unwind attributes array
3. Group by player, calculate average
4. Sort by rating
5. Limit results

**Innovation:** Joins players with their historical attributes using $lookup

### 4.4 Query 4: League Statistics
**Purpose:** Compare goal-scoring trends across leagues

**Metrics:**
- Total matches
- Total goals
- Average goals per match
- Home vs. Away goal averages

**Insight:** Reveals which leagues are more attacking/defensive

### 4.5 Query 5: Player Attributes Over Time
**Purpose:** Track player development across seasons

**Application:** 
- Scout player improvement
- Analyze peak performance periods
- Study aging curves

### 4.6 Query 6: Common Scorelines
**Purpose:** Find most frequent final scores

**Finding:** Most common scoreline is typically 1-0 or 1-1

**Use Case:** Betting analytics, match prediction models

### 4.7 Query 7: Team Rating Trend
**Purpose:** Show how team quality changed over seasons

**Methodology:**
- Aggregate player ratings by season
- Track average rating evolution
- Identify rebuilding/peak periods

### 4.8 Bonus Query 8: League Standings
**Purpose:** Generate complete league table

**Features:**
- Calculates all teams in a league
- Computes points, goal difference
- Sorts by points (then GD)
- Assigns table positions

**Complexity:** Highest - calls Query 2 for each team, then aggregates

### 4.9 Bonus Query 9: Head-to-Head
**Purpose:** Compare historical record between two teams

**Statistics:**
- Total matches played
- Wins for each team
- Draws
- Overall head-to-head record

---

## 5. REST API Architecture

### 5.1 Framework Choice: Flask
**Rationale:**
- Lightweight and easy to extend
- Excellent Python integration
- Perfect for educational projects
- Built-in development server

### 5.2 API Design Principles

**RESTful Conventions:**
- Resource-based URLs (`/api/team/<name>`)
- HTTP methods (GET)
- JSON responses
- Proper status codes

**CORS Enabled:**
- Allows dashboard to call API from same origin
- Supports future frontend separation

**Error Handling:**
- Graceful error responses
- Descriptive error messages
- Proper HTTP status codes (404, 500)

### 5.3 Endpoint Categories

**Teams (3 endpoints):**
- Individual team information
- Season statistics
- Team listing

**Players (2 endpoints):**
- Individual player profiles
- Top player rankings

**Leagues (4 endpoints):**
- League listings
- League-wide statistics
- Standings
- Top teams

**Matches (3 endpoints):**
- High-scoring match filter
- Common scorelines
- Head-to-head comparisons

**Utility (1 endpoint):**
- API documentation

---

## 6. Web Dashboard

### 6.1 Architecture

**Frontend Stack:**
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for interactivity
- Chart.js for data visualization

**Design Philosophy:**
- Clean, modern interface
- Intuitive navigation with tabs
- Responsive design
- Interactive charts and tables

### 6.2 Features by Tab

**Overview:**
- Database statistics at a glance
- League comparison bar chart
- Most common scorelines table

**Teams:**
- Team search functionality
- Season performance analysis
- High-scoring match filter
- Head-to-head comparisons

**Players:**
- Top player rankings
- Individual player profiles
- Detailed attribute display

**Leagues:**
- Full league standings tables
- Top 5 teams display
- League-wide statistics

**API Documentation:**
- Embedded API reference
- Example usage
- Parameter documentation

### 6.3 User Experience Highlights

**Visual Feedback:**
- Loading indicators during API calls
- Success/error messages
- Smooth animations
- Color-coded elements (wins=green, losses=red)

**Data Visualization:**
- Bar charts for league comparisons
- Tables for standings and statistics
- Position badges (gold/silver/bronze)
- Goal difference indicators

---

## 7. Testing & Validation

### 7.1 Test Suite (`test_queries.py`)

**Coverage:**
- Database connectivity
- Collection data verification
- Individual query testing
- End-to-end validation

**Test Results Format:**
```
✓ MongoDB connection successful
✓ Query 1 (High Scoring Matches): Found 245 matches
✓ Query 2 (Team Season Record): 38W 0D 0L
✓ Query 3 (Top Players): Found 10 players
...
Test Results: 9 passed, 0 failed
```

### 7.2 Demo Script (`demo.py`)

**Purpose:** Showcase all queries with real data

**Features:**
- Formatted output
- Multiple examples per query
- Progress indicators
- Sample data display

---

## 8. Deployment Options

### 8.1 Local Development
```bash
python app.py
# Access: http://localhost:5001
```

### 8.2 Docker Deployment
```bash
docker-compose up -d
# MongoDB + Flask in containers
```

**Benefits:**
- Consistent environment
- Easy setup
- Isolated dependencies
- Production-ready

---

## 9. Performance Considerations

### 9.1 Indexing Strategy

**Single-Field Indexes:**
- `matches.league_name`
- `matches.season`
- `matches.home_team_name`
- `matches.away_team_name`
- `players.player_name`

**Compound Indexes:**
- `player_attributes(player_api_id, date)` - for time-series queries

**Unique Indexes:**
- All API IDs for referential integrity

### 9.2 Query Optimization

**Batch Processing:**
- Data loading in 1,000-record batches
- Reduces memory overhead

**Projection:**
- Only retrieve needed fields
- Reduces network transfer

**Aggregation Pipeline:**
- Server-side processing
- Leverages MongoDB's optimizations

---

## 10. Future Enhancements

### 10.1 Additional Features
1. **Real-time Updates:** WebSocket integration for live scores
2. **Machine Learning:** Predict match outcomes using historical data
3. **Advanced Analytics:** Player heatmaps, possession statistics
4. **User Accounts:** Save favorite teams, create custom dashboards
5. **Data Export:** CSV/Excel export functionality

### 10.2 Scalability Improvements
1. **Caching:** Redis for frequently accessed data
2. **Pagination:** API pagination for large result sets
3. **Search:** Full-text search for players/teams
4. **Sharding:** Horizontal scaling for larger datasets

### 10.3 Additional Data Sources
1. **Transfer Market:** Player valuations and transfers
2. **Injury Data:** Availability and fitness information
3. **Weather Data:** Match conditions
4. **Betting Odds:** Market predictions

---

## 11. Lessons Learned

### 11.1 Technical Insights

**MongoDB Strengths:**
- Aggregation pipeline is incredibly powerful
- Flexible schema adapts to data evolution
- Excellent for analytics workloads

**Challenges:**
- Complex joins require $lookup (less performant than SQL joins)
- Aggregation pipeline has learning curve
- Index management requires planning

### 11.2 Development Process

**Successes:**
- Modular code structure enables easy testing
- API-first design facilitates future extensions
- Comprehensive documentation aids understanding

**Improvements:**
- Earlier index planning would have helped
- More comprehensive error handling needed
- Automated testing could be expanded

---

## 12. GenAI Usage Disclosure

This project utilized GenAI assistance (Claude) for:

**Code Development:**
- MongoDB aggregation pipeline optimization
- Flask API endpoint structure
- Dashboard UI/UX implementation
- JavaScript async/await patterns

**Documentation:**
- README structure
- Code comments
- API documentation
- This project report

**All code and documentation has been:**
- Reviewed for correctness
- Tested with actual data
- Modified to fit project requirements
- Fully understood by the project author

**Learning Outcomes:**
Despite using GenAI assistance, I have developed deep understanding of:
- MongoDB document model and query language
- Aggregation pipeline design patterns
- Flask REST API architecture
- Frontend-backend integration
- NoSQL database design principles

---

## 13. Conclusion

This project successfully demonstrates the power of MongoDB for analytical applications in sports data. The combination of flexible schema design, powerful aggregation capabilities, and developer-friendly tooling makes MongoDB an excellent choice for this use case.

**Key Achievements:**
- Complete data pipeline from relational to document model
- 9+ complex analytical queries
- Production-ready REST API
- Interactive web dashboard
- Comprehensive testing and documentation

**Project Impact:**
The system provides valuable insights into European soccer from 2008-2016, enabling:
- Historical performance analysis
- Player development tracking
- League comparisons
- Team strategy insights

This project serves as a strong foundation for future sports analytics applications and demonstrates practical NoSQL database design principles applicable to various domains beyond soccer.

---

## 14. References

1. **Dataset Source:**
   - Mathien, H. (2016). European Soccer Database. Kaggle.
   - https://www.kaggle.com/datasets/hugomathien/soccer

2. **Technologies:**
   - MongoDB Documentation: https://docs.mongodb.com/
   - Flask Documentation: https://flask.palletsprojects.com/
   - PyMongo Documentation: https://pymongo.readthedocs.io/

3. **Course Materials:**
   - DS5760 NoSQL for Modern Data Science Applications
   - Vanderbilt University, Fall 2025

---

**Project Repository:** https://github.com/hibu-11/Soccer-database.git

**Contact:** ziyi.tao@vanderbilt.edu

---

*End of Documentation*
