import statsapi as mlbstats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pbb
from datetime import date



df_sch = pd.read_csv('mets_2022.csv') #full schedule table
df_sch.pop('Unnamed: 0') #remove csv reading artifact




other_team = [] # list of other teams played

for index, row in df_sch.iterrows():

    if row['home_id'] == 121:
        other_team.append(row['away_name'])
    else:
        other_team.append(row['home_name'])

df_sch['other_team'] = other_team



team_set = set(other_team) #only want unique names of other teams

df_teams = pd.DataFrame({'team': [t for t in team_set]}) #table of just season series

### This method bothers me, will replace eventually with a more "Pythonic" way
df_teams['won'] = np.zeros(len(team_set))
df_teams['lost'] = np.zeros(len(team_set))
df_teams['incomplete'] = np.zeros(len(team_set))
df_teams['total'] = np.zeros(len(team_set))
df_teams['inc_home'] = np.zeros(len(team_set))
df_teams['inc_away'] = np.zeros(len(team_set))




### Not optimal method, should optimize to list comprehension in future version
for index, row in df_sch.iterrows():
    if row['status'] == 'Scheduled':
        df_teams.loc[df_teams['team']==row['other_team'], ['incomplete']] += 1
        if row['other_team'] == row['away_name']:
            df_teams.loc[df_teams['team']==row['other_team'], ['inc_home']] += 1
        else:
            df_teams.loc[df_teams['team']==row['other_team'], ['inc_away']] += 1


    elif row['winning_team'] == 'New York Mets':
        df_teams.loc[df_teams['team']==row['other_team'], ['won']] += 1

    else:
        df_teams.loc[df_teams['team']==row['other_team'], ['lost']] += 1    

    df_teams.loc[df_teams['team']==row['other_team'], ['total']] += 1   


df_teams.sort_values(['total', 'team'], ascending=[False, True], inplace=True, ignore_index=True)



_, won, lost, incomplete, total, inc_home, inc_away = df_teams.sum().values

won = round(won)
lost = round(lost)
incomplete = round(incomplete)
incomplete_home = round(inc_home)
incomplete_away = round(inc_away)




# For plotting correct tallies in the pie chart, 
def absval_out(v, row):
    '''Scales the normalized fractions to values for the pie charts'''
    val = round(v*row.loc[['total']][0]/100)
    if val == 0:
        return ""
    else:
        return val

def absval_in(v, row):
    '''Scales the normalized fractions to values for the pie charts'''
    val = round(v*row.loc[['total']][0]/100)
    if val == 0:
        return ""
    else:
        return val


# getting current standings info for all teams
standings = pd.concat(pbb.standings(), ignore_index=True)

outer_rad = 1.4 #outer radius of pie chart
inner_rad = 0.7 #inner radius of pie chart


# Pie chart time
fig, axs = plt.subplots(int(len(team_set)/2), 2, figsize = (8, 70))

for index, row in df_teams.iterrows():
    played_yet = (row.loc[['incomplete']].values[0] != row.loc[['total']].values[0])

    # Inner Pies
    absv = lambda v: absval_in(v, row)
    axs[index//2][index%2].pie(row.loc[['incomplete', 'won', 'lost']],
                                #  colors=['cornflowerblue', 'darkorange', 'silver'],
                                 colors=['silver', 'cornflowerblue', 'darkorange'],
                                #  autopct=absv, pctdistance=0.5*played_yet,
                                 textprops={'family': "serif", 'size':'x-large'},
                                 radius=inner_rad)

    # Outer Pies
    absv = lambda v: absval_out(v, row)
    axs[index//2][index%2].pie(row.loc[['inc_home', 'inc_away', 'won', 'lost']],
                                #  colors=['cornflowerblue', 'darkorange', 'gainsboro', 'gray'],
                                 colors=['gainsboro', 'gray', 'cornflowerblue', 'darkorange'],
                                 autopct=absv, pctdistance=0.77,
                                 textprops={'family': "serif", 'size':'x-large'},
                                 radius=outer_rad,
                                 wedgeprops=dict(width=outer_rad-inner_rad, linewidth=0))

    team_rec = f"{standings.loc[standings['Tm']==row.loc[['team']].values[0],['W']].values[0][0]} - {standings.loc[standings['Tm']==row.loc[['team']].values[0],['L']].values[0][0]} "

    axs[index//2][index%2].text(-0.01, 0.5, f"{row.loc[['team']].values[0]} \n{team_rec}", va='center', 
                    ha='right', fontsize=15,transform=axs[index//2][index%2].transAxes,
                    fontname="serif")

    inc_x = 0.4*(row['incomplete']!=row['total'])*np.cos(np.pi*row['incomplete']/row['total'])
    inc_y = 0.4*(row['incomplete']!=row['total'])*np.sin(np.pi*row['incomplete']/row['total'])
    if row['incomplete'] != 0:
        axs[index//2][index%2].text(inc_x, inc_y, round(row['incomplete']), 
                                    va='center', ha='center', fontname='serif', fontsize=15)



fig.legend(labels=['Incomplete', 'Won', 'Lost', 'Incomplete\nHome', 'Incomplete\nAway'],
            loc=5, ncol=1, prop={'family': "serif", 'size':'xx-large', 'weight': 'bold'})


fig.suptitle(f'Mets Current Season Series Results\n{date.today()}', fontname="serif",
            weight='bold', size=25, y=0.95)

record_str = f"Record: {won}-{lost}, {incomplete} Games Remaining"
fig.text(0.5, 0.07, record_str, horizontalalignment='center',
         weight='bold', size=20, fontname='serif')


plt.show()