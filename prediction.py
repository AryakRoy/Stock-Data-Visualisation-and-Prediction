import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import model_from_json
import os

class Predictor:
    def __init__(self,traverser):
        self.traverser = traverser

    def create_new_model(self,df,ticker):
        data = df.filter(['Close'])
        dataset = data.values
        training_data_len = math.ceil(len(dataset) * 0.8)
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(dataset)
        train_data = scaled_data[0:training_data_len,:]
        x_train = []
        y_train = []
        for i in range(60,len(train_data)):
            x_train.append(train_data[i-60:i,0])
            y_train.append(train_data[i,0])

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam',loss='mean_squared_error')
        model.fit(x_train,y_train,batch_size=1,epochs=1)
        model_json = model.to_json()
        save_path = os.path.join(os.getcwd(),"models",f"{ticker}.json")
        save_path_2 = os.path.join(os.getcwd(),"models",f"{ticker}.h5")
        try:
            with open(save_path, "w") as json_file:
                json_file.write(model_json)
        except FileNotFoundError:
            os.mkdir(os.path.join(os.getcwd(),"models"))
            with open(save_path, "w") as json_file:
                json_file.write(model_json)
        model.save_weights(save_path_2)

        last_60_days = data[-60:].values
        last_60_days_scaled = scaler.transform(last_60_days)
        todays_data = data[-61:-1].values
        todays_data_scaled = scaler.transform(todays_data)
        today_data = data.iloc[-1].values


        X_test = []
        X_test.append(last_60_days_scaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

        X_test_2 = []
        X_test_2.append(todays_data_scaled)
        X_test_2 = np.array(X_test_2)
        X_test_2 = np.reshape(X_test_2,(X_test_2.shape[0],X_test_2.shape[1],1))

        tomorrow_pred_price = model.predict(X_test)
        tomorrow_pred_price = scaler.inverse_transform(tomorrow_pred_price)
        todays_pred_price = model.predict(X_test_2)
        todays_pred_price = scaler.inverse_transform(todays_pred_price)

        tomorrow_pred_price = round(float(tomorrow_pred_price[0][0]),2)
        todays_pred_price = round(float(todays_pred_price[0][0]),2)
        today_data = round(today_data[0],2)

        return tomorrow_pred_price, todays_pred_price, today_data
    
    def load_existing_model(self,df,ticker):
        load_path = os.path.join(os.getcwd(),"models",f"{ticker}.json")
        load_path_2 = os.path.join(os.getcwd(),"models",f"{ticker}.h5")
        with open(load_path, "r") as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json)
        model.load_weights(load_path_2)
        model.compile(optimizer='adam',loss='mean_squared_error')

        data = df.filter(['Close'])
        dataset = data.values
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(dataset)
        last_60_days = data[-60:].values
        last_60_days_scaled = scaler.transform(last_60_days)
        todays_data = data[-61:-1].values
        todays_data_scaled = scaler.transform(todays_data)
        today_data = data.iloc[-1].values


        X_test = []
        X_test.append(last_60_days_scaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

        X_test_2 = []
        X_test_2.append(todays_data_scaled)
        X_test_2 = np.array(X_test_2)
        X_test_2 = np.reshape(X_test_2,(X_test_2.shape[0],X_test_2.shape[1],1))

        tomorrow_pred_price = model.predict(X_test)
        tomorrow_pred_price = scaler.inverse_transform(tomorrow_pred_price)
        todays_pred_price = model.predict(X_test_2)
        todays_pred_price = scaler.inverse_transform(todays_pred_price)

        tomorrow_pred_price = round(float(tomorrow_pred_price[0][0]),2)
        todays_pred_price = round(float(todays_pred_price[0][0]),2)
        today_data = round(today_data[0],2)
        return tomorrow_pred_price, todays_pred_price, today_data
    
    def predict(self,df,ticker):
        if self.traverser.traverse(ticker):
            tomorrow_pred_price, todays_pred_price, today_data =  self.load_existing_model(df,ticker)
        else:
            tomorrow_pred_price, todays_pred_price, today_data =  self.create_new_model(df,ticker)
        return tomorrow_pred_price, todays_pred_price, today_data