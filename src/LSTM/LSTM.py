
import pandas as pd
import numpy as np

from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import LSTM, Dense

import plotly.graph_objects as go

import time 

def predict(numPrediction, model, closeData, lookBack):

    predictionList = closeData[-lookBack:]
    
    for _ in range(numPrediction):
        x = predictionList[-lookBack:]
        x = x.reshape((1, lookBack, 1))
        out = model.predict(x)[0][0]
        predictionList = np.append(predictionList, out)
    predictionList = predictionList[lookBack-1:]

    return predictionList
    
def predictDates(numPrediction, df):
    
    lastDate = df['Date'].values[-1]
    predictionDates = pd.date_range(lastDate, periods=numPrediction+1).tolist()
    return predictionDates


def LSTMAlgorithm(ticker,time_frame):
    
    currentUnixTime = int(time.time())
    print(currentUnixTime)
    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={1532719575}&period2={currentUnixTime}&interval={time_frame}&events=history&includeAdjustedClose=true')

    df['Date'] = pd.to_datetime(df['Date'])

    df.drop(columns=['Open', 'High', 'Low', 'Volume'], inplace=True)

    closeData = df['Close'].values

    closeData = closeData.reshape((-1,1))


    dateData = df['Date'].values


    splitPercent = 0.80

    split = int(splitPercent*len(closeData))

    closeTrain = closeData[:split]
    closeTest = closeData[split:]

    lookBack = 30

    trainGenerator = TimeseriesGenerator(closeTrain, closeTrain, length=lookBack, batch_size=20)     
    testGenerator = TimeseriesGenerator(closeTest, closeTest, length=lookBack, batch_size=1)

    model = Sequential()

    model.add(LSTM(10, activation='relu'))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mse',metrics=['accuracy'])

    model.fit_generator(trainGenerator, epochs=200, verbose=1)

    prediction = model.predict_generator(testGenerator)

    closeTrain = closeTrain.reshape((-1))
    closeTest = closeTest.reshape((-1))
    prediction = prediction.reshape((-1))
    closeData = closeData.reshape((-1))

    layout = go.Layout(
        title = "LSTM Prediction",
        xaxis = {'title' : "Date"},
        yaxis = {'title' : "Close"},
    )

    forecast = predict(15, model, closeData, lookBack)
    forecastDates = predictDates(15, df)

    trace1 = go.Scatter(
        x = forecastDates,
        y = forecast,
        mode='lines',
        name = 'Forecast'
    )

    trace2 = go.Scatter(
        x = dateData,
        y = closeData,
        mode='lines',
        name = 'Previous'
    )

    fig = go.Figure(data=[trace2,trace1], layout=layout)
    #print('LSTM',fig)
    return fig 