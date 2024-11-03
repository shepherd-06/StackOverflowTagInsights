# app.py

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import logging
import data_fetcher  # Import the new module for data fetching
import seaborn as sns  # Import seaborn for color palette

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Tag Popularity Dashboard"
logger.info("Dash app initialized.")

# Layout with description, disclaimer, and a Sunburst chart with a loading spinner
app.layout = html.Div([
    # Header and Description Section
    html.Div([
        html.H1("Tag Popularity Dashboard", className="display-4 text-center mb-4"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P("This dashboard provides a hierarchical view of tag popularity across different programming collectives. "
                           "It allows you to explore relationships between collectives and tags and see detailed statistics about each tag's usage.",
                           className="lead"),
                    
                    html.P("How to Use:", className="font-weight-bold mt-4"),
                    html.Ul([
                        html.Li("Hover over a segment in the Sunburst chart to see the label and value."),
                        html.Li("Click on a collective segment to expand it and reveal associated tags."),
                        html.Li("Click on a tag to view detailed information in the panel below."),
                        html.Li("The chart is interactive and updates automatically as you explore.")
                    ]),
                    
                    html.P("Disclaimer: This chart was generated with the assistance of ChatGPT and may not meet all accessibility standards. "
                           "For a fully accessible experience, alternative visualizations may be necessary.",
                           className="text-muted mt-4")
                ], width=10),
            ], justify="center")
        ], className="mb-4")
    ], style={"margin": "30px"}),

    # Tabs with Sunburst Chart and Loading Spinner
    dcc.Tabs([
        dcc.Tab(label="Sunburst Chart", children=[
            dcc.Loading(
                id="loading-spinner",
                type="circle",  # Loading spinner type
                children=[
                    html.Div(dcc.Graph(id="sunburst-chart")),
                    html.Div(id="sunburst-info", style={"marginTop": "20px"})  # For displaying info on click
                ],
                fullscreen=True  # Show spinner over full content
            )
        ]),
    ])
])

# Define callback for Sunburst chart
@app.callback(
    Output("sunburst-chart", "figure"),
    Input("sunburst-chart", "id")
)
def update_sunburst_chart(_):
    logger.info("Updating Sunburst chart.")
    data = data_fetcher.fetch_sunburst_data()
    if data.empty:
        logger.warning("No data found for Sunburst chart.")
    
    # Use a Seaborn color palette for the sunburst chart
    palette = sns.color_palette("Set3", n_colors=len(data["collective_name"].unique()))
    color_map = {collective: f"rgb{tuple(int(x*255) for x in color)}" for collective, color in zip(data["collective_name"].unique(), palette)}

    # Create the Sunburst chart
    fig = px.sunburst(
        data,
        path=['collective_name', 'name'],  # Path defines the hierarchy
        values='tag_count',  # Size of each slice
        color='collective_name',  # Color by collective
        color_discrete_map=color_map  # Use Seaborn palette
    )
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    logger.info("Sunburst chart updated.")
    return fig

# Callback for displaying additional information on click
@app.callback(
    Output("sunburst-info", "children"),
    Input("sunburst-chart", "clickData")
)
def display_sunburst_info(clickData):
    if clickData:
        point = clickData['points'][0]
        collective_name = point['label']
        count = point.get('value', 'N/A')
        
        # Additional info based on click context
        info_text = f"Collective: {collective_name}<br>Tag Count: {count}<br>"
        return html.Div([
            html.H4("Selected Details"),
            html.P(info_text)
        ])
    return html.Div("Click on a segment to view details")

# Run the server
if __name__ == "__main__":
    logger.info("Starting Dash server.")
    app.run_server(debug=True)
    logger.info("Dash server is running.")
