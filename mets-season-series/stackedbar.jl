using DataFrames, PyCall, CSV, PlotlyJS

main_team = "New York Mets"


julia_df = CSV.read("mets_2022.csv", DataFrame)

select!(julia_df, [:game_date, :status, :away_name, :home_name,
                         :winning_team])


julia_df[!, :other_team] = [(row[:home_name]==main_team) ? row[:away_name] : row[:home_name] for row in eachrow(julia_df)]


teams = DataFrame(team=unique(julia_df[!, :other_team]))


teams.total = [count(i->(i == team.team), julia_df[:, :other_team]) for team in eachrow(teams)]
teams.won   = [count(i->(i.other_team == team.team && i.winning_team==main_team), 
                eachrow(dropmissing(julia_df[:, [:other_team, :winning_team]]))) for team in eachrow(teams)]
teams.lost  = [count(i->(i.other_team == team.team && i.winning_team==team.team), 
                eachrow(dropmissing(julia_df[:, [:other_team, :winning_team]]))) for team in eachrow(teams)]

teams.incomplete = [count(i->(i.other_team == team.team && i.status=="Scheduled"), 
                    eachrow(julia_df[:, [:other_team, :status]])) for team in eachrow(teams)]
teams.incomplete_home   = [count(i->(i.other_team == team.team && i.status=="Scheduled" && i.home_name==main_team),
                     eachrow(julia_df[:, [:other_team, :status, :home_name]])) for team in eachrow(teams)]
teams.incomplete_away   = [count(i->(i.other_team == team.team && i.status=="Scheduled" && i.away_name==main_team), 
                    eachrow(julia_df[:, [:other_team, :status, :away_name]])) for team in eachrow(teams)]

sort!(teams, [:total, :team], rev=[false, true])

# show(teams)
show(julia_df)

PlotlyJS.plot(
    [PlotlyJS.bar(teams, x=y, y=:team, text=y, textangle=0, 
    name=String(y), orientation="h" ) for y in [:won, :lost, :incomplete_home, :incomplete_away]],
    Layout(title="Mets Current Season Series Results", barmode="stack")
)