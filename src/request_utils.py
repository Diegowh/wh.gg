import requests
import time

BURST_LIMIT = 20
BURST_TIME = 1
SUSTAINED_LIMIT = 100
SUSTAINED_TIME = 120

last_request_time = 0

def throttle():
    global last_request_time
    time_since_last_request = time.time() - last_request_time
    if time_since_last_request < BURST_TIME:
        time.sleep(BURST_TIME - time_since_last_request)
    last_request_time = time.time()

def make_request(url, params):
    throttle()
    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"API rate limit exceeded. Retrying in {retry_after} seconds.")
            time.sleep(retry_after)
            return make_request(url, params)
        else:
            raise Exception(f"Error fetching data from API: {e}")
