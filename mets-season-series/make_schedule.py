import statsapi as mlbstats
import pandas as pd

mets = mlbstats.lookup_team('nyn')[0]['id']

sched = mlbstats.schedule(start_date = '01/01/2023', end_date='12/31/2023', team=str(mets))

df_sch = pd.DataFrame(sched)

df_sch = pd.DataFrame(df_sch.loc[df_sch['status'] != 'Postponed'])  #remove postponed games
df_sch = pd.DataFrame(df_sch.loc[df_sch['game_type'] == 'R'])       #remove spring training


df_sch.to_csv('mets_2023.csv')