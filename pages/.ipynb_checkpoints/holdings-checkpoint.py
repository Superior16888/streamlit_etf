import streamlit as st
import pandas as pd
import sqlite3
import pandas.io.formats.style
import plotly.express as px

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
    c.execute(f"SELECT * FROM etfs WHERE 年季='{year+season}' AND 代號簡稱='{etf_name}'")
    rows = c.fetchall()
    if len(rows) > 0:
        etf_data = pd.DataFrame(rows, columns=['年季', 'ETF名稱', '股票代號', '股票名稱', '持股比率', '產業類別', '產業比率','代號簡稱'])
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
        etf_data_formatted = etf_data_formatted.hide_index().set_table_styles([{'selector': 'th.row_heading', 'props': [('display','none')]}])
        st.dataframe(etf_data_formatted)
    else:
        st.write("No data found for the selected ETF.")
        
# Fetch the latest year and season from the database
selected_year, selected_season = fetch_latest_year_season()

# Fetch the list of available ETFs
conn = sqlite3.connect('etf.sqlite')
c = conn.cursor()
c.execute(f"SELECT DISTINCT 代號簡稱 FROM etfs WHERE 年季='{selected_year+selected_season}'")
available_etfs = c.fetchall()
available_etfs = [row[0] for row in available_etfs]
conn.close()

# Create a selectbox for choosing the ETF
selected_etf = st.selectbox("Select ETF", available_etfs)

# Fetch the ETF data for the latest year, season, and selected ETF
etf_data = fetch_etf_data(selected_year, selected_season, selected_etf)


# Create the treemap visualization if data is available
if etf_data is not None:
    fig = px.treemap(etf_data, path=[px.Constant("ETF"), '產業類別', '股票名稱'], values='持股比率')
    st.plotly_chart(fig,theme="streamlit",use_container_width=False)
    
    
# Show the ETF data
show_etf_data(etf_data)


