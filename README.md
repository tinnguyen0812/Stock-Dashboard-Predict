# Stock Dashboard and Predictor

This project contains a custom web based dashboard for stocks as well as machine learning algorithms to predict the prices of various stocks.

## Features

- Watchlist & Portfolio
- Prominent Exchanges at a Glance
- Search Page to Find Information About Any Given Stock
- Machine Learning Algorithm to Predict Prices of Stocks

## Installation

Make sure you are using Python 3.8.x in order for TensorFlow to work.

Clone the repository

```
git clone https://github.com/wos-if/Stock-Dashboard-Prediction
```

Install the dependencies

```python
pip install -r requirements.txt
```

## Usage

Run

```
cd src
python main.py
```

In the terminal there will be a localhost link (most likely http://127.0.0.1:8000/) which you can enter into a browser (preferably Chromium based) to access the web app. The library used for rendering the web app will print out useless information in the console and it can be safely ignored.

### Notes

- When searching for a ticker, you may have to wait some time depending on your machine for the machine learning algorithm to run.
- Upon launching the program, it may take time for the web app to actually load.

### Code used from sites / videos

| Site / video                                                                                       | Code used / why                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| https://towardsdatascience.com/time-series-forecasting-with-recurrent-neural-networks-74674e289816 | How to use the libraries and functions for the machine learning algorithm because the algorithm is quite complex and we did not know much about machine learning before this project. |
