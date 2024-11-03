# data_fetcher.py

import pandas as pd
from sqlalchemy import create_engine
import logging

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database configuration using SQLAlchemy
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/550_1"
engine = create_engine(DATABASE_URL)

def fetch_sunburst_data():
    """Fetch and process data for the Sunburst chart."""
    try:
        # Queries to fetch collectives and tags
        query_collectives = "SELECT * FROM collectives;"
        query_tags = """
        SELECT tags.tag_id, tags.name AS tag_name, tags.count, tag_collectives.collective_id
        FROM tags
        JOIN tag_collectives ON tags.tag_id = tag_collectives.tag_id;
        """
        
        # Fetch data
        collectives = pd.read_sql(query_collectives, engine)
        tags = pd.read_sql(query_tags, engine)
        logger.info("Data fetched successfully.")

        # Aggregate tags with counts below 10,000
        tags["tag_count"] = tags["count"].where(tags["count"] >= 10000, 0)
        tags.loc[tags["count"] < 10000, "tag_name"] = "Other"
        grouped_tags = tags.groupby(["collective_id", "tag_name"]).agg(
            {"tag_count": "sum"}).reset_index()

        # Merge with collectives and calculate collective total counts
        merged_data = grouped_tags.merge(collectives, on="collective_id")
        merged_data["collective_total_count"] = merged_data.groupby("collective_id")["tag_count"].transform("sum")

        # Rename columns and select necessary data for Sunburst
        merged_data.rename(columns={
            "collective_name": "collective_name",
            "tag_name": "name",
        }, inplace=True)
        sunburst_data = merged_data[["collective_name", "name", "tag_count", "collective_total_count"]]

        logger.info("Sunburst data processed successfully.")
        return sunburst_data

    except Exception as e:
        logger.error(f"Error fetching or processing data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error
