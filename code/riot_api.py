import requests
from summoner_requests import Summoner
import time


api_key = "RGAPI-6a313384-90c6-4035-a902-1e430877bcdf"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)

summoner_info = summoner.summoner_info()

start_time = time.time()
print(summoner.last_10_games_data())
end_time = time.time()

execution_time = end_time - start_time

print("Execution time: ", execution_time)

