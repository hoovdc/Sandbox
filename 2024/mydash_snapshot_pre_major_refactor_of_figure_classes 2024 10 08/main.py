#file: main.py
import gsheet_ingest
import time_ingest
import goals
import weather_get
import dash_define_figures
import dash_draw_figures

#ingest gsheet data
(habits_tab_data_headers, habits_tab_data, habits_tab_data_full, text_quotes, 
finmkts_tab_data,  df_fin_pers,fit_run_data, fit_weight_data)  = gsheet_ingest.get_gsheet_data()

#convert gsheet data to dataframes
dfs_habits = gsheet_ingest.process_habits(habits_tab_data_headers, habits_tab_data, habits_tab_data_full)
df_finmkts = gsheet_ingest.process_finmkts(finmkts_tab_data)
df_fit_run, df_fit_weight = gsheet_ingest.process_fitness(fit_run_data, fit_weight_data)

#habit dataframes to plotly figures
figs_habits = dash_define_figures.habits_from_df_to_figures(dfs_habits)

#time data:  ingest, build dataframes.  then draw the figures
df_time = time_ingest.get_time_data()
figs_time = dash_define_figures.time_from_df_to_figures(df_time)

#goal data:
fig_goals = goals.goals_input_to_fig()

#get real weather data as dash figure
fig_temp_hr = weather_get.weather_get()

#fake weather data to dataframes
hourly_dataframe, daily_dataframe = dash_define_figures.make_fake_weather_data()

#fake weather dataframes to plotly figures
fig_hr, fig_hr2, fig_day = dash_define_figures.make_weather_figures(hourly_dataframe, daily_dataframe)

#quote data to formatted text area
textarea_quotes = dash_define_figures.quotes_data_to_textarea(text_quotes)

#finance data to plotly figures
fig_finmkts, fig_finmkts_LxD, fig_fin_pers = dash_define_figures.finance_from_df_to_figures(df_finmkts, df_fin_pers)

#fitness data to plotly figure
fig_fit_run, fig_fit_weight = dash_define_figures.fitness_from_df_to_figures(df_fit_run, df_fit_weight)

#define the dash app
dash_app = dash_draw_figures.draw_figures(figs_habits, figs_time, fig_goals, textarea_quotes, fig_fit_run, fig_fit_weight,
                                            fig_temp_hr, fig_hr2, fig_day, fig_finmkts, fig_finmkts_LxD, fig_fin_pers)

#draw the dash app
dash_app.run_server(debug=True)
#dash_app.run_server(debug=True, host='127.0.0.1', port=8081)