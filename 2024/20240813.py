#file: dash_draw_multiarea.py
#A variation on dash draw where multiple data sources are arranged on the same dash
#when functioning, move this code into dash_draw.py

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

def habits_from_df_to_figures(df_habit_heatmap,df_habit_data_bars, df_habit_data_line_LxD, df_perhabit_lines_LxD,
                               df_habit_wkday_summary, df_habit_perhabit_summary):

    month = list(range(1, 13)) # 12 months
    day = list(range(1, 32)) # 31 days

    #define the heatmap figure
    fig_habits_heat = go.Figure(data=go.Heatmap(
                    z=df_habit_heatmap.values.tolist(),  # convert to list of lists
                    x=day,  
                    y=month,    
                    #set a continuous custom color scale where low values are white and high values are the default plotly dark mode purple
                    colorscale=[[0, 'white'], [1, '#636EFA']],
                    #colorscale='RdYlGn',  # Red is loss, Green is win
                    hoverongaps=False))

    fig_habits_heat.update_layout(
        title='Habit Heatmap',
        xaxis=dict(title='Day', range=[1, 31]),
        yaxis=dict(title='Month', range=[12, 1])  # Reverse the range to match the calendar
    )

    #define the bars figure
    #transform the bars dataframe columns to lists
    #x-axis: day in year
    bars_days= df_habit_data_bars["Day in Year"].tolist()
    #y-axis: win and loss percentages
    bars_win = df_habit_data_bars["Win %"].tolist()
    bars_loss = df_habit_data_bars["Loss %"].tolist()

    fig_habits_bars = go.Figure(data=[
        go.Bar(x=bars_days, y=bars_win, marker=dict(color='#636EFA'), name='Won'),
        go.Bar(x=bars_days, y=bars_loss, marker=dict(color='white'), name='Lost')
    ])

    fig_habits_bars.update_layout(
        title='Habit Tracker Win/Loss Time Series',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", xanchor="center", x=0.5),
        bargap=0.00,
        yaxis=dict(tickformat=".0%", range=[0, 1]),
        yaxis2=dict(tickformat=".0%", range=[0, 1], overlaying='y', side='right')
    )
    #define the line_LxD figure
    fig_habits_line_LxD = go.Figure(data=[
        go.Scatter(x=df_habit_data_line_LxD["Day in Year"], y=df_habit_data_line_LxD["Win %"], 
                    line_shape='spline', mode='lines+markers'),
        go.Scatter(x=df_habit_data_line_LxD["Day in Year"], y=df_habit_data_line_LxD["Win % YTD"], 
                line_shape='spline', mode='lines+markers', yaxis='y2',
                    line=dict(color='white', width=2))
    ])

    #Define variables for the min and max values of the Win % YTD data and apply a buffer for plotting on the right axis
    min_ytd = df_habit_data_line_LxD["Win % YTD"].min() * 0.98
    max_ytd = df_habit_data_line_LxD["Win % YTD"].max() * 1.02   

    #update the layout of the line figure to measure the Win % YTD on the right axis with a very narrow range of values
    fig_habits_line_LxD.update_layout(
        yaxis2=dict(range=[min_ytd, max_ytd], overlaying='y', side='right'),
                    title='Habit Win Rate:  Daily & YTD', showlegend=False,
    )

    #define the perhabit_lines_LxD figure as a series of line plots (scatter plots with lines)
    fig_perhabit_lines_LxD = go.Figure()
    for i in range(1, len(df_perhabit_lines_LxD.columns)):
        fig_perhabit_lines_LxD.add_trace(go.Scatter(
            x=df_perhabit_lines_LxD.index, 
            y=df_perhabit_lines_LxD.iloc[:, i], 
            mode='lines+markers', 
            name=df_perhabit_lines_LxD.columns[i])
            #name each series of lines by the column names in the dataframe
            
        )


    #define the habit_wkday_summary figure
    fig_habit_wkday_summary = go.Figure()
    fig_habit_wkday_summary.add_trace(go.Bar(x=df_habit_wkday_summary['Day of Week'], y=df_habit_wkday_summary['Win Rate']))
    fig_habit_wkday_summary.update_layout(title="Day-in-Week Win Rate")
    fig_habit_wkday_summary.update_yaxes(range=[0.5, 1.0])

    #define the habit_perhabit_summary figure
    fig_habit_perhabit_summary = go.Figure()
    fig_habit_perhabit_summary.add_trace(go.Bar(x=df_habit_perhabit_summary['Habit'], y=df_habit_perhabit_summary['Win Rate']))
    fig_habit_perhabit_summary.update_layout(title="Habit Win Rate")
    fig_habit_perhabit_summary.update_yaxes(range=[0.5, 1.0])

    #fig_habits_heat.show()
    return fig_habits_heat, fig_habits_bars, fig_habits_line_LxD,  fig_perhabit_lines_LxD, \
           fig_habit_wkday_summary, fig_habit_perhabit_summary
    

def quotes_data_to_textarea(text_quotes):
    #create a dcc.Textarea to display quotes
    return dcc.Textarea(
        id='textarea-quotes',
        #value='\n\Textarea content initialized\nwith multiple lines of text',
        value = text_quotes,
        style={'width': '100%', 'height': 250,
            'fontSize': 25, 
            'color': '#ffffff',  # Text color
            'backgroundColor': '#111111', 
            'borderColor': '#111111', 
            'textAlign': 'center', #alignment
            #Note that I have added paragraph returns to the quote data in gsheet_ingest.py
            #Those paragraph returns should be considered when adjusting vertical alignment
            'flexDirection': 'column',
            'justifyContent': 'flex-start',  # Align text to the top
            'marginTop': '0px', 'paddingTop': '0px', 'marginBottom': '0px', 'paddingBottom': '0px'
            },
    )

#FINMKTS DATA TO PLOTLY FIGURE
def finmkts_from_df_to_figures(df_finmkts):
    #transform the finmkts dataframe columns to lists
    finmkts_days= df_finmkts["Date"].tolist()     #x-axis: Date
    finmkts_price = df_finmkts["Price"].tolist()    #y-axis: Price

    #create lists with just the last x days of data
    LxD = 45 #last x days
    finmkts_days_LxD = finmkts_days[ (-1 * LxD) :] 
    finmkts_price_LxD = finmkts_price[ (-1 * LxD) :]

    fig_finmkts = go.Figure(data=[
        go.Scatter(x=finmkts_days, y=finmkts_price, mode='lines')
    ])

    fig_finmkts_LxD = go.Figure(data=[
        go.Scatter(x=finmkts_days_LxD, y=finmkts_price_LxD, mode='lines')
    ])

    fig_finmkts.update_layout(
        title='Daily NASDAQ Closing Price L24M',
    )

    fig_finmkts_LxD.update_layout(
        title=f'Daily NASDAQ Closing Price L{LxD}M',
    )
    
    return fig_finmkts, fig_finmkts_LxD

#FITNESS DATA TO PLOTLY FIGURES
def fitness_from_df_to_figures(df_fit_run):
    # Prepare data for Plotly
    df_fit_run['Timestamp'] = df_fit_run['Date'].map(pd.Timestamp.timestamp)
    x = df_fit_run['Timestamp'].values  # Convert dates to timestamps
    y = pd.to_numeric(df_fit_run['Distance (mi)']).values
    z = df_fit_run['Pace (min/mi)'].values

    # Create a 3D scatter plot
    fig_fit_run = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=5,
            color=z,  # Color by z value
            colorscale='Viridis',  # Choose a colorscale
            opacity=0.9
        ),
        text=df_fit_run['Date'].dt.strftime('%Y-%m-%d'),  # Add dates as hover text
        hovertemplate='Date: %{text}<br>Distance: %{y:.2f} mi<br>Pace: %{customdata:.2f} min/mi'
    )])

    # Define the common axis style
    common_axis_style = dict(
        gridcolor='gray',  # Dark gridline color
        zerolinecolor='gray',  # Dark zero line color
        showbackground=True,
        backgroundcolor='black'
    )    
    
    fig_fit_run.update_layout(
    template='plotly_dark',
    title='Pace Over Time and Distance',
    autosize=True,
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(
        xaxis=dict(
            title='Date',
            tickvals=x[::10],  # Show every 10th tick
            ticktext=df_fit_run['Date'].dt.strftime('%Y-%m-%d')[::10],  # Corresponding tick labels
            **common_axis_style  # Apply common style
        ),
        yaxis=dict(
            title='Distance (mi)',
            **common_axis_style  # Apply common style
        ),
        zaxis=dict(
            title='Pace (min/mi)',
             autorange='reversed',  # Reverse the z-axis to show faster paces at the top
            **common_axis_style  # Apply common style
        ),
        bgcolor='black'
    ),
    plot_bgcolor='black',
    paper_bgcolor='black'
    )

    return fig_fit_run

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

def draw_figures(fig_habits_heat, fig_habits_bars, 
                 fig_habits_line_LxD,  fig_perhabit_lines_LxD,
                 fig_habit_wkday_summary, fig_habit_perhabit_summary,
                 text_quotes, fig_fit_run,
                 fig_temp_hr, fig_hr2, fig_day, fig_finmkts, fig_finmkts_LxD):
                
    dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    #for half-width figures, shrink the margins around each chart
    fig_habit_wkday_summary.update_layout(margin=dict(l=3, r=3))
    fig_habit_perhabit_summary.update_layout(margin=dict(l=3, r=3))

    dash_app.layout = html.Div([
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig_habits_heat))),
            dbc.Col([
                dbc.Row([
                 dbc.Col(html.Div(dcc.Graph(figure=fig_habit_wkday_summary))),
                 dbc.Col(html.Div(dcc.Graph(figure=fig_habit_perhabit_summary)))
                ])
            ]),
            dbc.Col(html.Div(dcc.Graph(figure=fig_fit_run))),
            dbc.Col(html.Div(dcc.Graph(figure=fig_temp_hr))),
            dbc.Col(html.Div(dcc.Graph(figure=fig_finmkts)))
        ]),
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig_habits_bars))),
            dbc.Col(html.Div(dcc.Graph(figure=fig_habits_line_LxD))),
            dbc.Col([
               dbc.Row([
                    dbc.Col(html.Div(id='live-update-time', style={'fontSize': 70})),
                    dbc.Col(html.Div(id='live-update-day-date', style={'fontSize': 35}))
                    ], style=get_time_day_date_styles()),
                dbc.Row(html.Div(text_quotes))
            ]),
            #dbc.Col(html.Div(dcc.Graph(figure=fig_hr))),
            dbc.Col(html.Div(dcc.Graph(figure=fig_day))),
            dbc.Col(html.Div(dcc.Graph(figure=fig_finmkts_LxD)))
        ]),
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure= fig_perhabit_lines_LxD)))
        ]),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ], style={'backgroundColor': '#000000', 'height': '100vh', 'width': '125vw',
                  'transform': 'scale(0.75)',  # Adjust the scale to zoom out the entire layout
                  'transform-origin': 'top left'  # Set the origin of the transformation
      }
    )
    
    @dash_app.callback([Output('live-update-time', 'children'),
                       Output('live-update-day-date', 'children')],
              [Input('interval-component', 'n_intervals')])
    
    def update_metrics(n):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_weekday = datetime.datetime.now().strftime("%A")
        current_day = datetime.datetime.now().strftime("%Y %m %d")
        return current_time, [current_weekday, html.Br(), current_day]
        
    return dash_app
