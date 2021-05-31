import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import model_from_json
import os

class Predictor:
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
        with open(save_path, "w") as json_file:
            json_file.write(model_json)
        model.save_weights(save_path_2)

        last_60_days = data[-60:].values
        last_60_days_scaled = scaler.transform(last_60_days)
        X_test = []
        X_test.append(last_60_days_scaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
        pred_price = model.predict(X_test)
        pred_price = scaler.inverse_transform(pred_price)
        return pred_price[0][0]
    
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

        X_test = []
        X_test.append(last_60_days_scaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
        pred_price = model.predict(X_test)
        pred_price = scaler.inverse_transform(pred_price)
        return pred_price[0][0]