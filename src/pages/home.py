
from dash import html, dcc
import dash_bootstrap_components as dbc
import json
from pages.funcs import fetch

with open("./config.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()
firstName = jsonObject["firstName"]
lastName = jsonObject["lastName"]
colors = {
    'background': '#111111',
    'text': '#363636'
}
importantStocks = [['^GSPC', '^DJI', '^IXIC'], ['S&P 500', 'Dow Jones Industrial Average', 'NASDAQ Composite']]

cardsList = []
def getTime_frame():
    return 
for i in range(0, 3):
    stock = importantStocks[0][i]   
    fig, infor = fetch.homePage(stock)
    cardText = html.H5(f"{importantStocks[1][i]}:\n{float(infor[0])}$")
    cardsList.append(
        dbc.Card(
            [
                dcc.Graph(figure=fig),
                dbc.CardBody(
                    [
                        html.H4(cardText),
                        html.H6(f"Day High: {infor[3]}"),
                        html.H6(f"Day Low: {infor[4]}"),
                        html.H6(f"52 Week High: {infor[5]}"),
                        html.H6(f"52 Week Low: {infor[6]}"),
                    ]
                )
            ],
            color = "success",
            outline = True
        )
    )

cards = html.Div(
    children = dbc.Row(
        [
            dbc.Col(cardsList[0]), 
            dbc.Col(cardsList[1]),
            dbc.Col(cardsList[2]),
        ]
    ),
    style = {
        'margin-left' : '30px',
        'margin-right' : '30px'
    }   
)

layout = html.Div(
    children=[
        html.H1(
            children=f"Candlesticks of Important Stock",
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        cards
    ]
)
