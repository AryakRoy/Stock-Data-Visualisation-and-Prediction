import streamlit as st
from datetime import date
import yfinance as yf
from plotly import graph_objs as go
from urllib import request
import pandas as pd
import base64
from traverse import Traverse
from Stock_Sentiment_Analysis import Sentiment_Analyzer
from prediction import Predictor

st.set_page_config(
    page_title="Stock Sensei",
    page_icon="📈",
    layout="wide",
)

traverser = Traverse()
sentiment_analyzer = Sentiment_Analyzer()
predictor = Predictor()

@st.cache(allow_output_mutation=True)
def load_stock_data(ticker):
    data = yf.download(ticker,START,TODAY)
    stock_data = yf.Ticker(ticker)
    data.reset_index(inplace=True)
    return (data, stock_data)

@st.cache
def load_stock_list():
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = request.urlopen(url)
    html = response.read()
    data = pd.read_html(html,header = None)
    df = data[0]
    return df

st.title("Stock Analysis and Prediction")
st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikepedia) and its corresponding **stock closing price** (year-to-date).
* **Python Libraries :** base64, pandas, numpy, streamlit, yfinance, matplotlib, plotly, sklearn, keras
* **Data Source :** [Wikepedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)      [Yahoo Finance](https://in.finance.yahoo.com/)         [finviz](https://finviz.com)
""")
st.write('---')
st.sidebar.header("User Input Features")

df = load_stock_list()
sector = df.groupby('GICS Sector')
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sectors = st.sidebar.multiselect('Sector',sorted_sector_unique)
df_selected_sectors = df[df['GICS Sector'].isin(selected_sectors)]
st.sidebar.write(f"Companies : {df_selected_sectors.shape[0] or 0}")

START =st.sidebar.date_input(label="Enter Start Date",value=date(2016,1,1))
TODAY = date.today().strftime("%Y-%m-%d")

if len(selected_sectors) != 0:
    stocks = df_selected_sectors.Symbol.values 
else:
    stocks = df.Symbol.values
selected_stock = st.sidebar.selectbox("Select Stock",stocks)

data = pd.DataFrame()
if selected_stock != None:
    data, stock_details = load_stock_data(selected_stock)
    string_logo = f"<img src={stock_details.info['logo_url']}>"
    st.markdown(string_logo,unsafe_allow_html=True)
    st.header(stock_details.info["longName"])
    st.info(stock_details.info["longBusinessSummary"])
    container = st.beta_container()
    col1, col2 = container.beta_columns([5,5])
    col1.subheader(f"Raw Data")
    col1.write(data.tail(50))
    traverser.traverse(selected_stock)
    def filedownload(df):
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="{selected_stock}.csv">Download CSV File</a>'
        return href
    col1.markdown(filedownload(df_selected_sectors), unsafe_allow_html=True)

if data.empty == False:
    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
        fig.layout.update(title_text="Time Series Chart", xaxis_rangeslider_visible=True,yaxis_title="USD $")
        col2.plotly_chart(fig)
    plot_raw_data()

@st.cache()
def predict_price():
    sentiment_analysis_result = sentiment_analyzer.Analysis(selected_stock)
    if traverser.is_file_in_directory(selected_stock):
        price = predictor.load_existing_model(data,selected_stock)
    else:
        price = predictor.create_new_model(data,selected_stock)
    return price,sentiment_analysis_result
 
st.write('---')
st.header("Prediction")
if st.button("Predict"):
    loading_message = st.success("Loading Model...")
    if selected_stock != None:
        price, sentiment_analysis_result = predict_price()
    loading_message.success("Completed")
    st.write(f"Tomorrow's Prediction : {price}")
    st.write(sentiment_analysis_result)
else:
    st.write("Click the button above to run the prediction analysis")