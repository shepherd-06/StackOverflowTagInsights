# data_fetcher_trend.py

import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/550_1"
engine = create_engine(DATABASE_URL)

def get_all_collectives():
    """Fetch all available collectives for the dropdown selection."""
    query = "SELECT DISTINCT collective_name FROM collectives ORDER BY collective_name;"
    collectives = pd.read_sql(query, engine)
    return collectives['collective_name'].tolist()

def fetch_tags_from_collectives(selected_collectives):
    """Fetch all tags associated with the selected collectives."""
    placeholders = ', '.join(['%s'] * len(selected_collectives))
    query = f"""
    SELECT tags.name AS tag_name
    FROM tags
    JOIN tag_collectives ON tags.tag_id = tag_collectives.tag_id
    JOIN collectives ON tag_collectives.collective_id = collectives.collective_id
    WHERE collectives.collective_name IN ({placeholders});
    """
    tags_df = pd.read_sql(query, engine, params=tuple(selected_collectives))
    logger.info("Fetched Tags from Collectives data:")
    logger.info(tags_df.head())
    return tags_df['tag_name'].tolist()

def fetch_trend_data(selected_collectives, start_date, end_date):
    """Fetch trend data based on tags within the selected collectives and date range."""
    # Get all tags associated with the selected collectives
    tags = fetch_tags_from_collectives(selected_collectives)
    if not tags:
        logger.warning("No tags found for the selected collectives.")
        return pd.DataFrame()  # Return an empty DataFrame if no tags are found

    placeholders = ', '.join(['%s'] * len(tags))  # Prepare placeholders for SQL IN clause
    query = f"""
    SELECT tags.name AS tag, topvotedquestions.creation_date, COUNT(topvotedquestions.question_id) AS question_count
    FROM topvotedquestions
    JOIN questiontags ON topvotedquestions.question_id = questiontags.question_id
    JOIN tags ON questiontags.tag_id = tags.tag_id
    WHERE tags.name IN ({placeholders}) 
      AND topvotedquestions.creation_date BETWEEN %s AND %s
    GROUP BY tags.name, topvotedquestions.creation_date
    ORDER BY topvotedquestions.creation_date;
    """
    params = tuple(tags) + (start_date, end_date)
    data = pd.read_sql(query, engine, params=params)
    
    # Log the data to verify
    logger.info("Fetched trend data:")
    logger.info(data.head())
    
    return data
