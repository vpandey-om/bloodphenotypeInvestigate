from dash import dcc, html
from dash_bootstrap_components import Tabs, Tab, Row, Col,Modal, ModalBody, ModalHeader, ModalFooter
from components.plots import create_plot
from utils.helpers import create_table, download_links

# Define the layout
layout = html.Div(
    [
        html.Header(
            [
                html.Img(src="assets/logo.png", className="logo"),
                html.H1("Barseq Data Explorer", className="app-title"),
            ],
            className="header"
        ),
   

        # Search Box Section
        html.Div(
            [
                html.Label("Search Genes:", className="form-label"),
                dcc.Dropdown(
                    id="search-box",
                    options=[],  # Will be populated dynamically
                    placeholder="Type to search by gene, gene_name, gene_product, or current_version_ID...",
                    multi=False,
                    searchable=True,
                    style={"width": "100%"},
                ),
            ],
            className="container my-3",
        ),
        
        Tabs(
            [
                Tab(
                    label="Plot",
                    tab_id="plot-tab",
                    children=[
                        Row(
                            [
                                Col(create_plot(), width=9, className="tab-content"),
                                Col(
                                    html.Div(
                                        id="plot-details",
                                        className="p-3 border bg-light",
                                        children=html.P("Select a point to view details here."),
                                    ),
                                    width=3,
                                ),
                            ],
                            className="mt-3",
                        ),
                    ],
                ),
                Tab(
                    label="Table",
                    tab_id="table-tab",
                    children=[
                        Row(
                            [
                                Col(
                                    html.Div(
                                        [
                                            create_table(),
                                            html.Br(),
                                            download_links(),
                                        ],
                                        className="tab-content",
                                    ),
                                    width=9,
                                ),
                                Col(
                                    html.Div(
                                        id="table-details",
                                        className="p-3 border bg-light",
                                        children=html.P("Select a row to view details here."),
                                    ),
                                    width=3,
                                ),
                            ],
                            className="mt-3",
                        ),
                    ],
                ),
            ]
        ),

        # Modal for More Details
        # Modal for More Details
        Modal(
            [
                ModalHeader("Gene Details", id="modal-header"),
                ModalBody(
                    [
                        html.Div(
                            [
                                
                                html.Div(
                                    id="modal-table",  # This will hold the dynamically generated table
                                    children="Details will appear here.",
                                ),
                                dcc.Dropdown(
                                    id="experiment-dropdown",
                                    options=[],  # Populated dynamically based on available experiments
                                    placeholder="Filter by experiment...",
                                    style={"margin-bottom": "15px"},
                                    value=None,  # This will be updated dynamically
                                ),
                                html.Div(id="experiment-keys-output", style={"display": "none","margin-top": "20px"}),
                                
                        html.H4("Plot of barcode ratios in the population", style={"marginTop": "20px"}),
                        dcc.Graph(id="modal-figure-ratios", style={"marginTop": "10px"}),

                        html.H4("Normalized growth rate at each timepoint/mouse", style={"marginTop": "20px"}),
                        dcc.Graph(id="modal-figure-abs", style={"marginTop": "10px"}),

                        html.H4("Estimated accuracy of fitnesses at each timepoint/mouse", style={"marginTop": "20px"}),
                        dcc.Graph(id="modal-figure-inversevar", style={"marginTop": "10px"}),
                        
                            ]
                        )
                    ]
                ),
                ModalFooter(
                    html.Button("Close", id="close-modal", className="btn btn-secondary")
                ),
            ],
            id="details-modal",
            is_open=False,
            size="lg",  # Make the modal large
            scrollable=True,  # Allow scrolling inside the modal
        ),

    ],
    className="main-container"
)
