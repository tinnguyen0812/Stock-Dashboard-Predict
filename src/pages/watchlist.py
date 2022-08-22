import json
from dash import html, Output, State, Input
import dash_bootstrap_components as dbc
from pages.funcs import fetch
from app import app

def formtable():
    with open("pages/watchlist.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    watchlistStocks = jsonObject["watchlistStocks"]
    tableHeader = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Ticker"), 
                    html.Th("Current (USD)"), 
                    html.Th("Open (USD)"), 
                    html.Th("High (USD)"), 
                    html.Th("Low (USD)"), 
                    html.Th("52W High (USD)"), 
                    html.Th("52W Low (USD)")
                ]
            )
        )
    ]

    rows = []
    for i in range(0, len(watchlistStocks)):
        curData = fetch.watchlistFetchData(watchlistStocks[i])
        rows.append(
            html.Tr(
                [
                    html.Td(watchlistStocks[i]),
                    html.Td(curData[0]),
                    html.Td(curData[1]),
                    html.Td(curData[2]),
                    html.Td(curData[3]),
                    html.Td(curData[4]),
                    html.Td(curData[5])
                ]
            )
        )
    tableBody = [html.Tbody(rows)]
    table = dbc.Table(tableHeader + tableBody, bordered = False, striped = True, hover=True)
    return table

layout = html.Div(children=[
    html.H1(
        children="WATCHLIST", 
        style = {
            'text-align': 'center',
            'color': '#4db6ac', 
            'font-family': 'Montserrat' 
        }
    ),
    html.Div(
        style = {
            'margin': 'auto', 
            'width': '90%', 
            'padding': '30px', 
            'text-align': 'center' 
        },
        id = 'body-table' 
    ),
    html.Div(
        dbc.Row([
            dbc.Col(dbc.Button(
                children = 'Refresh Data',
                style = {
                    'text-align': 'center'
                },
                id='refresh-button',
                n_clicks=0,  outline=True, color="success"
            )),
            dbc.Col(dbc.Button(
                children = 'Remove stock',
                style = {
                    'text-align': 'center'
                },
                id='remove-button',
                n_clicks=0,  outline=True, color="danger"
            ), width=6)
        ]), 
        style = {
            'margin': 'auto',
            'width': '90%',
            'padding': '30px',
            'text-align': 'center'
        }
    ), 
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Remove a stock"), close_button=True),
                dbc.ModalBody([
                    dbc.Input(id="removed-stock", placeholder="Stock ticker (in caps)", type="text", debounce = True),
                ], id = "watchlist-remove-modal"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Submit",
                        id="submit-button",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="remove-popup-watchlist",
            centered=True,
            is_open=False,
        ),
        html.Div(id = 'remove-toast2')
], id='page-content')

@app.callback(
    Output('body-table', 'children'),
    Input('refresh-button', 'n_clicks')
)
def refreshTable(n):
    table = formtable()
    return [table]

@app.callback(
    Output('remove-popup-watchlist', 'is_open'),
    [Input('remove-button', 'n_clicks'),
    Input('submit-button', 'n_clicks')],
    [State('remove-popup-watchlist', 'is_open')]
)
def removePopup(removeClicks, submitClicks, is_open):
    if removeClicks or submitClicks:
        return not is_open

lastRemoved = ""
@app.callback(
    Output('remove-toast2', 'children'),
    [
        Input('submit-button', 'n_clicks'),
        Input('removed-stock', 'value'),
    ]
)
def removeWatchlistStock(clicks, ticker):
    if clicks is not None: 
        with open("pages/watchlist.json") as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
        watchlistStocks = jsonObject["watchlistStocks"]
        try: 
            watchlistStocks.remove(ticker)
            jsonObject = {'watchlistStocks': watchlistStocks}
            with open('pages/watchlist.json', 'w') as jsonFile: 
                json.dump(jsonObject, jsonFile)
                jsonFile.close()
            
            lastRemoved = ticker
            return [dbc.Toast(
                id="success-toast",
                icon="success",
                header=f"Success! Removed from your watchlist.",
                duration=2750,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            )]
        except:
            if ticker is not None and clicks is not None and lastRemoved != ticker: 
                return [dbc.Toast(
                id="error-toast",
                icon="danger",
                header=f"Invalid ticker name. Try Again.",
                duration=2750,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            )]
