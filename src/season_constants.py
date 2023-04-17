from datetime import datetime

season_start_date = "2023-01-11"
SEASON_START_TIMESTAMP = int(datetime.strptime(season_start_date, "%Y-%m-%d").timestamp())
