import requests
import json
import time
from traceback import print_exc, format_exc
from datetime import datetime

# Constants
BASE_URL = "https://api.stackexchange.com/2.3/questions"
SITE = "stackoverflow"
PAGE_SIZE = 100
MAX_PAGES = 100  # To get up to 10,000 questions (100 questions * 100 pages)
API_KEY = "rl_c1moaS69vnAxFksfyEy5h8y19"  # Optional, to avoid rate limits
LOG_FILE = "log.txt"

# Logging function
def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")
    print(message)

# Fetch questions and save each page
def fetch_top_voted_questions():
    print("*_**_**_**_**_**_**_**_**_**_**_*")
    print("*_**_**_**_**_**_**_**_**_**_**_*")
    print("Top 10000 Most Voted Questions and Their Tags in StackOverFlow")
    print("*_**_**_**_**_**_**_**_**_**_**_*")
    print("*_**_**_**_**_**_**_**_**_**_**_*")
    
    for page in range(1, MAX_PAGES + 1):
        # Construct the URL for each page
        url = f"{BASE_URL}?order=desc&sort=votes&site={SITE}&pagesize={PAGE_SIZE}&page={page}&key={API_KEY}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON response and save to a file
                data = response.json()
                with open(f"Top Voted Question/{page}.json", "w") as json_file:
                    json.dump(data, json_file, indent=2)
                log_message(f"{datetime.now()} - Page {page}: Success - Status: {response.status_code}")
            else:
                log_message(f"{datetime.now()} - Page {page}: Failed - Status: {response.status_code}")
                # Try to log the JSON content if available
                try:
                    error_json = response.json()
                    log_message(json.dumps(error_json, indent=2))  # Format JSON for readability
                except ValueError:
                    log_message("No JSON content in response.")
                break  # Stop on failure

        except Exception as e:
            log_message(f"{datetime.now()} - Page {page}: Exception occurred - {str(e)}")
            print_exc()
            log_message(format_exc())
            break  # Stop on exception

        # Wait 5 seconds between requests
        time.sleep(5)

# Run the function to start fetching
fetch_top_voted_questions()
