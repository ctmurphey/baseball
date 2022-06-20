using DataFrames, PyCall, CSV, StatsPlots

julia_df = CSV.read("mets_2022.csv", DataFrame)

select!(julia_df, [:game_date, :status, :away_name, :home_name,
                         :winning_team])

# show(julia_df)

# println(names(julia_df))

grp = groupby(julia_df, "winning_team")
# println(grp)

