import plotly
import plotly.io as pio #for style themes
import dash #for plot layouts
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

data = [[1, 20], [2, 19], [3, 18], [4, 17], [5, 16], [6, 15], [7, 14], [8, 13], [9, 12], [10, 11], 
        [11, 10], [12, 9], [13, 8], [14, 7], [15, 6], [16, 5], [17, 4], [18, 3], [19, 2], [20, 1]]

df = pd.DataFrame(data, columns=['col1', 'col2'])

'''
NEXT MAKE THIS WORK FOR HABITS AS A HEATMAP.  2 GOALS:
(1) GET HABITS DATA WORKING IN MY PROJECT
(2) GET MY NEW PROJECT STRUCTURE WORKING (NEW SET OF FILES AND FUNCTIONS)
USE THIS AS A TEMPLATE ("HEATMAP WITH DATETIME AXIS" SECTION)
https://plotly.com/python/heatmaps/
'''

#generate chart in Plotly Express
#set default style template for plots
pio.templates.default = "plotly_dark"
fig_hr = plotly.line(df, x = 'date', y = 'temperature_2m') #causes error
#fig_hr = px.line(hourly_export, x = 0, y = 1, title = "dark mode bayyybayyyyyy")
fig_hr2 = plotly.bar(df, x = 0, y = 1, title = "dark mode bayyybayyyyyy")
fig_day = plotly.scatter(df, x = 'date', y = 'sunrise')

dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

dash_app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig_hr), style={'width': '100%', 'height': '400px'})),
            dbc.Col(html.Div(dcc.Graph(figure=fig_hr2), style={'width': '100%', 'height': '400px'}))
        ]),
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig_day), style={'width': '100%', 'height': '400px'}))
        ])
    ], fluid=True)
	],
	 style={'backgroundColor': '#000000'}  
)

#the point of the first line of the block directly below is to ensure that the Dash server is only started when the script is run directly, and not when it's imported by another script.
if __name__ == '__main__':
	dash_app.run_server(debug=True)

#fig_hr.show()


