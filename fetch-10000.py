import requests
import time
import json
import os
from datetime import datetime

# Constants
PAGE_SIZE = 100
TOTAL_TAGS = 10000
MAX_PAGES = TOTAL_TAGS // PAGE_SIZE
BASE_URL = "https://api.stackexchange.com/2.3/tags"
LOG_FILE = "log.txt"
LAST_PAGE_FILE = "last_page.txt"
API_KEY = "rl_c1moaS69vnAxFksfyEy5h8y19"

# Function to log messages
def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")
    print(message)

# Function to save the last fetched page number
def save_last_page(page):
    with open(LAST_PAGE_FILE, "w") as file:
        file.write(str(page))

# Function to load the last fetched page number
def load_last_page():
    if os.path.exists(LAST_PAGE_FILE):
        with open(LAST_PAGE_FILE, "r") as file:
            return int(file.read().strip())
    return 1

# Main function to fetch tags
def fetch_tags():
    page = load_last_page()  # Start from the last saved page if it exists
    while page <= MAX_PAGES:
        url = f"{BASE_URL}?order=desc&sort=popular&site=stackoverflow&page={page}&pagesize={PAGE_SIZE}&key={API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Save data to a JSON file (e.g., 1.json, 2.json, etc.)
                with open(f"{page}.json", "w") as json_file:
                    json.dump(data, json_file, indent=2)

                log_message(f"{datetime.now()} - Page {page}: Success - Status: {response.status_code}")
                save_last_page(page)  # Update the last page fetched
                page += 1  # Move to the next page
            else:
                log_message(f"Page {page}: Failed with status code {response.status_code}")
                # Try to log the JSON content if available
                try:
                    error_json = response.json()
                    log_message(json.dumps(error_json, indent=2))  # Format JSON for readability
                except ValueError:
                    log_message("No JSON content in response.")
                break  # Stop on failure

        except Exception as e:
            log_message(f"Page {page}: Exception occurred - {str(e)}")
            break  # Stop on exception

        # Wait for 5 seconds between requests
        time.sleep(5)

# Run the fetch_tags function
fetch_tags()
