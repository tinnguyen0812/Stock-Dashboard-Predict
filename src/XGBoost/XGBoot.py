import math
import numpy as np
import pandas  as pd
import time
from datetime import date
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from xgboost import XGBRegressor
import plotly.graph_objects as go
import datetime

test_size = 0.2                
N = 3                          

model_seed = 100

def get_mape(y_true, y_pred):
    """
    Compute mean absolute percentage error (MAPE)
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def _load_data(ticker,time_frame):
    currentUnixTime = int(time.time())
    print(currentUnixTime)
    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={1532719575}&period2={currentUnixTime}&interval={time_frame}&events=history&includeAdjustedClose=true')
    print('data',df)
    df.loc[:, 'Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.columns = [str(x).lower().replace(' ', '_') for x in df.columns]
    df['month'] = df['date'].dt.month
    df.sort_values(by='date', inplace=True, ascending=True)
    print('data return',df)
    return df

def feature_engineer(df):
    df['range_hl'] = df['high'] - df['low']
    df['range_oc'] = df['open'] - df['close']
    lag_cols = ['adj_close', 'range_hl', 'range_oc', 'volume']
    shift_range = [x + 1 for x in range(N)]
    for col in lag_cols:
        for i in shift_range:

            new_col='{}_lag_{}'.format(col, i) 
            df[new_col]=df[col].shift(i)

    return df[N:]

def scale_row(row, feat_mean, feat_std):
    feat_std = 0.001 if feat_std == 0 else feat_std
    row_scaled = (row - feat_mean) / feat_std

    return row_scaled

def get_mov_avg_std(df, col, N):
    mean_list = df[col].rolling(window=N, min_periods=1).mean() 
    std_list = df[col].rolling(window=N, min_periods=1).std()  

    mean_list = np.concatenate((np.array([np.nan]), np.array(mean_list[:-1])))
    std_list = np.concatenate((np.array([np.nan]), np.array(std_list[:-1])))

    df_out = df.copy()
    df_out[col + '_mean'] = mean_list
    df_out[col + '_std'] = std_list

    return df_out

def XGBoostAl(ticker,time_frame):
    data_df=_load_data(ticker,time_frame)   
    df=feature_engineer(data_df)
   
    cols_list = [
        "adj_close",
        "range_hl",
        "range_oc",
        "volume"
    ]
    for col in cols_list:
        df = get_mov_avg_std(df, col, N)


    
    num_test = int(test_size * len(df))
    num_train = len(df) - num_test
    train = df[:num_train]
    test = df[num_train:]

    
    cols_to_scale = [
        "adj_close"
    ]
    for i in range(1, N + 1):
        cols_to_scale.append("adj_close_lag_" + str(i))
        cols_to_scale.append("range_hl_lag_" + str(i))
        cols_to_scale.append("range_oc_lag_" + str(i))
        cols_to_scale.append("volume_lag_" + str(i))

    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train[cols_to_scale])
    train_scaled = pd.DataFrame(train_scaled, columns=cols_to_scale)
    train_scaled[['date', 'month']] = train.reset_index()[['date', 'month']]

    test_scaled = test[['date']]
    for col in tqdm(cols_list):
        feat_list = [col + '_lag_' + str(shift) for shift in range(1, N + 1)]
        temp = test.apply(lambda row: scale_row(row[feat_list], row[col + '_mean'], row[col + '_std']), axis=1)
        test_scaled = pd.concat([test_scaled, temp], axis=1)

    features = []
    for i in range(1, N + 1):
        features.append("adj_close_lag_" + str(i))
        features.append("range_hl_lag_" + str(i))
        features.append("range_oc_lag_" + str(i))
        features.append("volume_lag_" + str(i))

    target = "adj_close"

    X_train = train[features]
    y_train = train[target]
    X_sample = test[features]
    y_sample = test[target]

    X_train_scaled = train_scaled[features]
    y_train_scaled = train_scaled[target]
    X_sample_scaled = test_scaled[features]

    from sklearn.model_selection import GridSearchCV
    parameters={'n_estimators':[90],
                'max_depth':[7],
                'learning_rate': [0.3],
                'min_child_weight':range(5, 21, 1),
                }
    model=XGBRegressor(seed=model_seed,
                         n_estimators=100,
                         max_depth=3,
                         eval_metric='rmse',
                         learning_rate=0.1,
                         min_child_weight=1,
                         subsample=1,
                         colsample_bytree=1,
                         colsample_bylevel=1,
                         gamma=0)
    gs=GridSearchCV(estimator= model,param_grid=parameters,cv=5,refit= True,scoring='neg_mean_squared_error')

    gs.fit(X_train_scaled,y_train_scaled)
    print ('accuracy: ' + str(gs.best_params_))

    est_scaled = gs.predict(X_train_scaled)
    train['est'] = est_scaled * math.sqrt(scaler.var_[0]) + scaler.mean_[0]

    pre_y_scaled = gs.predict(X_sample_scaled)
    test['pre_y_scaled'] = pre_y_scaled
    test['pre_y']=test['pre_y_scaled'] * test['adj_close_std'] + test['adj_close_mean']
    layout = go.Layout(
        title = "XGBoost Prediction",
        xaxis = {'title' : "Date"},
        yaxis = {'title' : "Adj_close"}
    )

    trace1 = go.Scatter(
        x = test['date'],
        y = test['adj_close'],
        mode='lines',
        name = 'Previous'
    )

    trace2 = go.Scatter(
        x = test['date'],
        y = test['pre_y'],
        mode='lines',
        name = 'Forecast'
    )

    fig = go.Figure(data=[trace1, trace2], layout=layout)

    return fig