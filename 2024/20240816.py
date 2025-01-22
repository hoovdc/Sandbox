#file: main.py
import gsheet_ingest
import weather_get
import dash_define_figures
import dash_draw_figures

# habits_tab_data  = gsheet_ingest.get_gsheet_habits()
# df_habits = gsheet_ingest.process_habits(habits_tab_data)
# dash_draw_habits.draw(df_habits)


#ingest gsheet data
habits_tab_data_headers, habits_tab_data, habits_tab_data_full, text_quotes, finmkts_tab_data, fit_run_data  = gsheet_ingest.get_gsheet_data()

#convert gsheet data to dataframes
df_habit_heatmap, df_habit_data_bars, df_habit_data_line_LxD, df_perhabit_lines_LxD, \
df_habit_wkday_summary, df_habit_perhabit_summary = \
gsheet_ingest.process_habits(habits_tab_data_headers, habits_tab_data, habits_tab_data_full)
df_finmkts = gsheet_ingest.process_finmkts(finmkts_tab_data)
df_fit_run = gsheet_ingest.process_fitness(fit_run_data)

#habit dataframes to plotly figures
fig_habits_heat, fig_habits_bars, fig_habits_line_LxD, fig_perhabit_lines_LxD, \
fig_habit_wkday_summary, fig_habit_perhabit_summary = \
dash_define_figures.habits_from_df_to_figures( \
df_habit_heatmap, df_habit_data_bars, df_habit_data_line_LxD, df_perhabit_lines_LxD, \
df_habit_wkday_summary, df_habit_perhabit_summary)

#get real weather data as dash figure
fig_temp_hr = weather_get.weather_get()

#fake weather data to dataframes
hourly_dataframe, daily_dataframe = dash_define_figures.make_fake_weather_data()

#fake weather dataframes to plotly figures
fig_hr, fig_hr2, fig_day = dash_define_figures.make_weather_figures(hourly_dataframe, daily_dataframe)

#quote data to formatted text area
textarea_quotes = dash_define_figures.quotes_data_to_textarea(text_quotes)

#finmkts data to plotly figure
fig_finmkts, fig_finmkts_LxD = dash_define_figures.finmkts_from_df_to_figures(df_finmkts)

#fitness data to plotly figure
fig_fit_run = dash_define_figures.fitness_from_df_to_figures(df_fit_run)

#define the dash app
dash_app = dash_draw_figures.draw_figures(fig_habits_heat, fig_habits_bars,
                                            fig_habits_line_LxD, fig_perhabit_lines_LxD, 
                                            fig_habit_wkday_summary, fig_habit_perhabit_summary,
                                            textarea_quotes, fig_fit_run,
                                            fig_temp_hr, fig_hr2, fig_day, fig_finmkts, fig_finmkts_LxD)

#draw the dash app
dash_app.run_server(debug=True)
#dash_app.run_server(debug=True, host='127.0.0.1', port=8081)