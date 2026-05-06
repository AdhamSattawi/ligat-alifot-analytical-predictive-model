import pandas as pd
import numpy as np

df = pd.read_csv("israel_league_FULL_2010_2025.csv")

df[['Home_Goals', 'Away_Goals']] = df['Score'].str.split(':', expand=True).astype(float)
df['Date'] = df['Date'].astype(str).str.strip()

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, format='mixed')
df = df.sort_values(['Season', 'Date'])  


conditions = [
    (df['Home_Goals'] > df['Away_Goals']),
    (df['Home_Goals'] == df['Away_Goals']),
    (df['Home_Goals'] < df['Away_Goals'])
]
df['Target'] = np.select(conditions, [0, 1, 2])

feature_data = {
    'Home_Team_Points': [], 'Away_Team_Points': [],
    'Home_Rank': [], 'Away_Rank': [],
    'Home_Form_5': [], 'Away_Form_5': []
}

for season in df['Season'].unique():
    season_df = df[df['Season'] == season]
    
    teams = set(season_df['Home_Team']).union(set(season_df['Away_Team']))
    points_table = {team: 0 for team in teams}
    form_history = {team: [] for team in teams} 
    
    for index, row in season_df.iterrows():
        h_team = row['Home_Team']
        a_team = row['Away_Team']
        
        
        h_points = points_table[h_team]
        a_points = points_table[a_team]
        
        
        current_standings = sorted(points_table.items(), key=lambda x: x[1], reverse=True)
        ranks = {team: i+1 for i, (team, pts) in enumerate(current_standings)}
        
        h_rank = ranks[h_team]
        a_rank = ranks[a_team]
        
        h_form = sum(form_history[h_team][-5:]) if form_history[h_team] else 0
        a_form = sum(form_history[a_team][-5:]) if form_history[a_team] else 0
        
        feature_data['Home_Team_Points'].append(h_points)
        feature_data['Away_Team_Points'].append(a_points)
        feature_data['Home_Rank'].append(h_rank)
        feature_data['Away_Rank'].append(a_rank)
        feature_data['Home_Form_5'].append(h_form)
        feature_data['Away_Form_5'].append(a_form)
        
        h_g = row['Home_Goals']
        a_g = row['Away_Goals']
        
        if h_g > a_g: # Home Win
            points_table[h_team] += 3
            form_history[h_team].append(3)
            form_history[a_team].append(0)
        elif h_g == a_g: # Draw
            points_table[h_team] += 1
            points_table[a_team] += 1
            form_history[h_team].append(1)
            form_history[a_team].append(1)
        else: # Away Win
            points_table[a_team] += 3
            form_history[a_team].append(3)
            form_history[h_team].append(0)


df = df.sort_values(['Season', 'Date']) 
for col, values in feature_data.items():
    df[col] = values


if 'Home_Rank' in df.columns:
    df = df.drop(columns=['Home_Rank', 'Away_Rank'])


for col, values in feature_data.items():
    df[col] = values

df.to_csv("final_training_data.csv", index=False)
print("Success! Created 'final_training_data.csv'")

df.to_csv("final_training_data.csv", index=False)
print("Success! Created 'final_training_data.csv'")
print(df[['Date', 'Home_Team', 'Home_Team_Points', 'Home_Rank', 'Score']].tail())