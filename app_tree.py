# app_tree.py

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
import data_fetcher_tree  # Import the tree data fetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Collapsible Tree Dashboard"
logger.info("Dash app initialized for Collapsible Tree.")

# Layout with Bootstrap for description, disclaimer, and loading spinner
app.layout = dbc.Container([
    # Title and Description Section
    html.Div([
        html.H1("Collapsible Tree of Tags and Questions", className="display-4 text-center my-4"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P("This visualization represents a hierarchical breakdown of programming collectives, tags, and questions.",
                           className="lead"),
                    
                    html.P("Each collective (e.g., 'Mobile Development') is represented as a top-level block. Clicking on a collective "
                           "expands it to show associated tags (e.g., 'android', 'ios'). Clicking on a tag reveals additional question "
                           "statistics, including total questions, top and least voted question scores, and median statistics for votes "
                           "and answer counts.",
                           className="mb-4"),
                    
                    html.P("Interaction Guide:", className="font-weight-bold"),
                    html.Ul([
                        html.Li("Hover over a segment to see the label and value."),
                        html.Li("Click on a collective to expand it and reveal tags."),
                        html.Li("Click on a tag to see detailed question statistics in a bar chart below."),
                        html.Li("The chart is interactive and updates automatically as you explore.")
                    ], className="mb-4"),
                    
                    html.P("Disclaimer: This chart was generated with the assistance of ChatGPT and may not meet all accessibility standards. "
                           "For a fully accessible experience, alternative visualizations may be necessary.",
                           className="text-muted")
                ], width=10)
            ], justify="center")
        ])
    ], className="mb-4"),

    # Tree Visualization with Loading Spinner
    dbc.Container([
        dcc.Loading(
            id="loading-spinner",
            type="circle",  # Loading spinner type
            children=[
                dbc.Container(dcc.Graph(id="collapsible-tree")),
                dbc.Container(id="tree-info", style={"marginTop": "20px"})  # For displaying info on click
            ],
            fullscreen=True  # Show spinner over full content
        )
    ])
], fluid=True)

# Callback to generate the collapsible tree chart
@app.callback(
    Output("collapsible-tree", "figure"),
    Input("collapsible-tree", "id")
)
def update_collapsible_tree(_):
    logger.info("Updating Collapsible Tree chart.")
    data = data_fetcher_tree.fetch_tree_data()
    
    # Convert structured tree data into flat lists for Treemap
    labels = []
    parents = []
    values = []

    # Recursive function to process tree data into flat lists for Treemap
    def process_node(node, parent_name=""):
        labels.append(node["name"])
        parents.append(parent_name)
        
        # Only add values for collectives initially
        if "tags" in node:
            # Collective level, so add total tags as value
            values.append(len(node["tags"]))
            # Do not expand tags/questions initially
            for tag in node["tags"]:
                process_node(tag, node["name"])
        elif "questions" in node:
            # This is a tag node, value is number of questions
            values.append(len(node["questions"]))
            for question in node["questions"]:
                process_node({"name": f"{question['name']} (Score: {question['score']}, Views: {question['views']})"}, node["name"])
        else:
            # This is a question node, no further children
            values.append(None)
    
    for collective in data:
        process_node(collective)

    # Create Treemap with branchvalues set to "remainder" to enable expanding on click
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value",
        branchvalues="remainder"  # This enables collapsing and expanding on click
    ))

    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    logger.info("Collapsible Tree chart updated.")
    return fig

# Callback for displaying additional information on click
@app.callback(
    Output("tree-info", "children"),
    Input("collapsible-tree", "clickData")
)
def display_tree_info(clickData):
    if clickData:
        point = clickData['points'][0]
        label = point['label']
        
        # Fetch statistics if the selected item is a tag
        statistics = data_fetcher_tree.fetch_tag_statistics(label)
        if statistics:
            # Create a bar chart for the statistics
            fig = go.Figure(data=[
                go.Bar(
                    x=["Total Questions", "Top Voted Question Score", "Least Voted Question Score", "Median Vote", "Median Answer Count"],
                    y=[
                        statistics["total_questions"],
                        statistics["top_voted_question"],
                        statistics["least_voted_question"],
                        statistics["median_vote"],
                        statistics["median_answer_count"]
                    ],
                    marker=dict(color=["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]),
                    text=[f"{value}" for value in [
                        statistics["total_questions"],
                        statistics["top_voted_question"],
                        statistics["least_voted_question"],
                        statistics["median_vote"],
                        statistics["median_answer_count"]
                    ]],
                    textposition="auto"
                )
            ])

            fig.update_layout(
                title=f"Statistics for '{label}'",
                xaxis_title="Statistics",
                yaxis_title="Values",
                margin=dict(t=50, b=30)
            )

            return dcc.Graph(figure=fig)

        else:
            # If no data available, display a message
            return html.Div(f"No additional data available for {label}.")

    # Default message if no item is selected
    return html.Div("Click on a segment to view details")

# Run the server
if __name__ == "__main__":
    logger.info("Starting Dash server for Collapsible Tree.")
    app.run_server(debug=True)
    logger.info("Dash server for Collapsible Tree is running.")
