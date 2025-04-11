#file: dash_define_figures.py
#Receives data and produces plotly figures

import plotly.graph_objects as go
import plotly.io as pio #for style themes
import dash #for plot layouts
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime

class figs_all:
    def __init__(self):
        self.physical = self.figs_physical()
        self.finance = self.figs_finance()

    class figs_physical:
        def __init__(self):
            self.run = None
            self.weight = None

    class figs_finance:
        def __init__(self):
            self.finmkts = None
            self.finmkts_LxD = None
            self.fin_pers = None

    class figs_weather:
        def __init__(self):
            self.hr = None
            self.hr2 = None
            self.day = None

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
# Update default template to include tight margins
pio.templates["plotly_dark"].layout.update(
    margin=dict(l=30, r=30, t=50, b=50, pad=10)
)

def make_weather_figures(hourly_dataframe, daily_dataframe):
    hourly_export = hourly_dataframe.copy()
    hourly_export.columns = ['date', 'temperature_2m']
    hourly_export = hourly_export.reset_index()

    # Generate chart in Plotly
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(x=hourly_dataframe['date'], y=hourly_dataframe['temperature_2m'], mode='lines'))
    fig_hr.update_layout(
        title="Hourly Temperature",
        yaxis=dict(range=[0, 100])  # Set fixed y-axis range from 0 to 100
    )

    fig_hr2 = go.Figure()
    fig_hr2.add_trace(go.Bar(x=hourly_export.index, y=hourly_export['temperature_2m']))
    fig_hr2.update_layout(title="Dark Mode Bayyybayyyyyy")

    fig_day = go.Figure()
    fig_day.add_trace(go.Scatter(x=daily_dataframe['date'], y=daily_dataframe['sunrise'], mode='markers'))
    fig_day.update_layout(title="Daily Sunrise")

    figs_all.figs_weather.hr = fig_hr
    figs_all.figs_weather.hr2 = fig_hr2
    figs_all.figs_weather.day = fig_day
    return figs_all.figs_weather

def habits_from_df_to_figures(dfs_habits):

    #define a class to contain all the habit figures
    class figs_habits:
        def __init__(self):
            self.heatmap = None
            self.bars = None
            self.line_LxD = None
            self.perhabit_lines_LxD = None
            self.wkday_summary = None
            self.perhabit_summary = None

    figs_habits = figs_habits()  #Create an instance of the class

    month = list(range(1, 13)) # 12 months
    day = list(range(1, 32)) # 31 days

    #define the heatmap figure
    figs_habits.heatmap = go.Figure(data=go.Heatmap(
                    z=dfs_habits.heatmap.values.tolist(),  # convert to list of lists
                    x=day,  
                    y=month,    
                    #set a continuous custom color scale where low values are white and high values are the default plotly dark mode purple
                    colorscale=[[0, 'white'], [1, '#636EFA']],
                    #colorscale='RdYlGn',  # Red is loss, Green is win
                    hoverongaps=False))

    figs_habits.heatmap.update_layout(
        title='Habit Heatmap',
        xaxis=dict(title='Day', range=[1, 31]),
        yaxis=dict(title='Month', range=[dfs_habits.heatmap.shape[0], 1])  # Reverse the range to match the calendar
    )

    #define the bars figure
    #transform the bars dataframe columns to lists
    #x-axis: day in year
    bars_days= dfs_habits.bars["Day in Year"].tolist()
    #y-axis: win and loss percentages
    bars_win = dfs_habits.bars["Win %"].tolist()
    bars_loss = dfs_habits.bars["Loss %"].tolist()

    figs_habits.bars = go.Figure(data=[
        go.Bar(x=bars_days, y=bars_win, marker=dict(color='#636EFA'), name='Won'),
        go.Bar(x=bars_days, y=bars_loss, marker=dict(color='white'), name='Lost')
    ])

    figs_habits.bars.update_layout(
        title='Habit Tracker Win/Loss Time Series',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", xanchor="center", x=0.5),
        bargap=0.00,
        yaxis=dict(tickformat=".0%", range=[0, 1]),
        yaxis2=dict(tickformat=".0%", range=[0, 1], overlaying='y', side='right')
    )
    #define the line_LxD figure
    figs_habits.line_LxD = go.Figure(data=[
        go.Scatter(x=dfs_habits.line_LxD["Day in Year"], y=dfs_habits.line_LxD["Win %"], 
                    line_shape='spline', mode='lines+markers'),
        go.Scatter(x=dfs_habits.line_LxD["Day in Year"], y=dfs_habits.line_LxD["Win % YTD"], 
                line_shape='spline', mode='lines+markers', yaxis='y2',
                    line=dict(color='white', width=2))
    ])

    #Define variables for the min and max values of the Win % YTD data and apply a buffer for plotting on the right axis
    min_ytd = dfs_habits.line_LxD["Win % YTD"].min() * 0.98
    max_ytd = dfs_habits.line_LxD["Win % YTD"].max() * 1.02   

    #update the layout of the line figure to measure the Win % YTD on the right axis with a very narrow range of values
    figs_habits.line_LxD.update_layout(
                        yaxis2=dict(range=[min_ytd, max_ytd], overlaying='y', side='right'),
                        title='Habit Win Rate:  Daily & YTD', showlegend=False,
    )

    #define the perhabit_lines_LxD figure as a series of line plots (scatter plots with lines)
    figs_habits.perhabit_lines_LxD = go.Figure()
    for i in range(0, len(dfs_habits.perhabit_lines_LxD.columns)):
        figs_habits.perhabit_lines_LxD.add_trace(go.Scatter(
            x=dfs_habits.perhabit_lines_LxD.index,
            y=dfs_habits.perhabit_lines_LxD.iloc[:, i],
            mode='lines+markers',
            name=dfs_habits.perhabit_lines_LxD.columns[i],
            line={'color': '#636EFA', 'width': 2}
        ))

    #remove the margin on the left and right sides of the chart
    figs_habits.perhabit_lines_LxD.update_layout(margin=dict(l=0, r=0))

    #define the habit_wkday_summary figure
    figs_habits.wkday_summary = go.Figure()
    figs_habits.wkday_summary.add_trace(go.Bar(x=dfs_habits.wkday_summary['Day of Week'], y=dfs_habits.wkday_summary['Win Rate']))
    figs_habits.wkday_summary.update_layout(title="Day-in-Week Win Rate")
    figs_habits.wkday_summary.update_yaxes(range=[0.5, 1.0])

    #define the habit_perhabit_summary figure
    figs_habits.perhabit_summary = go.Figure()
    figs_habits.perhabit_summary.add_trace(go.Bar(x=dfs_habits.perhabit_summary['Habit'], y=dfs_habits.perhabit_summary['Win Rate']))
    figs_habits.perhabit_summary.update_layout(title="Habit Win Rate")
    figs_habits.perhabit_summary.update_yaxes(range=[0.5, 1.0])

    return figs_habits

def time_from_df_to_figures(df_time):
    """
    This function receives a DataFrame with 'Month', 'Average Daily Hours Blocked', 
    and 'Median Daily Hours Blocked' columns, and returns a class containing two 
    Plotly polar bar charts (wind rose charts) - one for the average daily hours 
    and one for the median daily hours. The radial axis represents hours (0-24),
    and the angular axis represents the calendar months (1-12).
    """

    # Compute the range for the radial axis based on 80% of the minimum and 120% of the maximum
    avg_min = df_time['Average_Daily_Hours_Blocked'].min()
    avg_max = df_time['Average_Daily_Hours_Blocked'].max()
    med_min = df_time['Median_Daily_Hours_Blocked'].min()
    med_max = df_time['Median_Daily_Hours_Blocked'].max()

    radial_min = 0.8 * min(avg_min, med_min)
    radial_max = 1.05 * max(avg_max, med_max)

    # Common layout options for both figures
    common_layout = dict(
        polar=dict(
            radialaxis=dict(
                range=[radial_min, radial_max],
                tickvals=np.linspace(radial_min, radial_max, 3),
                ticktext=[f"{val:.1f}h" for val in np.linspace(radial_min, radial_max, 3)]
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=np.linspace(0, 330, 12),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                direction="clockwise",
                rotation=90
            )
        ),
        template="plotly_dark",  # Shared template
        showlegend=False,  # Disable legend to focus on color axis
        coloraxis=dict(
            colorscale=[[0, "white"], [1, "#636EFA"]],
            colorbar=dict(title="Hours")
        )
    )

    # Define a class to hold the figures
    class TimeFigures:
        def __init__(self):
            # Create polar bar chart for Average Daily Hours using go
            self.fig_avg = go.Figure(go.Barpolar(
                r=df_time['Average_Daily_Hours_Blocked'],
                theta=df_time['Month'] * (360 / 12),  # Spread months correctly across 360 degrees
                marker=dict(color=df_time['Average_Daily_Hours_Blocked'], coloraxis="coloraxis"),
                showlegend=False,
                name="Avg"
            ))
            self.fig_avg.update_layout(common_layout, title="Gcal: Average Daily Hrs per Month")

            # Create polar bar chart for Median Daily Hours using go
            self.fig_median = go.Figure(go.Barpolar(
                r=df_time['Median_Daily_Hours_Blocked'],
                theta=df_time['Month'] * (360 / 12),  # Spread months correctly across 360 degrees
                marker=dict(color=df_time['Median_Daily_Hours_Blocked'], coloraxis="coloraxis"),
                showlegend=False,
                name="Median"
            ))
            self.fig_median.update_layout(common_layout, title="Gcal: Median Daily Hrs per Month")
            #self.fig_median.show()
    # Return an instance of the class containing the figures
    return TimeFigures()



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
def finance_from_df_to_figures(df_finmkts, df_fin_pers):
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
        yaxis=dict(range=[0, max(finmkts_price) * 1.15])  
    )

    fig_finmkts_LxD.update_layout(
        title=f'Daily NASDAQ Closing Price L{LxD}D',
    )

    #create a figure for personal finance data as a line plot
    fig_fin_pers = go.Figure(data=[
        go.Scatter(x=df_fin_pers["Date"], y=df_fin_pers["Value"], mode='lines')
    ])

    fig_fin_pers.update_layout(
        title='Multiple of Max Net Wealth: Monthly',
        margin=dict(l=10, r=10)
    )
    
    figs_all.figs_finance.finmkts = fig_finmkts
    figs_all.figs_finance.finmkts_LxD = fig_finmkts_LxD
    figs_all.figs_finance.fin_pers = fig_fin_pers
    return figs_all.figs_finance

#FITNESS DATA TO PLOTLY FIGURES
def fitness_from_df_to_figures(df_fit_run, df_fit_weight):
   
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
        showbackground=True
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
        bgcolor='#111111'  # This sets the scene background to dark gray
    )
    )

     #create a line plot for fit_weight
    fig_fit_weight = go.Figure(data=[go.Scatter(
        x=df_fit_weight['Date'],
        y=df_fit_weight['Weight (lb)'],
        mode='lines'
    )])


    fig_fit_weight.update_layout(
        title='BodyWeight: Daily',
        xaxis=dict(title='Date', tickformat='%Y'),
        yaxis=dict( title='Weight (lb)',tickmode='linear', ticks='inside', dtick=5)
    )

    figs_all.figs_physical.run = fig_fit_run
    figs_all.figs_physical.weight = fig_fit_weight
    return figs_all.figs_physical


