import base64
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from stockA import analyze
# Function to encode the header image
st.set_page_config(layout="wide")
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Function to set the header image
def set_header_image(png_file):
    bin_str = get_base64(png_file)
    header_img = f'''
    <style>
    .header-img {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        height: 120px; /* Banner height */
        width: 100%;
        background-position: center;
    }}
    </style>
    <div class="header-img"></div>
    '''
    st.markdown(header_img, unsafe_allow_html=True)

# Function to set the black background
def set_black_background():
    st.markdown(
        '''
        <style>
        .stApp {{
            background-color: black;
            color: white;
        }}
        </style>
        ''',
        unsafe_allow_html=True
    )

# Function to scrape ETF data
def scrape_etf_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table_rows = soup.find_all("tr")

        # Prepare the list to store the stock data
        stock_data = []

        # Loop through each row in the table starting from index 1 (skip header row)
        for row in table_rows[1:]:
            cells = row.find_all("td")
            if len(cells) >= 4:
                symbol = cells[1].text.strip()  # Symbol
                name = cells[2].text.strip()    # Name of the company
                weight = cells[3].text.strip()  # Weight percentage
                shares = cells[4].text.strip()  # Weight percentage
                # Append to stock data list
                stock_data.append([symbol, name, weight, shares])

        # Create a pandas DataFrame for better table formatting
        df = pd.DataFrame(stock_data, columns=["Symbol", "Name", "% Weight", "Shares"])

        # Return the DataFrame
        return df
    else:
        raise Exception(f"Failed to fetch data from URL: {url}. Status code: {response.status_code}")

# ETF URLs
etf_urls = {
    "BOTZ (Global X Robotics & AI ETF)": "https://stockanalysis.com/etf/botz/holdings/",
    "AIQ (Global X Artificial Intelligence & Technology ETF)": "https://stockanalysis.com/etf/aiq/holdings/",
    "ARTY (Global X Artificial Intelligence & Tech)": "https://stockanalysis.com/etf/arty/holdings/",
    "ARKF (ARK Fintech Innovation ETF)": "https://stockanalysis.com/etf/arkf/holdings/",
    "ROBT (First Trust Robotics & AI ETF)": "https://stockanalysis.com/etf/robt/holdings/"
}

# Header image
set_header_image('aigent.png')

# Set black background
set_black_background()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["ETFs", "Stock Analyzer", "IPOs", "News"])

# Page content
if page == "ETFs":
    st.header("Analyze the Top AI ETFs")
    # User selects ETF or AIgent's Choice options
    options = ["AIgent's Choice"] + list(etf_urls.keys())
    selected_etf = st.selectbox("Select an ETF to analyze:", options)
    
    if selected_etf == "AIgent's Choice":
        # Scrape data from all ETFs
        st.write("AIgent's Choice is selecting the most common stocks across the top AI ETFs.")
        etf_data = {}
        for etf_name, url in etf_urls.items():
            try:
                etf_data[etf_name] = scrape_etf_data(url)
            except Exception as e:
                st.error(f"Failed to scrape {etf_name}: {e}")
        
        # Find common stocks across ETFs based on weight
        all_stocks = pd.concat(etf_data.values(), ignore_index=True)
        all_stocks["% Weight"] = pd.to_numeric(all_stocks["% Weight"].str.replace('%', ''), errors='coerce').fillna(0)
        common_stocks = all_stocks.groupby("Symbol").agg({"Name": "first", "% Weight": "sum"}).reset_index()
        common_stocks = common_stocks.sort_values(by="% Weight", ascending=False).reset_index(drop=True)
        common_stocks = common_stocks.head(50)
        
        # Display results
        st.write("### Common Stocks Across ETFs")
        if not common_stocks.empty:
            # Convert symbols to clickable buttons that navigate to Stock Analyzer
            common_stocks['Symbol'] = common_stocks['Symbol'].apply(
                lambda x: f'<a href="?page=Stock Analyzer&ticker={x}">{x}</a>'
            )
            st.markdown(
                common_stocks[["Symbol", "Name"]].to_html(escape=False, index=False), 
                unsafe_allow_html=True
            )
        else:
            st.write("No common stocks found.")
    
    else:
        # Get URL based on selection
        selected_url = etf_urls[selected_etf]
        
        # Scrape and display ETF data
        stock_data = scrape_etf_data(selected_url)
        if stock_data is not None and not stock_data.empty:
            st.write("### Holdings")
            # Convert symbols to clickable buttons that navigate to Stock Analyzer
            stock_data['Symbol'] = stock_data['Symbol'].apply(
                lambda x: f'<a href="?page=Stock Analyzer&ticker={x}">{x}</a>'
            )
            st.markdown(
                stock_data.to_html(escape=False, index=False), 
                unsafe_allow_html=True
            )
        else:
            st.write("No stock data available.")

elif page == "Stock Analyzer":
    st.header("Stock Analyzer")
    st.write("Analyze a stock by entering its ticker symbol below:")

    # Check if ticker is passed from ETFs page
    ticker = st.query_params.get("ticker", "")

    # Input for the ticker symbol (always keep this)
    manual_ticker = st.text_input("Enter the ticker symbol of the stock (e.g., 'AAPL', 'NVDA', 'TSLA'):")

    # Determine which ticker to use (prioritize passed ticker, then manual input)
    final_ticker = ticker or manual_ticker

    # Button to trigger the analysis
    if st.button("Analyze") or ticker:
        if final_ticker:  # Ensure the user has entered a ticker
            st.write(f"Analyzing stock: {final_ticker}")
            try:
                # Run the analyze function and display the result
                analysis_output = analyze(final_ticker)
                st.text_area("Stock Analysis Output", analysis_output, height=400)
            except Exception as e:
                st.error(f"An error occurred during the analysis: {str(e)}")
        else:
            st.warning("Please enter a valid ticker symbol to proceed.")
elif page == "IPOs":
    st.header("IPOs")
    st.write("Work in progress...")
    # Add IPO-related functionality here

elif page == "News":
    st.header("News")
    st.write("Work in progress...")
    # Add news-related functionality here