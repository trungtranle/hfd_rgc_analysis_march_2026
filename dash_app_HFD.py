from dash import Dash, html, dcc, callback, Output, Input
from matplotlib import figure
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import dash_mantine_components as dmc


app = Dash(__name__)
pio.templates.default = "plotly_white"

df_SMS_CA = pd.read_csv("SMS_CA_HFD_v_control_031526.csv").dropna()

all_cell_reference = pd.read_csv("rgc_types_SMS_reference_table.csv")
new_cell_names = pd.read_excel("mapping_cell_name_to_db_names.xlsx")
mean_SMS_by_type = pd.read_csv("mean_SMS_per_cell_type.csv")
mean_SMS_by_type["cell_type"] = mean_SMS_by_type["cell_type"].replace(
    new_cell_names.set_index("old_name")["new_name"]
)
all_cell_reference["cell_type"] = all_cell_reference["cell_type"].replace(
    new_cell_names.set_index("old_name")["new_name"]
)
sms_vc_on_alpha = pd.read_csv("SMS_VC_on_alpha_HDF_and_chow.csv")
sms_vc_on_alpha_reference = pd.read_csv("SMS_VC_on_alpha_reference.csv")


cell_types_in_HFD = df_SMS_CA["cell_type"].unique()
cell_type_options = [{"label": ct, "value": ct} for ct in cell_types_in_HFD]


color_discrete_map = {"HFD": "#EF553B", "chow": "#00CC96"}
app.layout = dmc.MantineProvider(
    [
        html.Div(
            [
                html.Div(
                    dmc.Select(
                        id="cell-type-dropdown",
                        data=cell_type_options,
                        placeholder="Select a cell type",
                        value="ON alpha",
                    )
                ),
                html.Div(
                    dcc.Graph(id="xy-plot"),
                ),
            ],
            style={"width": "49%", "float": "left", "display": "inline-block"},
        ),
        html.Div(
            [dcc.Graph(id="sms_ca_plot"), dcc.Graph(id="sms_ca_off_plot")],
            style={"width": "49%", "float": "right", "display": "inline-block"},
        ),
    ]
)


@callback(
    Output("xy-plot", "figure"),
    Input("cell-type-dropdown", "value"),
)
def update_xy_plot(selected_cell_type):
    filtered_df = df_SMS_CA[df_SMS_CA["cell_type"] == selected_cell_type]
    cells_xy = (
        filtered_df.groupby("cell_unid")[
            ["x", "y", "side", "quadrant", "feeding_condition", "cell_name"]
        ]
        .first()
        .reset_index()
    )
    fig = px.scatter(
        cells_xy,
        x="x",
        y="y",
        color="feeding_condition",
        symbol="side",
        title=f"Spatial Distribution of {selected_cell_type} Cells",
        hover_data=["cell_name"],
    )

    fig.update_traces(marker_size=12)

    return fig


@callback(
    Output("sms_ca_plot", "figure"),
    Output("sms_ca_off_plot", "figure"),
    Input("cell-type-dropdown", "value"),
)
def update_sms_ca_plot(selected_cell_type):
    filtered_df = df_SMS_CA[df_SMS_CA["cell_type"] == selected_cell_type]
    reference_df = all_cell_reference[
        all_cell_reference["cell_type"] == selected_cell_type
    ]
    fig = go.Figure()
    for cell_new_id in reference_df["cell_new_id"].unique():
        cell_data = reference_df[reference_df["cell_new_id"] == cell_new_id]
        if not cell_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=cell_data["spot_size"],
                    y=cell_data["on_spikes"],
                    mode="lines",
                    opacity=0.5,
                    line=dict(color="#636EFA", width=0.2),
                    showlegend=False,
                )
            )

    for cell_unid in filtered_df["dataset_number"].unique():
        cell_data = filtered_df[filtered_df["dataset_number"] == cell_unid]
        if not cell_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=cell_data["spot_sizes"],
                    y=cell_data["spikes_stim_mean"],
                    mode="lines",
                    line=dict(
                        color=color_discrete_map.get(
                            cell_data["feeding_condition"].iloc[0]
                        ),
                        width=1,
                    ),
                    marker=dict(size=8),
                    name=f"{cell_data['cell_name'].iloc[0]} - {cell_data['feeding_condition'].iloc[0]}",
                )
            )

    fig.add_trace(
        go.Scatter(
            x=mean_SMS_by_type[mean_SMS_by_type["cell_type"] == selected_cell_type][
                "size_bin"
            ],
            y=mean_SMS_by_type[mean_SMS_by_type["cell_type"] == selected_cell_type][
                "ON_mean"
            ],
            mode="lines",
            line=dict(color="#636EFA", width=4),
            name="Mean ON response",
        )
    )

    fig.update_xaxes(title_text="Spot Size (um)", range=[0, 1200])
    fig.update_layout(
        title=dict(text=f"ON response - {selected_cell_type} Cells", x=0.5)
    )

    fig_off = go.Figure()
    for cell_new_id in reference_df["cell_new_id"].unique():
        cell_data = reference_df[reference_df["cell_new_id"] == cell_new_id]
        if not cell_data.empty:
            fig_off.add_trace(
                go.Scatter(
                    x=cell_data["spot_size"],
                    y=cell_data["off_spikes"],
                    mode="lines",
                    opacity=0.5,
                    line=dict(color="blue", width=0.2),
                    showlegend=False,
                )
            )
    fig_off.update_xaxes(title_text="Spot Size (um)", range=[0, 1200])
    fig_off.update_layout(
        title=dict(text=f"OFF response - {selected_cell_type} Cells", x=0.5)
    )

    for cell_unid in filtered_df["dataset_number"].unique():
        cell_data = filtered_df[filtered_df["dataset_number"] == cell_unid]
        if not cell_data.empty:
            fig_off.add_trace(
                go.Scatter(
                    x=cell_data["spot_sizes"],
                    y=cell_data["spikes_tail_mean"],
                    mode="lines",
                    line=dict(
                        color=color_discrete_map.get(
                            cell_data["feeding_condition"].iloc[0]
                        ),
                        width=1,
                    ),
                    marker=dict(size=8),
                    name=f"{cell_data['cell_name'].iloc[0]} - {cell_data['feeding_condition'].iloc[0]}",
                )
            )

    fig_off.add_trace(
        go.Scatter(
            x=mean_SMS_by_type[mean_SMS_by_type["cell_type"] == selected_cell_type][
                "size_bin"
            ],
            y=mean_SMS_by_type[mean_SMS_by_type["cell_type"] == selected_cell_type][
                "OFF_mean"
            ],
            mode="lines",
            line=dict(color="#636EFA", width=4),
            name="Mean OFF response",
        )
    )
    return fig, fig_off


if __name__ == "__main__":
    app.run(debug=True)
