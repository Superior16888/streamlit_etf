import streamlit as st
import pandas as pd
import sqlite3

def fetch_etfs(year, season):
    conn = sqlite3.connect('etf.sqlite')
    c = conn.cursor()
    c.execute(f"SELECT * FROM etfs WHERE 年季='{year+season}'")
    rows = c.fetchall()
    if len(rows) > 0:
        ETFs = pd.DataFrame(rows, columns=['年季', 'ETF名稱', '股票代號', '股票名稱', '持股比率', '產業類別', '產業比率'])
    else:
        ETFs = get_ETFS(year, season)
        ETFs.to_sql('etfs', conn, if_exists='append', index=False)
    conn.close()
    ETFs['持股比率'] = ETFs['持股比率'].apply(lambda x: float(x[:-1]))/100
    ETFs['產業比率'] = ETFs['產業比率'].apply(lambda x: float(x[:-1]))/100
    return ETFs

def get_unique_etfs():
    conn = sqlite3.connect('etf.sqlite')
    c = conn.cursor()
    c.execute("SELECT DISTINCT 年季, ETF名稱 FROM etfs")
    rows = c.fetchall()
    unique_etfs = pd.DataFrame(rows, columns=['年季', 'ETF名稱'])
    conn.close()
    return unique_etfs

def show_etfs(etf_data):
    st.write(etf_data)

unique_etfs = get_unique_etfs()

# Sidebar to select year and season
selected_year = st.sidebar.selectbox('Select year', unique_etfs['年季'].unique())
selected_etf = st.sidebar.selectbox('Select ETF', unique_etfs.loc[unique_etfs['年季'] == selected_year, 'ETF名稱'].unique())

# Fetch ETF data and show
etf_data = fetch_etfs(selected_year[:3], selected_year[3:])
etf_data = etf_data[etf_data['ETF名稱'] == selected_etf]
etf_data[['持股比率', '產業比率']] = etf_data[['持股比率', '產業比率']].applymap('{:.2%}'.format)
show_etfs(etf_data)


