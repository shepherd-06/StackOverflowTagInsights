# app_trend.py

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
import data_fetcher_trend  # Import the updated data fetching module

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Collective Popularity Trends"

# Layout with description, disclaimer, and graph elements
app.layout = dbc.Container([
    # Title and Description Section
    html.Div([
        html.H1("Collective Popularity Trends", className="display-4 text-center my-4"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P("This dashboard provides a visualization of tag popularity over time within different programming collectives.",
                           className="lead"),

                    html.P("How to Use:", className="font-weight-bold mt-4"),
                    html.Ul([
                        html.Li("Select up to 7 collectives from the dropdown to view trends for all tags within those collectives."),
                        html.Li("Use the date range picker to specify the time period for the data."),
                        html.Li("The streamgraph shows the frequency of questions related to each tag within the selected collectives over time."),
                        html.Li("Hover over each area to see detailed information on the tag and question count at each time point.")
                    ]),

                    html.P("Disclaimer: This dashboard is designed for exploratory data analysis and may not meet all accessibility standards. "
                           "Trends are derived from available data in the `topvotedquestions` table, and the accuracy of insights is subject to the completeness and quality of that data. "
                           "For an accessible experience, consider alternative data visualizations or consult with a data specialist if needed. This chart was generated with the assistance of ChatGPT",
                           className="text-muted mt-4")
                ], width=10),
            ], justify="center")
        ], className="mb-4")
    ]),

    # Dropdown, Date Picker, and Streamgraph with Loading Spinner
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="collective-search",
                options=[{'label': collective, 'value': collective} for collective in data_fetcher_trend.get_all_collectives()],
                multi=True,
                placeholder="Search collectives...",
                style={"width": "100%"},
                className="mb-3"
            ),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=pd.to_datetime("2021-01-01"),
                max_date_allowed=pd.to_datetime("2023-12-31"),
                start_date=pd.to_datetime("2021-01-01"),
                end_date=pd.to_datetime("2023-12-31"),
                className="mb-3"
            ),
            html.Div(id="collective-limit-warning", className="text-danger mt-2")
        ], width=6)
    ], justify="center"),

    # Loading spinner and streamgraph
    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=[
            dcc.Graph(id="streamgraph")
        ],
        fullscreen=True
    )
], fluid=True)

# Callback to update the streamgraph based on selected collectives and date range
@app.callback(
    [Output("streamgraph", "figure"), Output("collective-limit-warning", "children")],
    [Input("collective-search", "value"), Input("date-range", "start_date"), Input("date-range", "end_date")]
)
def update_streamgraph(selected_collectives, start_date, end_date):
    # Check if the selected collectives exceed the limit of 7
    if selected_collectives and len(selected_collectives) > 7:
        warning_msg = "You can select up to 7 collectives only. Please reduce your selection."
        return go.Figure(), warning_msg

    if not selected_collectives:
        return go.Figure(), ""  # Return an empty figure if no collectives are selected

    # Fetch data based on selected collectives and date range
    data = data_fetcher_trend.fetch_trend_data(selected_collectives, start_date, end_date)
    
    # Log the data passed to the graph
    if data.empty:
        logger.warning("No data available for the selected collectives and date range.")
    else:
        logger.info("Data for streamgraph:")
        logger.info(data.head())

    # Return an empty figure if there's no data
    if data.empty:
        return go.Figure(), ""

    # Prepare the streamgraph using Plotly's area chart
    fig = px.area(
        data,
        x="creation_date",
        y="question_count",
        color="tag",
        title="Tag Popularity Over Time",
        line_group="tag"
    )
    
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        xaxis_title="Creation Date",
        yaxis_title="Question Count",
    )
    return fig, ""  # Return the figure with no warning message if the collective limit is within range

if __name__ == "__main__":
    app.run_server(debug=True)
