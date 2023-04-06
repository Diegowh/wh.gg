import requests
from summoner_requests import Summoner
import time


api_key = "RGAPI-45ba0427-faf4-4f8e-90ef-2795fc23db7f"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)

summoner_info = summoner.summoner_info()

start_time = time.time()
print(summoner.champion_stats())
end_time = time.time()

execution_time = end_time - start_time

print("Execution time: ", execution_time)


summoner.champion_stats["Nami"]["kda"]