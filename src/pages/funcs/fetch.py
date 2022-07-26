import pandas as pd
from dash import dcc
import plotly.graph_objects as go
import time 
from bs4 import BeautifulSoup
import requests 

def currentPriceParser(soup):
    currentPrice = soup.find_all('fin-streamer', class_="Fw(b) Fz(36px) Mb(-4px) D(ib)")
    currentPrice = str(currentPrice[0])
    lbool = False 
    gbool = True 
    currentPriceVal = ""
    for i in currentPrice:
        if gbool and i == "<": 
            gbool = False
            continue 

        if i == ">" and not lbool: 
            lbool = True
            continue 

        if lbool == True and i != "<":
            currentPriceVal += i 

        if i == "<" and not gbool: 
            break 
    
    currentPriceVal = currentPriceVal.replace(",", "")
    return currentPriceVal

def watchlistFetchData(ticker):
    URL = f'https://finance.yahoo.com/quote/{ticker}'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    currentPriceVal = currentPriceParser(soup)
    statsTable = soup.find_all('td', class_ = 'Ta(end) Fw(600) Lh(14px)')
    open = statsTable[1]
    open = str(open)[60:-5]
    dayRange = statsTable[4]
    dayRange = str(dayRange)[66:-5]
    dayRange = dayRange.split(" - ")
    low, high = dayRange[0], dayRange[1] 
    fiftyTwoWeekRange = statsTable[5] 
    fiftyTwoWeekRange = str(fiftyTwoWeekRange)[74:-5]
    fiftyTwoWeekRange = fiftyTwoWeekRange.split(" - ") 
    fiftyTwoWeekLow, fiftyTwoWeekHigh = fiftyTwoWeekRange[0], fiftyTwoWeekRange[1]
    return [currentPriceVal, open, high, low, fiftyTwoWeekHigh, fiftyTwoWeekLow]

def portfolioFetchData(ticker):
    URL = f'https://finance.yahoo.com/quote/{ticker}/'
    page = requests.get(URL) 
    soup = BeautifulSoup(page.content, "html.parser")
    currentPriceVal = currentPriceParser(soup)
    return currentPriceVal

def homePage(ticker):
    currentUnixTime = int(time.time())
    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={currentUnixTime - 63072000}&period2={currentUnixTime}&interval=1d&events=history&includeAdjustedClose=true')
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    URL = f'https://finance.yahoo.com/quote/{ticker}/'
    page = requests.get(URL) 
    soup = BeautifulSoup(page.content, "html.parser")
    currentPriceVal = currentPriceParser(soup)
    statsTable = soup.find_all('td', class_ = 'Ta(end) Fw(600) Lh(14px)')
    open = statsTable[1]
    open = str(open)[60:-5]
    open = float(open.replace(',', ''))
    close = statsTable[0]
    close = str(close)[66:-5]
    close = float(close.replace(',', ''))
    dayRange = statsTable[4]
    dayRange = str(dayRange)[74:-5]
    dayRange = dayRange.split(" - ")
    low, high = float(dayRange[0].replace(',','')), float(dayRange[1].replace(',',''))
    fiftyTwoWeekRange = statsTable[4]
    fiftyTwoWeekRange = str(fiftyTwoWeekRange)[74:-5]
    fiftyTwoWeekRange = fiftyTwoWeekRange.split(" - ")
    fiftyTwoWeekLow, fiftyTwoWeekHigh = float(fiftyTwoWeekRange[0].replace(',','')), float(fiftyTwoWeekRange[1].replace(',',''))
    return fig, [currentPriceVal, open, close, high, low, fiftyTwoWeekHigh, fiftyTwoWeekLow]

def searchData(ticker,time_frame):
    currentUnixTime = int(time.time())
    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={currentUnixTime - 63072000}&period2={currentUnixTime}&interval=1d&events=history&includeAdjustedClose=true')
    config = {'displayModeBar': True}
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title_text='Historical Stock Data', title_x = 0.5)
    URL = f'https://finance.yahoo.com/quote/{ticker}/'
    page = requests.get(URL) 
    soup = BeautifulSoup(page.content, "html.parser")
    fullName = soup.find_all('h1', class_='D(ib) Fz(18px)')
    fullName = str(fullName[0])
    fullName = fullName[27:-5]
    currentPriceVal = currentPriceParser(soup)
    statsTable = soup.find_all('td', class_ = 'Ta(end) Fw(600) Lh(14px)')
    open = statsTable[1]
    open = str(open)[60:-5]
    open = float(open.replace(',', ''))
    dayRange = statsTable[4]; 
    dayRange = str(dayRange)[66:-5]
    dayRange = dayRange.split(" - ")
    low, high = float(dayRange[0].replace(',','')), float(dayRange[1].replace(',',''))
    fiftyTwoWeekRange = statsTable[5]
    fiftyTwoWeekRange = str(fiftyTwoWeekRange)[74:-5]
    fiftyTwoWeekRange = fiftyTwoWeekRange.split(" - ") 
    fiftyTwoWeekLow, fiftyTwoWeekHigh = float(fiftyTwoWeekRange[0].replace(',','')), float(fiftyTwoWeekRange[1].replace(',',''))
    return dcc.Graph(figure=fig, config=config), fullName, [currentPriceVal, open, high, low, fiftyTwoWeekHigh, fiftyTwoWeekLow]

