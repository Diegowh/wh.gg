import requests
from summoner_requests import Summoner
import time


api_key = "RGAPI-3ba7525b-e0fc-4be2-86a4-58750debf565"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)

summoner_info = summoner.summoner_info()

start_time = time.time()
print(summoner.champion_stats())
end_time = time.time()

execution_time = end_time - start_time

print("Execution time: ", execution_time)