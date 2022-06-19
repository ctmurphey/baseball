using DataFrames, PyCall, CSV, StatsPlots

julia_df = CSV.read("mets_2022.csv", DataFrame)

trimmed_df = julia_df[!, [:game_date, :status, :away_name, :home_name]]

show(trimmed_df)