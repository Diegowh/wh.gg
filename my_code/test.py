from summoner import Summoner
import time


api_key = "RGAPI-885c2233-8ae3-4398-b5ec-3cb3698f68d2"
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

