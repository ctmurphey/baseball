import statsapi as mlbstats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



df_sch = pd.read_csv('mets_2022.csv')
df_sch.pop('Unnamed: 0')


df_sch = pd.DataFrame(df_sch.loc[df_sch['status'] != 'Postponed'])
df_sch = pd.DataFrame(df_sch.loc[df_sch['game_type'] != 'S'])


other_team = []

for index, row in df_sch.iterrows():
    # print(row[['home_name', 'away_name']])
    if row['home_id'] == 121:
        other_team.append(row['away_name'])
    else:
        other_team.append(row['home_name'])

df_sch['other_team'] = other_team



team_set = set(other_team)

df_teams = pd.DataFrame({'team': [t for t in team_set]})


df_teams['won'] = np.zeros(len(team_set))
df_teams['lost'] = np.zeros(len(team_set))
df_teams['incomplete'] = np.zeros(len(team_set))
df_teams['total'] = np.zeros(len(team_set))



def absval(v, row):
    val = int(v*row.loc[['total']][0]/100)
    if val == 0:
        return ""
    else:
        return val

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

won = int(won)
lost = int(lost)
incomplete = int(incomplete)


fig, axs = plt.subplots(int(len(team_set)/2), 2, figsize = (8, 70))

for index, row in df_teams.iterrows():

    absv = lambda v: absval(v, row)
    axs[index//2][index%2].pie(row.loc[['won', 'lost', 'incomplete']],
                                 colors=['cornflowerblue', 'darkorange', 'silver'],
                                 autopct=absv, pctdistance=0.5,
                                 textprops={'family': "serif", 'size':'large'})

    axs[index//2][index%2].text(-0.01, 0.5, row.loc[['team']].values[0], va='center', 
                    ha='right', fontsize=15,transform=axs[index//2][index%2].transAxes,
                    fontname="serif")

fig.legend(labels=['won', 'lost', 'incomplete'], loc=8, ncol=3,
             prop={'family': "serif", 'size':'xx-large', 'weight': 'bold'})


fig.suptitle('Mets Current Season Series Results \n 5/31/2022', fontname="serif",
            weight='bold', size=25, y=0.95)

record_str = f"Record: {won}-{lost}, {incomplete} Games Remaining"
fig.text(0.5, 0.07, record_str, horizontalalignment='center',
         weight='bold', size=20, fontname='serif')
plt.show()

