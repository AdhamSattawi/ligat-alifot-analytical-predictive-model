import pandas as pd

regular = pd.read_csv("israel_league_2010_2025.csv")
playoffs = pd.read_csv("israel_playoffs_2010_2024.csv")

full_df = pd.concat([regular, playoffs], ignore_index=True)

full_df['Date_Obj'] = pd.to_datetime(full_df['Date'], dayfirst=True, errors='coerce') 
full_df = full_df.sort_values(['Season', 'Date_Obj'])
full_df = full_df.drop(columns=['Date_Obj'])

full_df.to_csv("israel_league_FULL_2010_2025.csv", index=False)