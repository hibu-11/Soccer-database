// Main JavaScript for Soccer Dashboard

const API_BASE = window.location.origin;
let leagueChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadOverviewStats();
});

// Tab switching
function openTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-button');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Load overview statistics
async function loadOverviewStats() {
    try {
        // This would ideally come from a dedicated endpoint
        // For now, we'll load individual stats
        
        const leaguesResp = await fetch(`${API_BASE}/api/leagues/list`);
        const leaguesData = await leaguesResp.json();
        document.getElementById('total-leagues').textContent = leaguesData.total_leagues;
        
        const teamsResp = await fetch(`${API_BASE}/api/teams/list`);
        const teamsData = await teamsResp.json();
        document.getElementById('total-teams').textContent = teamsData.total_teams;
        
        // Set a placeholder for matches (would need dedicated endpoint)
        document.getElementById('total-matches').textContent = '25,000+';
        
    } catch (error) {
        console.error('Error loading overview stats:', error);
    }
}

// Load league statistics
async function loadLeagueStats() {
    const container = document.getElementById('league-stats-table');
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/leagues/stats`);
        const data = await response.json();
        
        if (data.leagues && data.leagues.length > 0) {
            // Create table
            let html = '<table><thead><tr>';
            html += '<th>League</th>';
            html += '<th>Matches</th>';
            html += '<th>Avg Goals/Match</th>';
            html += '<th>Avg Home Goals</th>';
            html += '<th>Avg Away Goals</th>';
            html += '</tr></thead><tbody>';
            
            data.leagues.forEach(league => {
                html += '<tr>';
                html += `<td><strong>${league.league_name}</strong></td>`;
                html += `<td>${league.total_matches}</td>`;
                html += `<td>${league.avg_goals_per_match}</td>`;
                html += `<td>${league.avg_home_goals}</td>`;
                html += `<td>${league.avg_away_goals}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
            
            // Create chart
            createLeagueChart(data.leagues);
        } else {
            container.innerHTML = '<p class="error">No league data found</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Create league statistics chart
function createLeagueChart(leagues) {
    const ctx = document.getElementById('leagueChart');
    
    if (leagueChart) {
        leagueChart.destroy();
    }
    
    const labels = leagues.map(l => l.league_name.split(' ').slice(0, 2).join(' '));
    const avgGoals = leagues.map(l => l.avg_goals_per_match);
    
    leagueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Goals per Match',
                data: avgGoals,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Goals per Match'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Load common scorelines
async function loadScorelines() {
    const container = document.getElementById('scorelines-results');
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/scorelines/common?limit=15`);
        const data = await response.json();
        
        if (data.scorelines && data.scorelines.length > 0) {
            let html = '<table><thead><tr>';
            html += '<th>Rank</th><th>Scoreline</th><th>Occurrences</th>';
            html += '</tr></thead><tbody>';
            
            data.scorelines.forEach((score, index) => {
                html += '<tr>';
                html += `<td>${index + 1}</td>`;
                html += `<td><strong>${score.scoreline}</strong></td>`;
                html += `<td>${score.occurrences}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="error">No scoreline data found</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Search team
async function searchTeam() {
    const teamName = document.getElementById('team-name').value.trim();
    const container = document.getElementById('team-results');
    
    if (!teamName) {
        container.innerHTML = '<p class="error">Please enter a team name</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/team/${encodeURIComponent(teamName)}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = '<div class="info-box">';
        html += `<h3>${data.team_name}</h3>`;
        html += `<p><strong>Short Name:</strong> ${data.team_info.short_name || 'N/A'}</p>`;
        html += `<p><strong>Total Matches:</strong> ${data.statistics.total_matches}</p>`;
        html += `<p><strong>Total Goals Scored:</strong> ${data.statistics.total_goals_scored}</p>`;
        html += '</div>';
        
        if (data.recent_matches && data.recent_matches.length > 0) {
            html += '<h3 style="margin-top: 20px;">Recent Matches</h3>';
            
            data.recent_matches.forEach(match => {
                const date = match.date ? new Date(match.date).toLocaleDateString() : 'N/A';
                html += '<div class="match-card">';
                html += `<div class="match-date">${date} - ${match.league_name} (${match.season})</div>`;
                html += `<div class="match-score">${match.home_team_name} ${match.home_team_goal} - ${match.away_team_goal} ${match.away_team_name}</div>`;
                html += '</div>';
            });
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get season statistics
async function getSeasonStats() {
    const teamName = document.getElementById('season-team-name').value.trim();
    const season = document.getElementById('season-select').value;
    const container = document.getElementById('season-stats-results');
    
    if (!teamName) {
        container.innerHTML = '<p class="error">Please enter a team name</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const seasonUrl = season.replace('/', '-');
        const response = await fetch(`${API_BASE}/api/team/${encodeURIComponent(teamName)}/season/${seasonUrl}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = '<div class="stats-grid">';
        html += `<div class="stat-card"><div class="stat-value">${data.matches_played}</div><div class="stat-label">Matches</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.wins}</div><div class="stat-label">Wins</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.draws}</div><div class="stat-label">Draws</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.losses}</div><div class="stat-label">Losses</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.points}</div><div class="stat-label">Points</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.goals_scored}</div><div class="stat-label">Goals For</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.goals_conceded}</div><div class="stat-label">Goals Against</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.goal_difference > 0 ? '+' : ''}${data.goal_difference}</div><div class="stat-label">Goal Diff</div></div>`;
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get high scoring matches
async function getHighScoringMatches() {
    const teamName = document.getElementById('high-score-team').value.trim();
    const minGoals = document.getElementById('min-goals').value;
    const container = document.getElementById('high-score-results');
    
    if (!teamName) {
        container.innerHTML = '<p class="error">Please enter a team name</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/matches/high-scoring?team=${encodeURIComponent(teamName)}&min_goals=${minGoals}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = `<p class="success">Found ${data.total_matches} matches where ${teamName} scored ${minGoals}+ goals</p>`;
        
        if (data.matches && data.matches.length > 0) {
            data.matches.forEach(match => {
                const date = match.date ? new Date(match.date).toLocaleDateString() : 'N/A';
                html += '<div class="match-card">';
                html += `<div class="match-date">${date} - ${match.league_name}</div>`;
                html += `<div class="match-score">${match.home_team_name} ${match.home_team_goal} - ${match.away_team_goal} ${match.away_team_name}</div>`;
                html += '</div>';
            });
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get head-to-head
async function getHeadToHead() {
    const team1 = document.getElementById('h2h-team1').value.trim();
    const team2 = document.getElementById('h2h-team2').value.trim();
    const container = document.getElementById('h2h-results');
    
    if (!team1 || !team2) {
        container.innerHTML = '<p class="error">Please enter both team names</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/head-to-head?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = '<div class="stats-grid">';
        html += `<div class="stat-card"><div class="stat-value">${data.total_matches}</div><div class="stat-label">Total Matches</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.team1_wins}</div><div class="stat-label">${team1} Wins</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.draws}</div><div class="stat-label">Draws</div></div>`;
        html += `<div class="stat-card"><div class="stat-value">${data.team2_wins}</div><div class="stat-label">${team2} Wins</div></div>`;
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get top players
async function getTopPlayers() {
    const limit = document.getElementById('player-limit').value;
    const container = document.getElementById('top-players-results');
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/players/top?limit=${limit}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = '';
        
        if (data.players && data.players.length > 0) {
            data.players.forEach((player, index) => {
                html += '<div class="player-card">';
                html += `<div class="player-rank">#${index + 1}</div>`;
                html += '<div class="player-info">';
                html += `<div class="player-name">${player.player_name}</div>`;
                html += `<div class="player-stats">`;
                html += `Height: ${player.height || 'N/A'} cm | `;
                html += `Weight: ${player.weight || 'N/A'} kg | `;
                html += `Foot: ${player.preferred_foot || 'N/A'}`;
                html += `</div></div>`;
                html += `<div class="player-rating">${player.avg_rating}</div>`;
                html += '</div>';
            });
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Search player
async function searchPlayer() {
    const playerName = document.getElementById('player-name').value.trim();
    const container = document.getElementById('player-results');
    
    if (!playerName) {
        container.innerHTML = '<p class="error">Please enter a player name</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/player/${encodeURIComponent(playerName)}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        let html = '<div class="info-box">';
        html += `<h3>${data.player_name}</h3>`;
        
        if (data.basic_info.birthday) {
            const birthday = new Date(data.basic_info.birthday);
            html += `<p><strong>Birthday:</strong> ${birthday.toLocaleDateString()}</p>`;
        }
        
        html += `<p><strong>Height:</strong> ${data.basic_info.height || 'N/A'} cm</p>`;
        html += `<p><strong>Weight:</strong> ${data.basic_info.weight || 'N/A'} kg</p>`;
        html += '</div>';
        
        if (data.current_attributes) {
            html += '<h3 style="margin-top: 20px;">Current Attributes</h3>';
            html += '<div class="stats-grid">';
            html += `<div class="stat-card"><div class="stat-value">${data.current_attributes.overall_rating || 'N/A'}</div><div class="stat-label">Overall</div></div>`;
            html += `<div class="stat-card"><div class="stat-value">${data.current_attributes.potential || 'N/A'}</div><div class="stat-label">Potential</div></div>`;
            html += `<div class="stat-card"><div class="stat-value">${data.current_attributes.finishing || 'N/A'}</div><div class="stat-label">Finishing</div></div>`;
            html += `<div class="stat-card"><div class="stat-value">${data.current_attributes.dribbling || 'N/A'}</div><div class="stat-label">Dribbling</div></div>`;
            html += `<div class="stat-card"><div class="stat-value">${data.current_attributes.sprint_speed || 'N/A'}</div><div class="stat-label">Speed</div></div>`;
            html += '</div>';
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get league standings
async function getStandings() {
    const leagueName = document.getElementById('league-name').value;
    const season = document.getElementById('standings-season').value;
    const container = document.getElementById('standings-results');
    
    if (!leagueName) {
        container.innerHTML = '<p class="error">Please select a league</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/league/${encodeURIComponent(leagueName)}/standings?season=${season}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        if (data.standings && data.standings.length > 0) {
            let html = '<table><thead><tr>';
            html += '<th>Pos</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th>';
            html += '<th>GF</th><th>GA</th><th>GD</th><th>Pts</th>';
            html += '</tr></thead><tbody>';
            
            data.standings.forEach(team => {
                let posClass = 'position-badge ';
                if (team.position === 1) posClass += 'position-1';
                else if (team.position === 2) posClass += 'position-2';
                else if (team.position === 3) posClass += 'position-3';
                else if (team.position <= 4) posClass += 'position-top4';
                else if (team.position >= data.standings.length - 2) posClass += 'position-bottom';
                
                html += '<tr>';
                html += `<td><span class="${posClass}">${team.position}</span></td>`;
                html += `<td><strong>${team.team}</strong></td>`;
                html += `<td>${team.matches_played}</td>`;
                html += `<td>${team.wins}</td>`;
                html += `<td>${team.draws}</td>`;
                html += `<td>${team.losses}</td>`;
                html += `<td>${team.goals_scored}</td>`;
                html += `<td>${team.goals_conceded}</td>`;
                html += `<td>${team.goal_difference > 0 ? '+' : ''}${team.goal_difference}</td>`;
                html += `<td><strong>${team.points}</strong></td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="error">No standings data found</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Get top teams
async function getTopTeams() {
    const leagueName = document.getElementById('top-teams-league').value;
    const season = document.getElementById('top-teams-season').value;
    const container = document.getElementById('top-teams-results');
    
    if (!leagueName) {
        container.innerHTML = '<p class="error">Please select a league</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/league/${encodeURIComponent(leagueName)}/top-teams?season=${season}`);
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        if (data.top_teams && data.top_teams.length > 0) {
            let html = '<table><thead><tr>';
            html += '<th>Pos</th><th>Team</th><th>Points</th><th>GD</th><th>W-D-L</th>';
            html += '</tr></thead><tbody>';
            
            data.top_teams.forEach(team => {
                html += '<tr>';
                html += `<td><span class="position-badge position-${team.position}">${team.position}</span></td>`;
                html += `<td><strong>${team.team}</strong></td>`;
                html += `<td><strong>${team.points}</strong></td>`;
                html += `<td>${team.goal_difference > 0 ? '+' : ''}${team.goal_difference}</td>`;
                html += `<td>${team.wins}-${team.draws}-${team.losses}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="error">No data found</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Load full API documentation
async function loadAPIInfo() {
    const container = document.getElementById('api-docs');
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/info`);
        const data = await response.json();
        
        let html = '<h3>All Available Endpoints</h3>';
        
        if (data.endpoints) {
            data.endpoints.forEach(endpoint => {
                html += '<div class="api-endpoint">';
                html += `<h4>${endpoint.method} ${endpoint.path}</h4>`;
                html += `<p>${endpoint.description}</p>`;
                if (endpoint.parameters) {
                    html += `<p><strong>Parameters:</strong> ${endpoint.parameters}</p>`;
                }
                html += `<code>${endpoint.example}</code>`;
                html += '</div>';
            });
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}
