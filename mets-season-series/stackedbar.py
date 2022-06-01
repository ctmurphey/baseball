import statsapi as mlbstats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pbb
from datetime import date



df_sch = pd.read_csv('mets_2022.csv')
df_sch.pop('Unnamed: 0')




other_team = [] # list of other teams played

for index, row in df_sch.iterrows():

    if row['home_id'] == 121:
        other_team.append(row['away_name'])
    else:
        other_team.append(row['home_name'])

df_sch['other_team'] = other_team



team_set = set(other_team) #only want unique values of other teams

df_teams = pd.DataFrame({'team': [t for t in team_set]})


df_teams['won'] = np.zeros(len(team_set))
df_teams['lost'] = np.zeros(len(team_set))
df_teams['incomplete'] = np.zeros(len(team_set))
df_teams['total'] = np.zeros(len(team_set))




### Not optimal method, should optimize to list comprehension in future version
for index, row in df_sch.iterrows():
    if row['status'] == 'Scheduled':
        df_teams.loc[df_teams['team']==row['other_team'], ['incomplete']] += 1

    elif row['winning_team'] == 'New York Mets':
        df_teams.loc[df_teams['team']==row['other_team'], ['won']] += 1

    else:
        df_teams.loc[df_teams['team']==row['other_team'], ['lost']] += 1    

    df_teams.loc[df_teams['team']==row['other_team'], ['total']] += 1   


df_teams.sort_values('won', ascending=False, inplace=True, ignore_index=True)
df_teams.sort_values('team', ascending=True, inplace=True, ignore_index=True)
df_teams.sort_values(['total', 'team'], ascending=[False, True], inplace=True, ignore_index=True)



_, won, lost, incomplete, total = df_teams.sum().values

won = round(won)
lost = round(lost)
incomplete = round(incomplete)



def absval(v, row):
    '''Scales the normalized fractions to values for the pie charts'''
    val = round(v*row.loc[['total']][0]/100)
    if val == 0:
        return ""
    else:
        return val

standings = pd.concat(pbb.standings(), ignore_index=True)


fig, ax = plt.subplots()

ax.barh(df_teams['team'], df_teams['won'], 0.7, label='won', color='cornflowerblue')
ax.barh(df_teams['team'], df_teams['lost'], 0.7, left=df_teams['won'], label='lost', color='darkorange')
ax.barh(df_teams['team'], df_teams['incomplete'], 0.7, left=df_teams['won']+df_teams['lost'],\
        label="incomplete", color='silver')
ax.invert_yaxis()
ax.set_xticks(range(0, 21, 5))
ax.set_xlim(0, 20)
ax.legend()
fig.tight_layout()
plt.show()