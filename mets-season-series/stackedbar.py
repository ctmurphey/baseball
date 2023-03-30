# import statsapi as mlbstats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pbb
from datetime import date
from matplotlib import gridspec
from matplotlib import gridspec

pbb.cache.enable()


df_sch = pd.read_csv('mets_2023.csv')
df_sch.pop('Unnamed: 0') #artifact from saving csv in other code


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

# get divisions for teams:
divs = ['ALE', 'ALC', 'ALW', 'NLE', 'NLC', 'NLW'] #order that pbb prints standings

### Preseason messes up pybaseball.standings:
try:
    standings = pd.concat(pbb.standings(), ignore_index=True)
    team_rec = [f"{standings.loc[standings['Tm']==team, ['W']].values[0][0]}-{standings.loc[standings['Tm']==team, ['L']].values[0][0]}" for team in df_teams['team']]
except:
    standings = pd.concat(pbb.standings(2022), ignore_index=True)
    team_rec = ["0-0" for team in df_teams['team']]
standings['div'] = [divs[i] for i in range(6) for j in range(5)]
teams_div = [standings.loc[standings['Tm']==team, ['div']].values[0][0] for team in df_teams['team']]

nicknames = [] ## Adding city names crowds up the labels too much
for i,t in enumerate(df_teams['team']):
    if t.split()[-1] == "Sox" or t.split()[-1] == "Jays": #Accounting for teams with 2-word nicknames
        nicknames.append(f"{t.split()[-2]+ ' ' + t.split()[-1] } ({team_rec[i]})")
    else:
        nicknames.append(f"{t.split()[-1]} ({team_rec[i]})")
df_teams['team'] = nicknames
df_teams['div'] = teams_div

df_teams['div'] = pd.Categorical(df_teams['div'], ["NLE", "NLC", "NLW", "ALE", "ALC", "ALW"])


### Order for the teams to be plotted in, consistent throughout the season
df_teams.sort_values(['div', 'total', 'team'], ascending=[True, False, True], inplace=True, ignore_index=True)

# Tallying total season results actross all teams
won, lost, incomplete, total, inc_home, inc_away = df_teams.sum(numeric_only=True).values
won = round(won)
lost = round(lost)
incomplete = round(incomplete)
incomplete_home = round(inc_home)
incomplete_away = round(inc_away)


### Trying new way due to 50% more teams:
fig = plt.figure(tight_layout=True, figsize=(12.75, 7))
gs = gridspec.GridSpec(2, 2, height_ratios=[1,12], width_ratios=[13,3])

w = 0.9 #main bar width
x = [np.arange(14), np.arange(15)]


### Total season progress bar:
ax = fig.add_subplot(gs[0, :])

if won != 0:
    wins   = ax.barh(0, won, w, label='won',
                        color="cornflowerblue", edgecolor='k')
    ax.text(won/2, 0, round(won) ,weight='bold', va='center', ha='center',
                    size=18, fontname='serif')
if lost != 0:
    losses = ax.barh(0, lost, w, left=won,
                        label='lost', color="darkorange", edgecolor='k')
    ax.text(won+lost/2, 0, round(lost), weight='bold', va='center', ha='center',
                    size=18, fontname='serif')
if inc_home != 0:
    home   = ax.barh(0, inc_home, w, left=won+lost,
                        label="incomplete home", color='silver', edgecolor='k')
    ax.text(won+lost+inc_home/2, 0, round(inc_home),
                    weight='bold', va='center', ha='center',
                    size=18, fontname='serif')

if inc_away != 0:
    away   = ax.barh(0, inc_away, w, left=won+lost+inc_home,
                        label="incomplete away", color='k', edgecolor='k')
    ax.text(won+lost+inc_home+inc_away/2, 0, round(inc_away),
                    weight='bold', va='center', ha='center', color='w',
                    size=18, fontname='serif')

ax.axis('off')
ax.set_title('Total Season:', size=20, weight='bold',
             fontname='serif')

ax.set_xlim(0, 162)



### Individual team progress bars, broken into two plots
leagues = ["National League", "American League"]
locs = ["center", "left"]

for i in range(2):
    ax = fig.add_subplot(gs[1, i])
    wins       = ax.barh(x[i], df_teams['won'][14*i : 14+i*15], w, label='won',
                        color="cornflowerblue", edgecolor='k')
    
    losses     = ax.barh(x[i], df_teams['lost'][14*i : 14+i*15], w, left=df_teams['won'][14*i : 14+i*15],
                        label='lost', color="darkorange", edgecolor='k')

    home       = ax.barh(x[i], df_teams['inc_home'][14*i : 14+i*15], w,
                          left=df_teams['won'][14*i : 14+i*15]+df_teams['lost'][14*i : 14+i*15],
                        label="incomplete home", color='silver', edgecolor='k')
    
    away       = ax.barh(x[i], df_teams['inc_away'][14*i : 14+i*15], w, 
                         left=df_teams['won'][14*i : 14+i*15]+df_teams['lost'][14*i : 14+i*15] + df_teams['inc_home'][14*i : 14+i*15],
                        label="incomplete away", color='k', edgecolor='k')
    

    for j in x[i]: 
        if wins.datavalues[j] != 0: #Ignore values that are currently 0
            ax.text(wins.datavalues[j]/2, x[i][j], int(wins.datavalues[j]), 
                    weight='bold', va='center', ha='center',
                    size=18, fontname='serif')
            
        if losses.datavalues[j] != 0:
            ax.text(wins.datavalues[j] + losses.datavalues[i]/2, x[i][j], int(losses.datavalues[j]), 
                    weight='bold', va='center', ha='center',
                    size=18, fontname='serif')
            
        if home.datavalues[j] != 0:
            ax.text(wins.datavalues[j] + losses.datavalues[j] + home.datavalues[j]/2, x[i][j], int(home.datavalues[j]), 
                    weight='bold', va='center', ha='center',
                    size=18, fontname='serif')
            
        if away.datavalues[j] != 0:
            ax.text(wins.datavalues[j] + losses.datavalues[j] + home.datavalues[j]\
                     + away.datavalues[j]/2, x[i][j], int(away.datavalues[j]), 
                    weight='bold', va='center', ha='center',
                    size=18, fontname='serif', color='w')

    ax.set_ylim(-w/2, max(x[i])+w/2)
    ax.invert_yaxis()
    ax.set_xticks(range(0, 21, 5), fontfamily='serif', minor=False)
    ax.set_xticks(range(0, 21, 1), fontfamily='serif', minor=True)
    ax.tick_params('x', labelsize='large')
    ax.set_yticks(ticks = x[i], labels=df_teams['team'][14*i : 14+i*15], size=18, fontfamily='serif')
    ax.set_xlim(0, [13, 4][i])
    ax.set_title(leagues[i], loc=locs[i], weight='bold', va='center', ha='center', size=18, fontname='serif')


handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.025),
           prop={'family': "serif", 'size':'x-large', 'weight': 'bold'}, framealpha=0)



fig.suptitle(f"Mets Current Season Series Progress\n{date.today()} ({won}-{lost}, {incomplete} GR)"
             , size=24, weight='bold', fontname='serif', y=0.9, va='bottom')
fig.tight_layout()
plt.savefig("test.jpg")
# plt.show()