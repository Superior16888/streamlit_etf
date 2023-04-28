import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import warnings
warnings.filterwarnings('ignore')
import sqlite3

def get_ETFS(year, season):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t78sb04'
    payload = {
        'mponent': '1',
        'TYPEK': 'all',
        'step': '1',
        'run': 'Y',
        'firstin': 'true',
        'FUNTYPE': '02',
        'year': year,
        'season': season,
        'fund_no': '0'
    }
    response = requests.post(url, payload)
    soup = BeautifulSoup(response.content, "html.parser")

    ETFs = pd.DataFrame(columns=['年季', 'ETF名稱', '股票代號', '股票名稱', '持股比率', '產業類別', '產業比率'])

    Number_of_ETFs = len(soup.find_all('table', {"class": "noBorder"}))

    for i in range(Number_of_ETFs):
        ETF_Name = soup.find_all('table', {"class": "noBorder"})[i].find_all('td')[1].text.strip()
        data = soup.find_all('table', {"class": "hasBorder"})[i].find_all('tr', {"class": ["odd", "even"]})
        rows = [[td.text for td in tr.find_all('td')] for tr in data if len(tr.find_all('td')) == 5]
        columns = ['股票代號', '股票名稱', '持股比率', '產業類別', '產業比率']
        ETF = pd.DataFrame(data=rows, columns=columns)
        ETF.insert(0, 'ETF名稱', ETF_Name, True)
        ETF.insert(0, '年季', year + season, True)
        ETFs = pd.concat([ETFs, ETF], ignore_index=True)

        time.sleep(5)
    return ETFs


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
    return ETFs


# Fetch ETF data for year 112, season 01
ETFS = fetch_etfs('111', '03')

ETFS
