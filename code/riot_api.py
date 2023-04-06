import requests
from summoner_requests import Summoner

api_key = "RGAPI-3ba7525b-e0fc-4be2-86a4-58750debf565"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)

summoner_info = summoner.summoner_info()

print(len(summoner.all_ranked_matches_this_season()))
