from dash import Dash, Input, Output, html, State,dcc
import dash_bootstrap_components as dbc
import pandas as pd
from components.layout import layout
from components.plots import create_plot
from utils.helpers import (send_data_frame, get_selected_row_details,get_gene_details_from_csv,get_experiment_keys)
import dash
# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Barseq Data Explorer"
server = app.server  # 👈 This line is crucial!
# Load the dataset
try:
    data = pd.read_csv("data/Barseq20250124.csv")
except FileNotFoundError:
    data = pd.DataFrame(
        {"gene": [], "gene_name": [], "gene_product": [], "current_version_ID": [],
         "Relative.Growth.Rate": [], "Confidence": [], "phenotype": []}
    )
    print("Warning: Dataset not found. Using an empty DataFrame.")

# Set the layout
app.layout = html.Div([
    layout,
    dcc.Store(id="selected-gene-store")  # Store for the selected gene
])

# Callback to populate the search dropdown options
# Callback to populate the dropdown options
@app.callback(
    Output("search-box", "options"),
    Input("search-box", "search_value"),
)
def update_search_options(search_value):
    """
    Dynamically update dropdown options based on user input.
    """
    if not search_value:
        # Add an "All" option when no search value is provided
        return [{"label": "All", "value": "all"}]

    matching_rows = data[
        data["gene"].str.contains(search_value, case=False, na=False)
        | data["gene_name"].str.contains(search_value, case=False, na=False)
        | data["gene_product"].str.contains(search_value, case=False, na=False)
        | data["current_version_ID"].str.contains(search_value, case=False, na=False)
    ]
    options = [
        {"label": f"{row['gene']} ({row['gene_name']} - {row['gene_product']})", "value": row["gene"]}
        for _, row in matching_rows.iterrows()
    ]
    return [{"label": "All", "value": "all"}] + options  # Include "All" as the first option


@app.callback(
    [
        Output("scatter-plot", "figure"),  # Update the scatter plot
        Output("plot-details", "children"),  # Update the plot details section
        Output("table-details", "children"),  # Update the table details section
        Output("data-table", "data"),  # Update the table data
        Output("selected-gene-store", "data"),  
    ],
    [
        Input("search-box", "value"),  # Search box selection
        Input("scatter-plot", "clickData"),  # Scatter plot click
        Input("data-table", "selected_rows"),  # Table row selection
    ],
)
def update_details(selected_gene, click_data, selected_rows):
    """
    Consolidate updates for the scatter plot, plot details, and table details.
    """
    ctx = dash.callback_context
    fig = create_plot().figure  # Default scatter plot

    # Default details and table data
    plot_details = html.P("Select a point to view details here.")
    table_details = html.P("Select a row to view details here.")
    filtered_table_data = data.to_dict("records")  # Default to full dataset
    stored_gene = None  # Default if no gene is selected

    # Determine the trigger
    if not ctx.triggered:
        return fig, plot_details, table_details, filtered_table_data,stored_gene

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle search box selection
    if trigger_id == "search-box" and selected_gene:
        filtered_data = data[data["gene"] == selected_gene]
        if not filtered_data.empty:
            # Extract phenotype color dynamically from the base figure
            phenotype = filtered_data["phenotype"].iloc[0]
            color_map = {trace.name: trace.marker.color for trace in fig.data}  # Map phenotype to colors
            point_color = color_map.get(phenotype, "blue")  # Default to 'blue' if phenotype not found
            
            # Make all points in the background lighter
            for trace in fig.data:
                trace.marker.opacity = 0.2  # Set background point opacity
            
            # Add highlighted marker
            fig.add_scatter(
                x=filtered_data["Relative.Growth.Rate"],
                y=filtered_data["Confidence"],
                mode="markers",
                marker=dict(size=20, color=point_color, opacity=1),  # Highlighted point with full opacity
                name="Selected Gene",
                hoverinfo="skip",  # Prevent duplicate hover info
            )
            # Update plot and table details
            plot_details = get_selected_row_details(None, [filtered_data.index[0]], data)
            # Filter table to show only the selected gene
            filtered_table_data = filtered_data.to_dict("records")
            stored_gene = selected_gene

    # Handle scatter plot click
    elif trigger_id == "scatter-plot" and click_data:
        plot_details = get_selected_row_details(click_data, [], data)
        gene_from_click = click_data["points"][0]["customdata"][0]
        stored_gene = gene_from_click
    # Handle table row selection
    elif trigger_id == "data-table" and selected_rows:
        selected_row_index = selected_rows[0]
        gene_from_table = data.iloc[selected_row_index]["gene"] 
        table_details = get_selected_row_details(None, selected_rows, data)
        stored_gene = gene_from_table
    return fig, plot_details, table_details, filtered_table_data,stored_gene

# Callback for downloading CSV
@app.callback(
    Output("download-csv", "data"),
    Input("btn-csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return send_data_frame(data.to_csv, "Barseq_Data.csv", index=False)

# Callback for downloading Excel
@app.callback(
    Output("download-xlsx", "data"),
    Input("btn-xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def download_xlsx(n_clicks):
    return send_data_frame(data.to_excel, "Barseq_Data.xlsx", index=False)


@app.callback(
    [
        Output("details-modal", "is_open"),          # Toggle modal open/close
        Output("experiment-dropdown", "options"),   # Populate dropdown with experiments
        Output("experiment-dropdown", "value"),     # Reset dropdown value on modal open
        Output("modal-table", "children"),          # Populate table with filtered details
    ],
    [Input("more-details-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [
        State("selected-gene-store", "data"),       # Access the selected gene
        State("experiment-dropdown", "value"),     # Get the selected experiment
    ],
    prevent_initial_call=True,
)
def toggle_modal(open_click, close_click, stored_gene, selected_experiment):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, [], None, ""

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle opening the modal
    if trigger_id == "more-details-button" and open_click:
        if open_click > 0:
            if stored_gene:
                # Fetch gene details from CSV
                filtered_df, full_df = get_gene_details_from_csv(stored_gene, file_path="data/temp.csv")

                if not filtered_df.empty:
                    # Generate unique experiment options for dropdown
                    experiment_options = [
                        {"label": exp, "value": exp}
                        for exp in sorted(filtered_df["experiment"].unique())
                        ]
                    # Automatically select the first experiment if available
                    first_experiment = experiment_options[0]["value"] if experiment_options else None


                    # Reset dropdown value and regenerate the table for the full dataset
                    formatted_table = html.Table(
                        [
                            html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns])),
                            html.Tbody(
                                [
                                    html.Tr(
                                        [
                                            html.Td(f"{value:.2f}" if isinstance(value, (int, float)) else value)
                                            for value in row
                                        ]
                                    )
                                    for row in filtered_df.itertuples(index=False, name=None)
                                ]
                            ),
                        ],
                        className="table table-striped",
                    )

                    return True, experiment_options, first_experiment, formatted_table

                # If no data is found for the gene
                return True, [], None, f"No details found for gene: {stored_gene}"

    # Handle closing the modal
    if trigger_id == "close-modal" and close_click:
        return False, [], None, ""

    # Default: Reset state
    return False, [], None, ""



@app.callback(
    [Output("experiment-keys-output", "children"), 
     Output("modal-figure-ratios", "figure"), 
     Output("modal-figure-abs", "figure"),
     Output("modal-figure-inversevar", "figure")],
    [Input("experiment-dropdown", "value")],
    [State("selected-gene-store", "data")]
)
def display_experiment_keys(selected_experiment, gene):
    if not selected_experiment:
        return "Please select an experiment.", {}, {}, {}  # Return empty figures

    if not gene:
        return "Please select a gene first.", {}, {}, {}  # Return empty figures

    # Get the keys and the figures for the selected experiment and gene
    keys, fig_ratios, fig_abs, fig_inversevar = get_experiment_keys(selected_experiment, gene=gene)
    if keys:
        # Display the keys and render the figures
        keys_output = html.Div([
            html.P(f"Keys for selected experiment and gene: {', '.join(keys)}"),
        ])
        return keys_output, fig_ratios, fig_abs, fig_inversevar

    # If no keys are found, display a message and return empty figures
    return "No keys found for the selected experiment and gene.", {}, {}, {}


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
