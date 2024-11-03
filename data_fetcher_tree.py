# data_fetcher_tree.py

import pandas as pd
from sqlalchemy import create_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database configuration using SQLAlchemy
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/550_1"
engine = create_engine(DATABASE_URL)

def fetch_tree_data():
    """Fetch and process data for the collapsible tree."""
    try:
        # Queries to fetch collectives, tags, and topvotedquestions with tag connections
        query_collectives = "SELECT * FROM collectives;"
        query_tags = """
        SELECT tags.tag_id, tags.name AS tag_name, tag_collectives.collective_id
        FROM tags
        JOIN tag_collectives ON tags.tag_id = tag_collectives.tag_id;
        """
        query_questions = """
        SELECT topvotedquestions.question_id, topvotedquestions.title, topvotedquestions.score,
               topvotedquestions.view_count, questiontags.tag_id
        FROM topvotedquestions
        JOIN questiontags ON topvotedquestions.question_id = questiontags.question_id;
        """
        
        # Fetch data
        collectives = pd.read_sql(query_collectives, engine)
        tags = pd.read_sql(query_tags, engine)
        questions = pd.read_sql(query_questions, engine)
        logger.info("Data fetched successfully for collapsible tree.")

        # Merge tags with collectives and questions with tags to create a hierarchy
        tags_with_collectives = tags.merge(collectives, on="collective_id")
        questions_with_tags = questions.merge(tags, on="tag_id")

        # Create a tree structure: Collectives > Tags > Questions
        tree_data = []
        for _, collective in collectives.iterrows():
            # Find tags within this collective
            collective_tags = tags_with_collectives[tags_with_collectives["collective_id"] == collective["collective_id"]]
            tags_list = []

            for _, tag in collective_tags.iterrows():
                # Find questions within this tag
                tag_questions = questions_with_tags[questions_with_tags["tag_id"] == tag["tag_id"]]
                questions_list = [
                    {
                        "name": question["title"],
                        "score": question["score"],
                        "views": question["view_count"]
                    }
                    for _, question in tag_questions.iterrows()
                ]
                
                tags_list.append({
                    "name": tag["tag_name"],
                    "questions": questions_list
                })

            # Append collective with its tags and questions
            tree_data.append({
                "name": collective["collective_name"],
                "tags": tags_list
            })

        logger.info("Tree data structured successfully.")
        return tree_data

    except Exception as e:
        logger.error(f"Error fetching or processing data for tree: {e}")
        return []  # Return empty list in case of error


def fetch_tag_statistics(tag_name):
    """Fetch statistical information for a specific tag."""
    try:
        query = f"""
        SELECT topvotedquestions.score, topvotedquestions.answer_count
        FROM topvotedquestions
        JOIN questiontags ON topvotedquestions.question_id = questiontags.question_id
        JOIN tags ON questiontags.tag_id = tags.tag_id
        WHERE tags.name = %s
        """
        
        # Fetch data for the selected tag
        data = pd.read_sql(query, engine, params=(tag_name,))
        if data.empty:
            logger.warning(f"No data found for tag: {tag_name}")
            return None
        
        # Calculate statistics
        statistics = {
            "total_questions": len(data),
            "top_voted_question": data["score"].max(),
            "least_voted_question": data["score"].min(),
            "median_vote": data["score"].median(),
            "median_answer_count": data["answer_count"].median()
        }

        logger.info(f"Statistics for tag '{tag_name}' fetched successfully.")
        return statistics

    except Exception as e:
        logger.error(f"Error fetching statistics for tag '{tag_name}': {e}")
        return None
