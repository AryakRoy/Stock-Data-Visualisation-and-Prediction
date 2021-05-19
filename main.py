import streamlit as st
from datetime import date
import yfinance as yf
from plotly import graph_objs as go

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title("Stock Analysis and Prediction")

stocks = ("AAPL","GOOG","MSFT","GME")
selected_stock = st.selectbox("Select Stock",stocks)

n_years = st.slider("Years of Prediction : ",1,4)
period = n_years * 365

@st.cache
def load_data(ticker):
    data_load_state.text("Loading Data...")
    data = yf.download(ticker,START,TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Load Data")
data = load_data(selected_stock)
data_load_state.text("Data Successfully Loaded")

st.subheader(f"{selected_stock} Raw Stock Data")
st.write(data.tail(50))

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True,yaxis_title="USD $")
    st.plotly_chart(fig)

plot_raw_data()