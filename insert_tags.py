import os
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database configuration
DB_NAME = "550_1"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # replace with actual password
DB_HOST = "localhost"

# Directory containing JSON files
DATA_DIR = "Top 10000 tags"
LOG_FILE = "insertion_log.txt"
LAST_PROCESSED_FILE = "last_successful_file.txt"

# Connect to the PostgreSQL database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = conn.cursor()

# Create log entry
def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")
    print(message)

# Load last processed file to resume
def load_last_processed_file():
    if os.path.exists(LAST_PROCESSED_FILE):
        with open(LAST_PROCESSED_FILE, "r") as file:
            return file.read().strip()
    return None

# Save the last processed file to resume if interrupted
def save_last_processed_file(filename):
    with open(LAST_PROCESSED_FILE, "w") as file:
        file.write(filename)

# Insert data function
def insert_data():
    last_file = load_last_processed_file()
    start_processing = False if last_file else True

    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".json"):
            if not start_processing:
                if filename == last_file:
                    start_processing = True
                continue

            file_path = os.path.join(DATA_DIR, filename)
            try:
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                
                # Insert each tag and collective into database
                for item in data["items"]:
                    # Insert tag
                    cursor.execute("""
                        INSERT INTO tags (name, count)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING;
                    """, (item["name"], item["count"]))
                    
                    # Insert collectives if available
                    if "collectives" in item:
                        for collective in item["collectives"]:
                            # Insert collective
                            cursor.execute("""
                                INSERT INTO collectives (collective_name)
                                VALUES (%s)
                                ON CONFLICT (collective_name) DO NOTHING;
                            """, (collective["name"],))
                            
                            # Get collective_id
                            cursor.execute("SELECT collective_id FROM collectives WHERE collective_name = %s", (collective["name"],))
                            collective_id = cursor.fetchone()[0]

                            # Get tag_id
                            cursor.execute("SELECT tag_id FROM tags WHERE name = %s", (item["name"],))
                            tag_id = cursor.fetchone()[0]

                            # Insert into tag_collectives
                            cursor.execute("""
                                INSERT INTO tag_collectives (tag_id, collective_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING;
                            """, (tag_id, collective_id))

                conn.commit()  # Commit after processing each file
                log_message(f"Successfully processed {filename}")
                save_last_processed_file(filename)

            except Exception as e:
                conn.rollback()  # Rollback in case of error
                log_message(f"Error processing {filename}: {e}")
                break  # Stop processing on error

# Run the insertion process
try:
    insert_data()
finally:
    cursor.close()
    conn.close()
