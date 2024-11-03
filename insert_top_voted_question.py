import os
import json
import psycopg2
import logging
from datetime import datetime
import sys

# Database connection parameters
DB_NAME = "550_1"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Directory containing the JSON files
DATA_DIR = "Top Voted Question"

# Set up logging
logging.basicConfig(filename="data_import.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def log_and_print(message):
    """Helper function to log and print messages with timestamps."""
    logging.info(message)
    print(f"{datetime.now()} - {message}")

# Database connection
try:
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = connection.cursor()
    log_and_print("Database connection established.")
except Exception as e:
    log_and_print(f"Failed to connect to the database: {e}")
    exit()

# Insert data function
def insert_data(data):
    """Insert question data into the TopVotedQuestions and QuestionTags tables."""
    try:
        # Insert into TopVotedQuestions
        cursor.execute("""
            INSERT INTO TopVotedQuestions (question_id, view_count, is_answered, answer_count, score, creation_date, link, title)
            VALUES (%s, %s, %s, %s, %s, TO_TIMESTAMP(%s), %s, %s)
            ON CONFLICT (question_id) DO NOTHING
        """, (
            data["question_id"],
            data["view_count"],
            data["is_answered"],
            data["answer_count"],
            data["score"],
            data["creation_date"],
            data["link"],
            data["title"]
        ))
        
        # Insert into QuestionTags
        for tag in data["tags"]:
            cursor.execute("""
                INSERT INTO QuestionTags (question_id, tag_id)
                SELECT %s, tag_id FROM tags WHERE name = %s
                ON CONFLICT (question_id, tag_id) DO NOTHING
            """, (data["question_id"], tag))
        
        connection.commit()
    except Exception as e:
        connection.rollback()
        log_and_print(f"Error inserting data for question ID {data['question_id']}: {e}")
        sys.exit(-255)

# Process files
for filename in range(1, 101):  # Files numbered from 1 to 100
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    if not os.path.isfile(filepath):
        log_and_print(f"File {filename}.json not found.")
        continue
    
    log_and_print(f"Processing file: {filename}.json")
    
    # Load and insert data from JSON file
    try:
        with open(filepath, "r") as file:
            content = json.load(file)
            for item in content["items"]:
                # Clean data and insert
                item_data = {
                    "question_id": item["question_id"],
                    "view_count": item["view_count"],
                    "is_answered": item["is_answered"],
                    "answer_count": item["answer_count"],
                    "score": item["score"],
                    "creation_date": item["creation_date"],
                    "link": item["link"],
                    "title": item["title"],
                    "tags": item["tags"]
                }
                insert_data(item_data)
                log_and_print(f"Inserted question ID {item_data['question_id']} successfully.")
    except Exception as e:
        log_and_print(f"Error processing file {filename}.json: {e}")

# Close database connection
cursor.close()
connection.close()
log_and_print("Database connection closed.")
