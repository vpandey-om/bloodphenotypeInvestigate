from dash import dcc
import plotly.express as px
import pandas as pd

# Load the dataset
data = pd.read_csv("data/Barseq20250124.csv")

# Define custom colors for phenotypes
phenotype_colors = {
    "Slow": "#636EFA",  # Blue
    "Essential": "#EF553B",  # Red
    "Dispensable": "#00CC96",  # Green
    "Insufficient data": "#000000",  # Purple
    "Fast": "#FFC0CB",  # Orange
}

# Function to create the plot
def create_plot():
    fig = px.scatter(
        data,
        x="Relative.Growth.Rate",
        y="Confidence",
        color="phenotype",
        title="Scatter Plot of Growth Rate vs Confidence",
        labels={"Relative.Growth.Rate": "Growth Rate", "Confidence": "Confidence"},
        template="plotly_white",
        custom_data=["gene"],  # Add 'gene' to custom data for interactivity
        hover_data={"gene": True, "Relative.Growth.Rate": ":.2f", "Confidence": ":.2f"},  # Format hover data
        color_discrete_map=phenotype_colors,  # Apply custom colors
    )
    fig.update_traces(marker=dict(size=6, opacity=1))  # Default marker size and opacity
    return dcc.Graph(
        id="scatter-plot",  # Add an ID for callback reference
        figure=fig
    )
