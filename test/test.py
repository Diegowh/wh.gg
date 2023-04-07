from my_code.summoner import Summoner
import time


api_key = "RGAPI-6a313384-90c6-4035-a902-1e430877bcdf"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)


# calculador de tiempo de ejecucion

def execution_time(func, *args, **kwargs):

    print("#####################")
    print("Starting execution...")
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    print("#####################")
    execution_time = end_time - start_time
    
    return execution_time


summoner_name = execution_time(lambda: summoner.summoner_name)
print(f"summoner name execution time: {summoner_name}")
soloq_rank = execution_time(lambda: summoner.soloq_rank())
print(f"soloq rank execution time: {soloq_rank}")
flex_rank = execution_time(lambda: summoner.flex_rank())
print(f"flex rank execution time: {flex_rank}")
champ_stats = execution_time(lambda: summoner.champion_stats())
print(f"champion stats execution time: {champ_stats}")
last_10_games = execution_time(lambda: summoner.last_10_games_data())
print(f"last 10 games: {last_10_games}")