import json
import datetime
import time
import requests
from bs4 import BeautifulSoup
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from dash import dcc 
from app import app
from pages.funcs import fetch
from LSTM.LSTM import LSTMAlgorithm
from XGBoost.XGBoot import XGBoostAl
import pandas as pd

text_input = html.Div(
    [
        html.Div(dbc.Input(id="input", placeholder="Ticker", type="text", debounce=True), style = {
            
        }),
        html.Br(),
        html.Div(id="output"),
    ]
)


with open("pages/watchlist.json") as jsonFile:
    currentWatchlist = json.load(jsonFile)['watchlistStocks']   
    jsonFile.close()

with open("pages/portfolioStocks.json") as jsonFile:
    currentPortfolio = json.load(jsonFile)['portfolioStocks']   
    jsonFile.close()

layout_output = html.Div(
    [html.Div(id = 'layout-output', style = {})],
    id = 'layout-content'
)

tickerName = []
@app.callback(
    Output("layout-content", "children"), 
    [Input("input", "value")]
)

def output_text(value):
    try: 
        fig, fullname, info = fetch.searchData(str(value).upper(),'1d')
        predictionFigure = LSTMAlgorithm(str(value).upper(),'1d')
        XGBoostFigure = XGBoostAl(str(value).upper(),'1d')
        stockInfo = dbc.Row([
                dbc.Col([fig]),
                dbc.Col([
                    html.H2(f"{fullname}"),
                    html.Br(),
                    html.H3(info[0]), 
                    html.H5(f"Open: {info[1]}"),
                    html.H5(f"High: {info[2]}"),
                    html.H5(f"Low: {info[3]}"),
                    html.H5(f"52W High: {info[4]}"),
                    html.H5(f"52W Low: {info[5]}"),
                ])
            ])
        
        buttons = html.Div(
            [
                dbc.Button("Watchlist +", color="warning", disabled=False, id='watchlist-add'),
                dbc.Button("Portfolio +", color="danger", disabled=False, id='portfolio-add'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Add to Portfolio"), close_button=True),
                        dbc.ModalBody([
                            dbc.Input(id="volume-input", placeholder="Number of Shares Bought", type="text", debounce = True), 
                            dbc.Input(id="buy-date", placeholder="Date Bought (DD/MM/YYYY)", type="text", debounce = True),
                        ], id = "modalbody"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Submit",
                                id="submit-button",
                                className="ms-auto",
                                n_clicks=0,
                            )
                        ),
                    ],
                    id="portfolio-popup",
                    centered = True,
                    is_open = False,
                ),
            ], className="d-grid gap-2 col-6 mx-auto"
        )
    
        tickerName.append(value.upper())
        return [
            buttons,
            html.Div(
                [stockInfo], 
                id='layout-output', 
                style = {'margin-top' : '30px'}
            ),
            html.Div(
                dcc.Graph(figure = predictionFigure)
            ),
            html.Div(
                dcc.Graph(figure = XGBoostFigure)
            )
            ]
    except: 
        if value is not None:
            return [dbc.Toast(
                [html.P("Please enter a valid ticker that can be found on Yahoo Finance", className="mb-0")],
                id="auto-toast",
                header="Invalid Ticker",
                icon="danger",
                duration=2750,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            )]

@app.callback(
    Output("portfolio-popup", "is_open"),
    [
        Input("portfolio-add", "n_clicks"), 
        Input("submit-button", "n_clicks")
    ],
    [State("portfolio-popup", "is_open")],
)
def toggle_modal(portfolioClicks, submitClicks, is_open):
    if portfolioClicks or submitClicks:
        return not is_open

@app.callback(
    Output('portfolio-toast', 'children'),
    [
        Input('submit-button', 'n_clicks'),
        Input('volume-input', 'value'),
        Input('buy-date', 'value')
    ]
)

def updatePortfolio(clicks, volumeValue, buyDate):
    """
    Args:
        clicks: int
        volumeValue: str
        buyDate: str
    """
    if volumeValue is not None and buyDate is not None:
        try:
            volumeValue = float(volumeValue)
            dates = str(buyDate).split('/')
            print(dates)
            if len(dates) == 3 and len(dates[0]) == 2 and len(dates[1]) == 2 and len(dates[2]) == 4:
                try:
                    currentUnixTime = str(int(time.time()))
                    buyYear = int(dates[2])
                    buyMonth = int(dates[1])
                    buyDay = int(dates[0])
                    pastUnixTime = time.mktime(datetime.date(buyYear, buyMonth, buyDay).timetuple()) 
                    print(pastUnixTime,currentUnixTime)
                    if int(pastUnixTime) > int(currentUnixTime):
                        return [dbc.Toast(
                            id="auto-toast",
                            icon="danger",
                            header=f"Invalid date input. Try Again.",
                            duration=2750,
                            is_open=True,
                            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                        )]
                    try:
                        historicalCSV = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{tickerName[-1]}?period1={int(pastUnixTime) - 86400}&period2={int(pastUnixTime)}&interval=1d&events=history&includeAdjustedClose=true')
                        buyPrice = int(historicalCSV.loc[0].at['Open'])
                    except:
                        return [dbc.Toast(
                            id="auto-toast",
                            icon="danger",
                            header=f"Date inputted cannot be a date when the market was closed.",
                            duration=2750,
                            is_open=True,
                            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                        )]
                    try: 
                        URL = f'https://finance.yahoo.com/quote/{tickerName[-1]}/'
                        page = requests.get(URL)
                        soup = BeautifulSoup(page.content, "html.parser")
                        industry = soup.find_all(class_='D(ib) Va(t)'); 
                        industry = industry[0] 
                        industry = str(industry).split(':')[2]; 
                        industry = industry.split('Fw(600)">')[1] 
                        industry = industry.split('<')[0]

                        if [tickerName[-1], volumeValue, buyDate, buyPrice, industry] not in currentPortfolio:
                            currentPortfolio.append([tickerName[-1], volumeValue, buyDate, buyPrice, industry])

                        if clicks is not None:
                            currentPortfolio.sort(key = lambda x : x[0])
                            jsonData = {
                            "portfolioStocks" : currentPortfolio
                            }
                            with open('pages/portfolioStocks.json', 'w') as jsonFile:
                                json.dump(jsonData, jsonFile)
                                jsonFile.close()
                            return [dbc.Toast(
                                id="auto-toast",
                                icon="success",
                                header="Added to your portfolio",
                                duration=2750,
                                is_open=True,
                                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                            )]
                    except:
                        if [tickerName[-1], volumeValue, buyDate, buyPrice] not in currentPortfolio:
                            currentPortfolio.append([tickerName[-1], volumeValue, buyDate, buyPrice])
                        currentPortfolio.sort(key = lambda x : x[0])
                        jsonData = {
                            "portfolioStocks" : currentPortfolio
                        }
                        with open('pages/portfolioStocks.json', 'w') as jsonFile:
                            json.dump(jsonData, jsonFile)
                            jsonFile.close()
                        return [dbc.Toast(
                            id="auto-toast",
                            icon="success",
                            header="Added to your portfolio",
                            duration=2750,
                            is_open=True,
                            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                        )]
                except Exception:
                    return [dbc.Toast(
                        id="auto-toast",
                        icon="danger",
                        header=f"Invalid date input. Try Again.",
                        duration=2750,
                        is_open=True,
                        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                    )]
            else:
                return [dbc.Toast(
                    id="auto-toast",
                    icon="danger",
                    header=f"Invalid date input. Try Again.",
                    duration=2750,
                    is_open=True,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                )]
        except:
            if volumeValue is not None:
                return [dbc.Toast(
                        id="auto-toast",
                        icon="danger",
                        header=f"Invalid volume input. Try Again.",
                        duration=2750,
                        is_open=True,
                        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                    )]

@app.callback(
    Output("watchlist-toast", 'children'),
    [Input('watchlist-add', 'n_clicks')]
)
def updateWatchlist(n):
    if n is not None:
        with open("pages/watchlist.json") as jsonFile:
            currentWatchlist = json.load(jsonFile)['watchlistStocks']
    
            jsonFile.close()
        if tickerName[-1] not in currentWatchlist: 
            currentWatchlist.append(tickerName[-1])
            currentWatchlist.sort(key = lambda x : x[0])
            jsonData={
                "watchlistStocks": currentWatchlist
            }
            with open('pages/watchlist.json', 'w') as jsonFile:
                json.dump(jsonData, jsonFile)
                jsonFile.close()
        else:
            return [dbc.Toast(
                    id="auto-toast",
                    icon="danger",
                    header=f"{tickerName[-1]} is already in your watchlist",
                    duration=2750,
                    is_open=True,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                )]
        return [dbc.Toast(
                id="auto-toast",
                icon="success",
                header="Added to your watchlist",
                duration=2750,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            )]

layout = html.Div(children=[
    dbc.Spinner(children = [dbc.Row([
        dbc.Col([]),
        dbc.Col([text_input]),
        dbc.Col([])
    ]),
    dbc.Row([dbc.Col([layout_output])])], type = "grow", color = "success"),
    html.Div(id = 'watchlist-toast'),
    html.Div(id = 'portfolio-toast')
], id='page-content')