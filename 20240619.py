#file: dash_draw_multiarea.py
#A variation on dash draw where multiple data sources are arranged on the same dash
#when functioning, move this code into dash_draw.py

import plotly.graph_objects as go
import plotly.io as pio #for style themes
import dash #for plot layouts
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
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

# Set default style template for plots
pio.templates.default = "plotly_dark"

def make_weather_figures(hourly_dataframe, daily_dataframe):
    hourly_export = hourly_dataframe.copy()
    hourly_export.columns = ['date', 'temperature_2m']
    hourly_export = hourly_export.reset_index()

    # Generate chart in Plotly
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(x=hourly_dataframe['date'], y=hourly_dataframe['temperature_2m'], mode='lines'))
    fig_hr.update_layout(title="Hourly Temperature")

    fig_hr2 = go.Figure()
    fig_hr2.add_trace(go.Bar(x=hourly_export.index, y=hourly_export['temperature_2m']))
    fig_hr2.update_layout(title="Dark Mode Bayyybayyyyyy")

    fig_day = go.Figure()
    fig_day.add_trace(go.Scatter(x=daily_dataframe['date'], y=daily_dataframe['sunrise'], mode='markers'))
    fig_day.update_layout(title="Daily Sunrise")
    return(fig_hr, fig_hr2, fig_day)

def habits_from_df_to_figures(df_habit_heatmap):

    month = list(range(1, 13)) # 12 months
    day = list(range(1, 32)) # 31 days

    fig_habits = go.Figure(data=go.Heatmap(
                    z=df_habit_heatmap.values.tolist(),  # convert to list of lists
                    x=month,  
                    y=day,    
                    colorscale='Greens',
                    hoverongaps=False))

    fig_habits.update_layout(
        title='Habit Tracker Test Plot',
        xaxis=dict(title='Month', range=[1, 12]),
        yaxis=dict(title='Day', autorange='reversed')
    )

    #fig_habits.show()

    return fig_habits

def draw_figures(fig_habits, fig_hr, fig_hr2, fig_day):
    dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
      
    dash_app.layout = html.Div([
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig_habits)), width=6, style={'height': '800px'}),
            dbc.Col([
                dbc.Row(html.Div(dcc.Graph(figure=fig_hr2)), style={'height': '400px'}),
                dbc.Row(html.Div(dcc.Graph(figure=fig_day)), style={'height': '400px'})
            ], width=6)
        ])
    ], style={'backgroundColor': '#000000'})

    return dash_app