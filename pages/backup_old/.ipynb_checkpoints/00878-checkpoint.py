import streamlit as st
import pandas as pd
import sqlite3
import pandas.io.formats.style

def fetch_latest_year_season():
    conn = sqlite3.connect('etf.sqlite')
    c = conn.cursor()
    c.execute("SELECT MAX(年季) FROM etfs")
    latest_year_season = c.fetchone()[0]
    conn.close()
    return latest_year_season[:3], latest_year_season[3:]

def fetch_etf_data(year, season, etf_name):
    conn = sqlite3.connect('etf.sqlite')
    c = conn.cursor()
    c.execute(f"SELECT * FROM etfs WHERE 年季='{year+season}' AND ETF名稱='{etf_name}'")
    rows = c.fetchall()
    if len(rows) > 0:
        etf_data = pd.DataFrame(rows, columns=['年季', 'ETF名稱', '股票代號', '股票名稱', '持股比率', '產業類別', '產業比率'])
        etf_data['持股比率'] = etf_data['持股比率'].apply(lambda x: float(x[:-1])) / 100
        etf_data['產業比率'] = etf_data['產業比率'].apply(lambda x: float(x[:-1])) / 100
        return etf_data
    else:
        return None

def show_etf_data(etf_data):
    if etf_data is not None:
        # Exclude 'ETF名稱' column and format percentages
        etf_data_formatted = etf_data.drop(columns=['ETF名稱']).style.format({'持股比率': '{:.2%}', '產業比率': '{:.2%}'})
        # Hide index and remove border around index column
        etf_data_formatted = etf_data_formatted.hide_index().set_table_styles([{'selector': 'th.row_heading', 'props': [('display', 'none')]}])
        st.dataframe(etf_data_formatted)
    else:
        st.write("No data found for the selected ETF.")

# Fetch the latest year and season from the database
selected_year, selected_season = fetch_latest_year_season()

# Specify the ETF name
selected_etf = '國泰台灣高股息傘型證券投資信託基金之台灣ESG永續高股息ETF證券投資信託基金'

# Fetch the ETF data for the latest year, season, and ETF name
etf_data = fetch_etf_data(selected_year, selected_season, selected_etf)





import plotly.express as px
import numpy as np
df = etf_data
fig = px.treemap(df, path=[px.Constant("ETF"), '產業類別', '股票名稱'], values='持股比率')
# fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
# fig.show()
# fig.write_html(f'00878_Perform_{start_date}_{end_date}.html')
st.plotly_chart(fig, use_container_width=False)

# Show the ETF data
show_etf_data(etf_data)

