# Various Baseball Codes
A collective repository of various smaller "just for fun" baseball coding projects. 

## `mets-season-series`
Graphically displays the current status of all of the season series matchups for my favorite team: the New York Mets. Data is fetched via the `MLB-StatsAPI` library and loaded into a pandas DataFrame. To not have to fetch every time, the is done in `make_schedule.py` which stores the data into `mets_2022.csv`. `piecharts.py` then reads this csv and visualizes how the Mets have performed against other teams as a series of pie charts. All pie charts are stored in `figures`.