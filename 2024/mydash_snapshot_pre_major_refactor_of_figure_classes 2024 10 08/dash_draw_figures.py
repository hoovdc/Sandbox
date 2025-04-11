#file: dash_draw_multiarea.py
#A variation on dash draw where multiple data sources are arranged on the same dash

import plotly.graph_objects as go
import plotly.io as pio #for style themes
import dash #for plot layouts
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import datetime
#import threading

def make_fake_weather_data():
    # Create some tiny placeholder data to test the code below
    hourly_dataframe = pd.DataFrame({
        'date': pd.date_range(start='1/1/2023', periods=24, freq='h'),
        'temperature_2m': [60 + i for i in range(24)]
    })
    daily_dataframe = pd.DataFrame({
        'date': pd.date_range(start='1/1/2023', periods=7, freq='D'),
        'sunrise': ['07:30', '07:31', '07:29', '07:33', '07:34', '07:35', '07:36']
    })
    return hourly_dataframe, daily_dataframe

pio.templates.default = "plotly_dark"  # Set default style template for plots

def get_time_day_date_styles():
    return {
        'marginTop': '0px',
        'color': 'white',
        'height': '50%',
        'width': '100%',
        'display': 'flex',
        'textAlign': 'center',
        'justifyContent': 'center',
        'alignItems': 'center',
        'backgroundColor': '#111111'
    }

def draw_figures(figs_habits, figs_time, fig_goals, text_quotes, fig_fit_run, fig_fit_weight,
                 fig_temp_hr, fig_hr2, fig_day, fig_finmkts, fig_finmkts_LxD, fig_fin_pers):
    
    dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    #for half-width figures, shrink the margins around each chart
    figs_habits.wkday_summary.update_layout(margin=dict(l=3, r=3))
    figs_habits.perhabit_summary.update_layout(margin=dict(l=3, r=3))

    dash_app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                # Left column content
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=figs_habits.heatmap)), width=2),
                    dbc.Col(dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=figs_habits.wkday_summary))),
                        dbc.Col(html.Div(dcc.Graph(figure=figs_habits.perhabit_summary)))
                    ]), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_fit_weight)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_fit_run)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_temp_hr)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_finmkts)), width=2)
                ]),
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=figs_habits.bars)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=figs_habits.line_LxD)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=figs_time.fig_avg)), width=2),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(html.Div(id='live-update-time', style={'fontSize': 70})),
                            dbc.Col(html.Div(id='live-update-day-date', style={'fontSize': 35}))
                        ], style=get_time_day_date_styles()),
                        dbc.Row(html.Div(text_quotes))
                    ], width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_fin_pers)), width=2),
                    dbc.Col(html.Div(dcc.Graph(figure=fig_finmkts_LxD)), width=2)
                ]),
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=figs_habits.perhabit_lines_LxD)))
                ])
            ], width=9, className="d-flex flex-column", style={'padding': '0', 'margin': '0'}),
            dbc.Col([ #right column
                html.Div(
                    dcc.Graph(figure=fig_goals, style={'height': '100%', 'width': '100%'}),
                    style={'height': '100%'}
                )
            ], width=3, style={'padding': '0', 'margin': '0'})
        ], className="g-0", style={'flex': '1', 'display': 'flex', 'align-items': 'stretch'}),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # In milliseconds
            n_intervals=0
        )
    ], className="g-0", style={
        'backgroundColor': '#000000',
        #align the layout to the top left of the screen
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'transform-origin': 'top left',
        'display': 'flex',
        'flex-direction': 'column',
        'margin': '0',
        'transform': 'scale(0.67)',
        #'transform':  'scale(0.65,0.65)'
        'height': '50vh',
        'width': '148vw',
        #'zoom': '0.8',  # Not a great feature.  Inconsistent across browsers, seeing some issues with it.
    })
    
    @dash_app.callback([Output('live-update-time', 'children'),
                       Output('live-update-day-date', 'children')],
              [Input('interval-component', 'n_intervals')])
    
    def update_metrics(n):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_weekday = datetime.datetime.now().strftime("%A")
        current_day = datetime.datetime.now().strftime("%Y %m %d")
        return current_time, [current_weekday, html.Br(), current_day]
        
    return dash_app
