import streamlit as st
from datetime import date
import yfinance as yf
from plotly import graph_objs as go
from urllib import request
import pandas as pd
import base64

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="📈",
    layout="wide",
)

@st.cache
def load_stock_data(ticker):
    data_load_state.text("Loading Data...")
    data = yf.download(ticker,START,TODAY)
    data.reset_index(inplace=True)
    return data

@st.cache
def load_stock_list():
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = request.urlopen(url)
    html = response.read()
    data = pd.read_html(html,header = None)
    df = data[0]
    return df

container = st.beta_container()
col1, col2 = container.beta_columns([5,5])
st.sidebar.header("User Input Features")

df = load_stock_list()
sector = df.groupby('GICS Sector')
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sectors = st.sidebar.multiselect('Sector',sorted_sector_unique)
df_selected_sectors = df[df['GICS Sector'].isin(selected_sectors)]
st.sidebar.write(f"Companies : {df_selected_sectors.shape[0] or 0}")
col1.title("Stock Analysis and Prediction")
START =st.sidebar.date_input(label="Enter Start Date",value=date(2012,1,1))
TODAY = date.today().strftime("%Y-%m-%d")
if len(selected_sectors) != 0:
    stocks = df_selected_sectors.Symbol.values 
else:
    stocks = df.Symbol.values
selected_stock = st.sidebar.selectbox("Select Stock",stocks)

data = pd.DataFrame()
if selected_stock != None:
    data_load_state = st.text("Load Data")
    data = load_stock_data(selected_stock)
    data_load_state.text("Data Successfully Loaded")
    col1.subheader(f"{selected_stock} Raw Data")
    col1.write(data.tail(50))
    def filedownload(df):
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="{selected_stock}.csv">Download CSV File</a>'
        return href
    st.markdown(filedownload(df_selected_sectors), unsafe_allow_html=True)

if data.empty == False:
    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
        fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True,yaxis_title="USD $")
        col2.plotly_chart(fig)
    plot_raw_data()

st.header("Prediction")