import streamlit as st
import requests
import io
import pandas as pd
import numpy as np
import plotly.express as px

st.title("上市公司每月營收")

# Input for year and month
year = st.slider("選擇年度", 102, 121, 112)
month = st.slider("選擇月份", 1, 12, 9)

def monthly_revenue(year, month):
    url = "https://mops.twse.com.tw/server-java/FileDownLoad" 
    payload = {
        "step": "9",
        "functionName": "show_file2",
        "filePath": "/t21/sii/",
        "fileName": f"t21sc03_{year}_{month}.csv"
    }
    response = requests.post(url, data=payload)
    response.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(response.text))
    
    df['公司名稱'] = df['公司名稱'] + "<br>" + df['公司代號'].astype(str)
    df_filtered = df[df['營業收入-當月營收'] > 0]
    df_filtered = df_filtered[['產業別','公司名稱','營業收入-當月營收','營業收入-上月營收','累計營業收入-當月累計營收','累計營業收入-去年累計營收']]
    df_filtered['營業收入-當月營收'] = (df_filtered['營業收入-當月營收'] / 100000)
    df_filtered['營業收入-上月營收'] = df_filtered['營業收入-上月營收'] / 100000
    df_filtered['月營收增減'] = (df_filtered['營業收入-當月營收'] - df_filtered['營業收入-上月營收']) / df_filtered['營業收入-上月營收'].abs()
    df_filtered['月營收變動'] = df_filtered['月營收增減'] ## 
    df_filtered['累計營業收入-當月累計營收'] = df_filtered['累計營業收入-當月累計營收'] / 100000
    df_filtered['累計營業收入-去年累計營收'] = df_filtered['累計營業收入-去年累計營收'] / 100000
    df_filtered['累計營收增減'] = (df_filtered['累計營業收入-當月累計營收'] - df_filtered['累計營業收入-去年累計營收']) / df_filtered['累計營業收入-去年累計營收'].abs()
    return df_filtered

df_filtered = monthly_revenue(year, month)

limit = 0.5
df_filtered['月營收變動'] = np.where(df_filtered['月營收變動'] > limit, limit, 
              np.where(df_filtered['月營收變動'] < -limit, -limit, df_filtered['月營收變動']))
fig = px.treemap(df_filtered, 
                 path=[px.Constant('月營收'),'產業別','公司名稱'],
                 values='營業收入-當月營收',
                 color='月營收變動',
                 color_continuous_scale='RdYlBu_r',
                 width=1200, height=700,
                 color_continuous_midpoint=0,
                 custom_data=['月營收增減','累計營收增減','累計營業收入-當月累計營收','累計營業收入-去年累計營收']) 

fig.update_layout(margin=dict(t=30, l=10, r=10, b=5))
fig.update_traces(hovertemplate='當月營收(億)：%{value:.0f}<br>營收增減: %{customdata[0]:.1%}<br>當年累計營收: %{customdata[2]:.0f}<br>累計營收增減: %{customdata[1]:.1%}')
fig.update_traces(textinfo='label+percent entry')
fig.update_traces(textfont_size=16)

st.plotly_chart(fig)
