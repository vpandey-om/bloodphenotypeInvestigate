from dash import dash_table, dcc, html
import pandas as pd
import json
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


# Load the dataset
try:
    data = pd.read_csv("data/Barseq20250124.csv")
except FileNotFoundError:
    data = pd.DataFrame(
        {"gene": [], "Relative.Growth.Rate": [], "Confidence": [], "phenotype": []}
    )
    print("Warning: Dataset not found. Using an empty DataFrame.")


# Load the dataset
try:
    df = pd.read_csv("data/temp.csv")
except FileNotFoundError:
    print("Warning: Dataset not found. Using an empty DataFrame.")


# Function to create a DataTable


def create_table():
    """
    Generates a Dash DataTable that displays all columns from the dataset.
    """
    return dash_table.DataTable(
        id="data-table",
        columns=[
            {"name": col, "id": col} for col in data.columns  # Include all columns dynamically
        ],
        data=data.to_dict("records"),  # Convert DataFrame to records
        page_size=20,  # Number of rows per page
        style_table={
            "overflowX": "auto",  # Enable horizontal scrolling
            "overflowY": "auto",  # Enable vertical scrolling
            "height": "400px",    # Fixed height for vertical scroll
            "maxWidth": "100%",   # Ensure the table does not exceed container width
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "textAlign": "center"
        },
        style_cell={
            "textAlign": "left",
            "padding": "5px",
            "whiteSpace": "normal",  # Allow text wrapping for better visibility
            "minWidth": "120px",    # Force horizontal scrolling with a minimum column width
            "maxWidth": "250px",    # Optional: Prevent overly wide columns
            "overflow": "hidden",   # Hide overflowing text
            "textOverflow": "ellipsis"  # Add "..." for overflowing text
        },
        row_selectable="single",  # Enable single row selection
        sort_action="native",  # Enable sorting
        filter_action="native",  # Enable filtering
        style_data_conditional=[
            {
                "if": {"state": "selected"},  # Style the selected row
                "backgroundColor": "#e8f4f8",
                "border": "1px solid #99c2ff"
            }
        ],
    )

# Function to create download links
def download_links():
    """
    Generates download links for CSV and Excel exports.
    """
    return html.Div(
        [
            dcc.Download(id="download-csv"),  # For CSV download
            dcc.Download(id="download-xlsx"),  # For Excel download
            html.Button("Download CSV", id="btn-csv", className="btn btn-primary mx-1"),
            html.Button("Download Excel", id="btn-xlsx", className="btn btn-success mx-1"),
        ],
        className="d-flex justify-content-start align-items-center mt-3"
    )

# Function to export data
def send_data_frame(export_func, filename, **kwargs):
    """
    Wrapper for Dash's send_data_frame function to export data.
    """
    return dcc.send_data_frame(export_func, filename, **kwargs)

# Function to display selected gene details
def get_selected_row_details(click_data, selected_rows, data):
    """
    Generate details of the selected row or clicked scatter plot point.

    Args:
        click_data: Data from scatter plot click event.
        selected_rows: List of selected row indices from the DataTable.
        data: DataFrame containing the dataset.

    Returns:
        An HTML Div containing the gene details or a default message.
    """
    # Handle scatter plot click event
    if click_data:
        point = click_data["points"][0]
        gene = point.get("customdata", [None])[0]  # Retrieve the custom data (gene)
        if gene and gene in data["gene"].values:  # Ensure the gene exists in the data
            row_data = data[data["gene"] == gene].iloc[0]
            return _generate_gene_details(row_data)

    # Handle table row selection event
    if selected_rows:
        row_idx = selected_rows[0] if selected_rows else None
        if row_idx is not None and row_idx < len(data):
            row_data = data.iloc[row_idx]
            return _generate_gene_details(row_data)

    # Default message when no selection is made
    return html.Div(
        [
            html.P("Select a gene by clicking a point on the plot or selecting a row in the table."),
        ],
        className="p-2 text-muted"
    )

def _generate_gene_details(row_data):
    """
    Helper function to generate the HTML content for gene details.

    Args:
        row_data: The row of the dataset corresponding to the selected gene.

    Returns:
        An HTML Div containing the details of the gene.
    """
    return html.Div(
        [
            html.P(f"Gene: {row_data['gene']}", className="font-weight-bold"),
            html.P(f"Growth Rate: {row_data['Relative.Growth.Rate']:.2f}"),
            html.P(f"Confidence: {row_data['Confidence']:.2f}"),
            html.P(f"Phenotype: {row_data['phenotype']}"),
            html.Button(
                "More Details",
                id="more-details-button",
                className="btn btn-info mt-2",
            ),
        ],
        className="p-3 border bg-light rounded"
    )








def get_gene_details_from_csv(gene_id, file_path="data/temp.csv"):
    """
    Read a CSV file and extract details for a specific gene.
    Parameters:
        gene_id (str): The gene ID to filter.
        file_path (str): The path to the CSV file.
    Returns:
        tuple: A DataFrame with relevant columns (renamed and ordered) and the full DataFrame.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        # print("CSV File Loaded Successfully")  # Debug: Confirm file load
        # print(f"Columns in CSV: {df.columns.tolist()}")  # Debug: Check CSV columns
        # print(f"Gene ID to filter: {gene_id}")  # Debug: Confirm gene being searched

        # Ensure the 'fitness' column exists
        if "fitness" not in df.columns:
            raise KeyError("Column 'fitness' not found in the CSV file.")

        # Filter the DataFrame for the specific gene and drop rows with NaN in 'fitness'
        filtered_df = df[(df["gene"] == gene_id) & (df["fitness"].notna())]

        # Reorder columns for display
        if not filtered_df.empty:
            filtered_df = filtered_df[["experiment", "fitness", "lower", "upper"]]
            # Rename 'fitness' to 'Relative Growth Rate'
            filtered_df = filtered_df.rename(columns={"fitness": "Relative Growth Rate"})

        # print(f"Filtered Data for Gene {gene_id}:")  # Debug: Check filtered data
        # print(filtered_df)

        # Return the filtered DataFrame and the full DataFrame
        return filtered_df, df
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return pd.DataFrame(), pd.DataFrame()
    except KeyError as e:
        print(f"KeyError: {e}")
        raise KeyError(f"Missing column in CSV file: {e}")






def get_experiment_keys(selected_experiment, gene, order_file="data/experiment_order.txt", json_file="data/arrays.json"):
    """
    Fetch dictionary keys from arrays.json based on the selected experiment's index and plot data for a specific gene.
    
    Parameters:
        selected_experiment (str): The experiment name selected by the user.
        gene (str): The gene name for plotting.
        order_file (str): Path to the experiment order file.
        json_file (str): Path to the JSON file containing the list of dictionaries.
        
    Returns:
        list: Keys of the dictionary at the selected experiment's index.
        Plotly Figures: Ratios plot, Abs fitness plot, and Inverse variance plot.
    """
    try:
        # Read the experiment order file and map experiments to their line index
        with open(order_file, "r") as f:
            experiment_order = {line.strip(): idx for idx, line in enumerate(f) if line.strip()}

        # Get the index for the selected experiment
        if selected_experiment not in experiment_order:
            raise ValueError(f"Experiment '{selected_experiment}' not found in {order_file}.")
        selected_index = experiment_order[selected_experiment]

        # Load the JSON file
        with open(json_file, "r") as f:
            array_data = json.load(f)

        # Get the dictionary at the specified index
        if selected_index >= len(array_data):
            raise IndexError(f"Index {selected_index} is out of range for {json_file}.")
        selected_dict = array_data[selected_index]

        # Create the plots
        fig_ratios = create_ratios_plot(selected_dict, gene_name=gene)
        fig_abs = create_abs_fitness_plot(selected_dict, gene_name=gene)
        fig_inversevar = create_inversevar_plot(selected_dict, gene_name=gene)
        
        # Return the keys of the dictionary and the plots
        return list(selected_dict.keys()), fig_ratios, fig_abs, fig_inversevar

    except Exception as e:
        print(f"Error: {e}")
        return [], {}, {}, {}





def create_ratios_plot(selected_dict, gene_name="Selected Gene"):
    """
    Create a Plotly plot using ratios and ratiovar from the selected dictionary.
    
    Parameters:
        selected_dict (dict): Dictionary containing ratios and ratiovar arrays.
        gene_name (str): Name of the gene for the plot title.
    
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    try:
        # Extract ratios and ratiovar from the dictionary
        ratios_array = np.array(selected_dict.get("ratios"))
        ratiovar_array = np.array(selected_dict.get("ratiosvar"))

        # Ensure arrays are 3D (mouse x day x id)
        if ratios_array.ndim != 3 or ratiovar_array.ndim != 3:
            raise ValueError("Ratios and ratiovar arrays must be 3-dimensional.")

        # Dynamically generate day column names based on the number of days
        num_days = ratios_array.shape[1]
        day_columns = [f"day{i+1}" for i in range(num_days)]

        # Extract data for the first id (similar to the R function)
        ratios = pd.DataFrame(ratios_array[:, :, 0], columns=day_columns)
        ratiovar = pd.DataFrame(ratiovar_array[:, :, 0], columns=day_columns)

        # Melt data to long format (mouse, day, ratio, ratiovar)
        ratios = ratios.reset_index().melt(id_vars="index", var_name="day", value_name="ratio")
        ratiovar = ratiovar.reset_index().melt(id_vars="index", var_name="day", value_name="ratiovar")

        # Combine ratios and ratiovar
        merged = pd.merge(ratios, ratiovar, on=["index", "day"])

        # Ensure numeric values in 'ratio' and 'ratiovar'
        merged["ratio"] = pd.to_numeric(merged["ratio"], errors="coerce")
        merged["ratiovar"] = pd.to_numeric(merged["ratiovar"], errors="coerce")

        # Drop rows with NaN values in 'ratio'
        merged = merged.dropna(subset=["ratio", "ratiovar"])

        # Calculate standard deviation and confidence intervals
        merged["sd"] = np.sqrt(merged["ratiovar"])  # Standard deviation
        merged["ratiomin"] = merged["ratio"] - merged["sd"] * 2
        merged["ratiomax"] = merged["ratio"] + merged["sd"] * 2

        # Format days (convert to numeric)
        merged["day"] = merged["day"].str.extract(r"(\d+)").astype(int)
        merged["day"] += 3  # Offset by 3 as in the R function

        # Filter to include only days 4 to 8
        merged = merged[merged["day"].isin([4, 5, 6, 7, 8])]
        
        # Define custom colors for the mice
        custom_colors = {
            0: "red",   # Mouse 1
            1: "blue",  # Mouse 2
            2: "green"  # Mouse 3
        }

        # Create the plot
        fig = go.Figure()

        # Add scatter points and line traces for each mouse
        for mouse in merged["index"].unique():
            mouse_data = merged[merged["index"] == mouse]

            fig.add_trace(go.Scatter(
                x=mouse_data["day"],
                y=mouse_data["ratio"],
                mode="markers+lines",
                marker=dict(color=custom_colors.get(mouse, "black")),  # Default to black if mouse index exceeds 2
                line=dict(color=custom_colors.get(mouse, "black")),
                name=f"Mouse {mouse + 1}"  # Mouse numbers start from 1
            ))

        # Format layout
        fig.update_layout(
            title=f"Barcode Abundance for {gene_name}",
            yaxis=dict(title="Barcode Abundance (%)", tickformat=".1%"),
            xaxis=dict(title="Day", dtick=1, tickvals=[4, 5, 6, 7, 8]),  # Force ticks for days 4 to 8
            legend_title="Mouse",
            showlegend=True
        )

        return fig

    except Exception as e:
        print(f"Error creating ratios plot: {e}")
        return None


def create_abs_fitness_plot(selected_dict, gene_name="Selected Gene"):
    """
    Create a Plotly bar plot using absfitness from the selected dictionary without error bars.
    
    Parameters:
        selected_dict (dict): Dictionary containing absfitness and absfitnessvar arrays.
        gene_name (str): Name of the gene for the plot title.
    
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    try:
        # Extract absfitness from the dictionary
        abs_array = np.array(selected_dict.get("absfitness"))

        # Ensure the array is 3D (mouse x day x id)
        if abs_array.ndim != 3:
            raise ValueError("absfitness array must be 3-dimensional.")

        # Dynamically generate day column names based on the number of days
        num_days = abs_array.shape[1]
        day_columns = [f"day{i+1}" for i in range(num_days)]

        # Extract data for the first id (similar to the R function)
        abs_df = pd.DataFrame(abs_array[:, :, 0], columns=day_columns)

        # Melt data to long format (mouse, day, absfitness)
        abs_df = abs_df.reset_index().melt(id_vars="index", var_name="day", value_name="abs")

        # Ensure numeric values in 'abs'
        abs_df["abs"] = pd.to_numeric(abs_df["abs"], errors="coerce")

        # Drop rows with NaN values in 'abs'
        abs_df = abs_df.dropna(subset=["abs"])

        # Format days (convert to numeric)
        abs_df["day"] = abs_df["day"].str.extract(r"(\d+)").astype(int)
        abs_df["day"] += 4  # Offset by 4 as in the R function

        # Define custom colors for the mice
        custom_colors = {
            0: "red",   # Mouse 1
            1: "blue",  # Mouse 2
            2: "green"  # Mouse 3
        }

        # Create the plot
        fig = go.Figure()

        # Add bar traces for each mouse
        for mouse in abs_df["index"].unique():
            mouse_data = abs_df[abs_df["index"] == mouse]

            fig.add_trace(go.Bar(
                x=mouse_data["day"],
                y=mouse_data["abs"],
                name=f"Mouse {mouse + 1}",
                marker=dict(color=custom_colors.get(mouse, "gray")),
            ))

        # Add a horizontal line at y=1
        # fig.add_shape(
        #     type="line",
        #     x0=min(abs_df["day"]),
        #     x1=max(abs_df["day"]),
        #     y0=1,
        #     y1=1,
        #     line=dict(color="black", width=2, dash="dot"),
        # )

        # Format layout
        fig.update_layout(
            title=f"Normalized Relative Growth Rate for {gene_name}",
            yaxis=dict(title="Normalized Relative Growth Rate"),
            xaxis=dict(title="Day"),
            legend_title="Mouse",
            showlegend=True,
            barmode="group",  # Group bars for each mouse
        )

        return fig

    except Exception as e:
        print(f"Error creating abs fitness plot: {e}")
        return None
    
def create_inversevar_plot(selected_dict, gene_name="Selected Gene"):
    """
    Create a Plotly bar plot for inverse variance (precision) using absfitnessvar from the selected dictionary.
    
    Parameters:
        selected_dict (dict): Dictionary containing absfitnessvar arrays.
        gene_name (str): Name of the gene for the plot title.
    
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    try:
        # Extract absfitnessvar from the dictionary
        absvar_array = np.array(selected_dict.get("absfitnessvar"))

        # Ensure the array is 3D (mouse x day x id)
        if absvar_array.ndim != 3:
            raise ValueError("absfitnessvar array must be 3-dimensional.")

        # Dynamically generate day column names based on the number of days
        num_days = absvar_array.shape[1]
        day_columns = [f"day{i+1}" for i in range(num_days)]

        # Extract data for the first id (similar to the R function)
        absvar_df = pd.DataFrame(absvar_array[:, :, 0], columns=day_columns)

        # Melt data to long format (mouse, day, absfitnessvar)
        absvar_df = absvar_df.reset_index().melt(id_vars="index", var_name="day", value_name="absvar")

        # Ensure numeric values in 'absvar'
        absvar_df["absvar"] = pd.to_numeric(absvar_df["absvar"], errors="coerce")

        # Drop rows with NaN values in 'absvar'
        absvar_df = absvar_df.dropna(subset=["absvar"])

        # Compute inverse variance
        absvar_df["inversevar"] = 1 / absvar_df["absvar"]

        # Format days (convert to numeric)
        absvar_df["day"] = absvar_df["day"].str.extract(r"(\d+)").astype(int)
        absvar_df["day"] += 4  # Offset by 4 as in the R function

        # Define custom colors for the mice
        custom_colors = {
            0: "red",   # Mouse 1
            1: "blue",  # Mouse 2
            2: "green"  # Mouse 3
        }

        # Create the plot
        fig = go.Figure()

        # Add bar traces for each mouse
        for mouse in absvar_df["index"].unique():
            mouse_data = absvar_df[absvar_df["index"] == mouse]

            fig.add_trace(go.Bar(
                x=mouse_data["day"],
                y=mouse_data["inversevar"],
                name=f"Mouse {mouse + 1}",
                marker=dict(color=custom_colors.get(mouse, "gray")),
            ))

        # Format layout
        fig.update_layout(
            title=f"Fitness: {gene_name}",
            yaxis=dict(title="Weight (Precision)", range=[0, absvar_df["inversevar"].max() * 1.1]),
            xaxis=dict(title="Day"),
            legend_title="Mouse",
            showlegend=True,
            barmode="group",  # Group bars for each mouse
        )

        return fig

    except Exception as e:
        print(f"Error creating inverse variance plot: {e}")
        return None
