import requests

# # summoner_name = str(input("Enter a summoner name:\n"))

# summoner_name = "Flan de Nata"

# api_key = "RGAPI-a5d0c46c-dc80-4a4f-9f00-353156010418"
# api_summoner_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}"


# # summoner request
# summoner_response = requests.get(api_summoner_url)

# player_info: dict = summoner_response.json()

# player_account_id = player_info["accountId"]
# player_level = player_info["summonerLevel"]
# puuid = player_info["puuid"]



# # 20 last matches request
# api_match_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={api_key}"

# matches_response = requests.get(api_match_url)

# matches: list = matches_response.json()


# # One match data request
# match_data_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matches[0]}?api_key={api_key}"

# match_data_response: dict = requests.get(match_data_url)
# match_data: dict = match_data_response.json()

# game_mode = match_data['info']['gameMode']


# participant_1_data = match_data['info']['participants'][0]


# summinfo = requests.get(f"https://EUW1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}")
# summ_id = summinfo.json()['id']
# print(summ_id)

# league_entries = requests.get(f"https://EUW1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summ_id}?api_key={api_key}")

# print(league_entries.json())


# def generate_numbers(n):
#     i = 1
#     while i <= n:
#         yield i
#         i += 1

# # Usar la función generadora en un bucle for
# for number in generate_numbers(5):
#     print(number)

response = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/EUW1_6336043681?api_key=RGAPI-3ba7525b-e0fc-4be2-86a4-58750debf565")
response.raise_for_status()

print(response.json()["info"])

puuid = "1ryf4QieWJNGsHACMIkwCNt2s08RNjz3CMNuWgnyw7DHJb7hddaK3pJKMQbadlVxvzUSdDcpz9qOgg"
match_id = "EUW1_6336043681"


