# app.py

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import logging
import data_fetcher  # Import the new module for data fetching
import seaborn as sns  # Import seaborn for color palette

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Tag Popularity Dashboard"
logger.info("Dash app initialized.")

# Layout with placeholders for the Sunburst chart and a spinner
app.layout = html.Div([
    html.H1("Tag Popularity Dashboard"),
    
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
