from ..models.summoner import Summoner
import time


api_key = "RGAPI-13f2c40d-9832-4434-afe5-d7607e66bc36"
region = "EUW1"
summoner_name = "Flan de Nata"


summoner = Summoner(api_key=api_key, region=region, summoner_name= summoner_name)


# calculador de tiempo de ejecucion

# def execution_time(func, *args, **kwargs):

#     print("#####################")
#     print("Starting execution...")
#     start_time = time.time()
#     result = func(*args, **kwargs)
#     end_time = time.time()
#     print("#####################")
#     execution_time = end_time - start_time
    
#     return execution_time


# games_data = execution_time(lambda: summoner.games_data())
# print(f"execution time: {games_data}")

# print(summoner.all_ranked_matches_this_season())

all_match_id = ['EUW1_6345549710', 'EUW1_6345496538', 'EUW1_6345433904', 'EUW1_6345142322', 'EUW1_6339380493', 'EUW1_6339323920', 'EUW1_6339250960', 'EUW1_6336043681', 'EUW1_6335990485', 'EUW1_6335149846', 'EUW1_6335083193', 'EUW1_6334990202', 'EUW1_6333398038', 'EUW1_6333289128', 'EUW1_6333198691', 'EUW1_6333116104', 'EUW1_6331707404', 'EUW1_6331633424', 'EUW1_6331557626', 'EUW1_6319379556', 'EUW1_6318454124', 'EUW1_6318368453', 'EUW1_6318275124', 'EUW1_6313645022', 'EUW1_6313601210', 'EUW1_6306959370', 'EUW1_6306074985', 'EUW1_6306002649', 'EUW1_6300186510', 'EUW1_6300157620', 'EUW1_6300138970', 'EUW1_6298835377', 'EUW1_6294672876', 'EUW1_6294612471', 'EUW1_6293112896', 'EUW1_6293053761', 'EUW1_6291660744', 'EUW1_6291566163', 'EUW1_6291488103', 'EUW1_6291475115', 'EUW1_6291419097', 'EUW1_6290626547', 'EUW1_6290123210', 'EUW1_6289437841', 'EUW1_6289414741', 'EUW1_6288194229', 'EUW1_6288124915', 'EUW1_6288065494', 'EUW1_6287569584', 'EUW1_6287547276', 'EUW1_6285142804', 'EUW1_6280426248', 'EUW1_6278719626', 'EUW1_6278655818', 'EUW1_6278596626', 'EUW1_6274057661', 'EUW1_6274004995', 'EUW1_6273946004', 'EUW1_6273909833', 'EUW1_6270710954', 'EUW1_6270690415', 'EUW1_6260610386', 'EUW1_6259920316', 'EUW1_6258300501', 'EUW1_6258251372', 'EUW1_6258228878', 'EUW1_6258179758', 'EUW1_6256957149', 'EUW1_6256925289']

print(summoner.league_entries())