# import statsapi as mlbstats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pbb
from datetime import date
from matplotlib import gridspec




df_sch = pd.read_csv('mets_2023.csv')
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


### Preseason messes up pybaseball.standings:
try:
    standings = pd.concat(pbb.standings(), ignore_index=True)
    team_rec = [f"{standings.loc[standings['Tm']==team, ['W']].values[0][0]}-{standings.loc[standings['Tm']==team, ['L']].values[0][0]}" for team in df_teams['team']]
except:
    team_rec = ["0-0" for team in df_teams['team']]


nicknames = []
for i,t in enumerate(df_teams['team']):
    if t.split()[-1] == "Sox": #Accounting for Boston/Chicago Sox
        nicknames.append(f"{t.split()[-2]+ ' ' + t.split()[-1] } ({team_rec[i]})")
    else:
        nicknames.append(f"{t.split()[-1]} ({team_rec[i]})")
df_teams['team'] = nicknames

df_teams.sort_values(['total', 'team'], ascending=[False, True], inplace=True, ignore_index=True)



_, won, lost, incomplete, total, inc_home, inc_away = df_teams.sum().values

won = round(won)
lost = round(lost)
incomplete = round(incomplete)
incomplete_home = round(inc_home)
incomplete_away = round(inc_away)



###


# fig, ax= plt.subplots(figsize=(25, 25), nrows=2, ncols=1, gridspec_kw={'height_ratios': [5, 1]})
fig, ax= plt.subplots(nrows=2, ncols=2, gridspec_kw={'height_ratios': [15, 1]})
ax[1,1].remove()
w = 0.9 #main bar width
x = [np.arange(15), np.arange(14)]

for i in range(2):
    wins       = ax[0,i].barh(x[i], df_teams['won'][i::2], w, label='won',
                        color="cornflowerblue", edgecolor='k')
    losses     = ax[0,i].barh(x[i], df_teams['lost'][i::2], w, left=df_teams['won'][i::2],
                        label='lost', color="darkorange", edgecolor='k')


    home       = ax[0,i].barh(x[i], df_teams['inc_home'][i::2], w, left=df_teams['won'][i::2]+df_teams['lost'][i::2],
                        label="incomplete home", color='silver', edgecolor='k')
    away       = ax[0,i].barh(x[i], df_teams['inc_away'][i::2], w, left=df_teams['won'][i::2]+df_teams['lost'][i::2] + df_teams['inc_home'][i::2],
                        label="incomplete away", color='k', edgecolor='k')

for index, row in df_teams.iterrows():
    # print(row)
    # So we ignore when one of the totals equals zero
    if round(row['won']) != 0:
        ax[0,index%2].text(row['won']/2, x[0,index//2], int(row['won']),
                weight='bold', va='center', ha='center',
                size=18, fontname='serif')
    
    if round(row['lost']) != 0:
        ax[0,index%2].text(row['won']+row['lost']/2, x[0,index//2], int(row['lost']),
                weight='bold', va='center', ha='center',
                size=18, fontname='serif')

    if round(row['inc_home']) != 0:
        ax[0,index%2].text(row['won']+row['lost']+row['inc_home']/2,
                x[0][index//2], int(row['inc_home']),
                weight='bold', va='center', ha='center',
                size=18, fontname='serif')

    if round(row['inc_away']) != 0:
        ax[0,index%2].text(row['won']+row['lost']+row['inc_home']+row['inc_away']/2,
                x[0][index//2], int(row['inc_away']),
                weight='bold', va='center', ha='center', color='w',
                size=18, fontname='serif')
    


###total season bar

wins       = ax[1,0].barh(0, won, w, label='won',
                     color="cornflowerblue", edgecolor='k')
ax[1,0].text(won/2, 0, round(won) ,weight='bold', va='center', ha='center',
                size=18, fontname='serif')

losses     = ax[1,0].barh(0, lost, w, left=won,
                     label='lost', color="darkorange", edgecolor='k')
ax[1,0].text(won+lost/2, 0, round(lost), weight='bold', va='center', ha='center',
                size=18, fontname='serif')

home       = ax[1,0].barh(0, inc_home, w, left=won+lost,
                     label="incomplete home", color='silver', edgecolor='k')
ax[1,0].text(won+lost+inc_home/2, 0, round(inc_home),
                weight='bold', va='center', ha='center',
                size=18, fontname='serif')

away       = ax[1,0].barh(0, inc_away, w, left=won+lost+inc_home,
                     label="incomplete away", color='k', edgecolor='k')
ax[1,0].text(won+lost+inc_home+inc_away/2, 0, round(inc_away),
                weight='bold', va='center', ha='center', color='w',
                size=18, fontname='serif')

ax[1,0].axis('off')
ax[1,0].set_title('Total Season:', size=20, weight='bold',
             fontname='serif')

ax[1,0].set_xlim(0, 162)
###End edits

#Graph styling:



# ax[0,0].grid(axis='x', which='major', linewidth=2)
for i in range(2):
    ax[0,i].set_ylim(min(x[0])-w/2, max(x[0])+w/2)
    ax[0,i].invert_yaxis()
    ax[0,i].set_xticks(range(0, 21, 5), fontfamily='serif', minor=False)
    ax[0,i].set_xticks(range(0, 21, 1), fontfamily='serif', minor=True)
    ax[0,i].tick_params('x', labelsize='large')
    ax[0,i].set_yticks(ticks = x[i], labels=df_teams['team'][i::2], size=18, fontfamily='serif')
    ax[0,i].set_xlim(0, df_teams['total'].max())
ax[0,0].legend(labels=['won', 'lost', 'incomplete home', 'incomplete away'],
          loc=4, ncol=1, prop={'family': "serif", 'size':'x-large', 'weight': 'bold'})

fig.suptitle(f"Mets Current Season Series Progress\n{date.today()} ({won}-{lost}, {incomplete} GR)", size=24, weight='bold',
             fontname='serif', y=0.9, va='bottom')
plt.subplots_adjust(wspace=0.5, right=0.995, left=0.21)


### Legend plot



# plt.savefig("test.png")
plt.show()