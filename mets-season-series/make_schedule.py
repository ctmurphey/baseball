import statsapi as mlbstats
import pandas as pd

mets = mlbstats.lookup_team('nyn')[0]['id']

sched = mlbstats.schedule(start_date = '01/01/2022', end_date='12/31/2022', team=str(mets))

df_sch = pd.DataFrame(sched)

df_sch.to_csv('mets_2022.csv')