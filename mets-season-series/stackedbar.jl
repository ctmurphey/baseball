using DataFrames, CSV, PlotlyJS, Dates

main_team = "New York Mets"


games_df = CSV.read("mets_2022.csv", DataFrame)

select!(games_df, [:game_date, :status, :away_name, :home_name,
                         :winning_team])


games_df[!, :other_team] = [(row[:home_name]==main_team) ? row[:away_name] : row[:home_name] for row in eachrow(games_df)]

#Initialize main dataframe to plot
teams = DataFrame(team=unique(games_df[!, :other_team]))

#Fill out rest of the values needed in the dataframe
teams.total = [count(i->(i == team.team), games_df[:, :other_team]) for team in eachrow(teams)]
teams.won   = [count(i->(i.other_team == team.team && i.winning_team==main_team), 
                eachrow(dropmissing(games_df[:, [:other_team, :winning_team]]))) for team in eachrow(teams)]
teams.lost  = [count(i->(i.other_team == team.team && i.winning_team==team.team), 
                eachrow(dropmissing(games_df[:, [:other_team, :winning_team]]))) for team in eachrow(teams)]

teams.incomplete = [count(i->(i.other_team == team.team && i.status=="Scheduled"), 
                    eachrow(games_df[:, [:other_team, :status]])) for team in eachrow(teams)]
teams.incomplete_home   = [count(i->(i.other_team == team.team && i.status=="Scheduled" && i.home_name==main_team),
                     eachrow(games_df[:, [:other_team, :status, :home_name]])) for team in eachrow(teams)]
teams.incomplete_away   = [count(i->(i.other_team == team.team && i.status=="Scheduled" && i.away_name==main_team), 
                    eachrow(games_df[:, [:other_team, :status, :away_name]])) for team in eachrow(teams)]

#Sort the teams consistently
sort!(teams, [:total, :team], rev=[false, true])

title = "Mets Current Season Series Results: " * string(today())
### make the stacked bar graphs
PlotlyJS.plot(
    [PlotlyJS.bar(teams, x=y, y=:team, text=y, textangle=0, 
    name=String(y), orientation="h" ) for y in [:won, :lost, :incomplete_home, :incomplete_away]],
    Layout(title=title, barmode="stack")
)