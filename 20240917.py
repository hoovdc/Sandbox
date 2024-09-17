#File: Goal_Sankey_Standalone.py
#Originally generated by ChatGPT 4o, refined by Claude 3.5 Sonnet in Cursor IDE

import pandas as pd
import plotly.graph_objects as go

# Load the CSV file
file_path = r'Data\Time Data\Goal Data\Goal, Task, and Time Tree - Structure and Synthetic Data - Data_Summary_Flat.csv'
df_clean = pd.read_csv(file_path, skiprows=2)  # Skip the first two rows

# Extract the relevant columns for the Sankey chart
df_sankey = df_clean[['From_Node_Tier', 'From_Node_ID', 'From_Node_Name', 'To_Node_ID', 'To_Node_Name', 'Edge Weight']].dropna()

# Get unique node names and map them to indices
nodes = pd.concat([df_sankey['From_Node_Name'], df_sankey['To_Node_Name']]).unique()
node_dict = {node: i for i, node in enumerate(nodes)}

# Map node names to indices for Sankey chart
df_sankey['source'] = df_sankey['From_Node_Name'].map(node_dict)
df_sankey['target'] = df_sankey['To_Node_Name'].map(node_dict)

# Define node labels and links
labels = list(node_dict.keys())
sources = df_sankey['source'].tolist()
targets = df_sankey['target'].tolist()
values = df_sankey['Edge Weight'].astype(float).tolist()

# Create the node labels with values on two lines
label_with_values = []
for node_name in labels:
    incoming_sum = df_sankey[df_sankey['To_Node_Name'] == node_name]['Edge Weight'].sum()
    outgoing_sum = df_sankey[df_sankey['From_Node_Name'] == node_name]['Edge Weight'].sum()
    value_sum = max(incoming_sum, outgoing_sum)
    label_with_values.append(f"{node_name}<br>{int(value_sum)}hrs")

# Set edge colors based on tier and top-level edges
link_colors = []
for source, target in zip(sources, targets):
    if target not in sources:  # This identifies top-level edges
        link_colors.append("rgba(99, 110, 250, 0.9)")  # Plotly purple with custom opacity. Color is same value as #636EFA
    elif df_sankey.loc[df_sankey['source'] == source, 'From_Node_Tier'].iloc[0] == 0:
        link_colors.append("rgba(99, 110, 250, 0.9)")  # Plotly purple with custom opacity. Color is same value as #636EFA
    else:
        link_colors.append("rgba(192, 192, 192, 0.5)")  # Default gray (with transparency)

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=label_with_values,
        color="gray"  # Use grayscale for nodes
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=link_colors  # Set edge colors based on tier and top-level edges
    )
)])

# Update layout to use plotly_dark template and other style adjustments
fig.update_layout(
    title_text="Task and Goals Sankey Diagram",
    font=dict(size=12, color='white'),
    template='plotly_dark'
)

# Show the updated figure
fig.show()
