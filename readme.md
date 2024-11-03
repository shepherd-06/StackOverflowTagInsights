# StackOverflow Tag Insights

StackOverflowTagInsights is an interactive data visualization project designed to analyze trends and popularity of tags, questions, and programming collectives on Stack Overflow. This project gathers data from the Stack Exchange API and uses various dashboards to display hierarchical, temporal, and comparative insights into the Stack Overflow ecosystem.

## Table of Contents

* Features
* Installation
* Database Structure
* Known Issues

## Features

* **API Integration**: Collects data from Stack Overflow on the most popular tags and top-voted questions.
* **Database Storage**: Structured PostgreSQL database stores hierarchical relationships between tags, questions, and collectives.
* **Interactive Visualizations**: Provides various dashboards using Plotly and Dash to explore tag and question data interactively.
* **Insights into Tag Popularity**: Allows users to explore relationships between tags and collectives, view tag trends over time, and analyze popularity shifts within programming topics.

## Installation

1. Clone the Repository:

```bash
git clone https://github.com/shepherd-06/StackOverflowTagInsights.git
cd StackOverflowTagInsights
```

2. Set Up Virtual Environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install Dependencies:

```bash
pip install -r requirements.txt
```

4. Configure PostgreSQL Database

* Create a PostgreSQL database and user for this project.
* Import the database schema provided in the `database/database_dump.sql` file.

5. Run the Application:

```bash
python app.py         # For Sunburst Chart
python app_tree.py    # For Collapsible Tree Dashboard
python app_trend.py   # For Tag Trend Streamgraph
```

Database Structure

The PostgreSQL database stores data in the following tables:

* Tags: Stores individual tags and their usage counts.
* TopVotedQuestions: Contains metadata about the top questions, such as question ID, title, creation date, score, and view count.
* Collectives: Represents parent tags (collectives) that group multiple related tags.
* TagCollectives: Links individual tags to their parent collectives.
* QuestionTags: Links questions with tags, enabling many-to-many relationships.

## Known Issues

**SQL Query Inconsistencies**: Certain SQL queries may not fully capture the intended relationships, affecting visualization accuracy. Updates to the data-fetching logic are planned.
