from summoner import Summoner
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


games_data = execution_time(lambda: summoner.games_data())
print(f"execution time: {games_data}")


print("DATOS DE CACHE ################")
cache_key = f"{summoner.puuid}_games_data"
print(summoner.cache.get(cache_key))


games_data_2 = execution_time(lambda: summoner.games_data())
print(f"execution time 2: {games_data_2}")