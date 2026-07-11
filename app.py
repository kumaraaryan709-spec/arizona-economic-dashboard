import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Config
st.set_page_config(page_title="Arizona Economic Dashboard", layout="wide")
st.title("🌵 Arizona Legislative & Regional Economic Dashboard")
st.markdown("Designed for public policy data analysis and legislative briefing.")

# 2. Key configuration
API_KEY = "5c005c1076e52f6e561016655c245351"

# Mapping friendly names to FRED Series IDs
metrics = {
    'Arizona Unemployment Rate (%)': 'AZUR',
    'Phoenix-Mesa Consumer Price Index (Inflation)': 'CUURS49ASF0',
    'Arizona Total Nonfarm Payrolls (Employment)': 'AZNA'
}

st.sidebar.header("Dashboard Filters")
selected_name = st.sidebar.selectbox("Select Economic Metric to Analyze:", list(metrics.keys()))
series_id = metrics[selected_name]

# 3. Data Fetching Function
@st.cache_data(ttl=86400)
def fetch_fred_data(series):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={API_KEY}&file_type=json"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"FRED API Error: Received status code {response.status_code}")
        return pd.DataFrame()
        
    data_json = response.json()
    if 'observations' not in data_json:
        st.error("FRED API Error: No observations found in data.")
        return pd.DataFrame()
        
    observations = data_json['observations']
    df = pd.DataFrame(observations)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.dropna()

try:
    # Get data from 2020 onward
    df_raw = fetch_fred_data(series_id)
    
    if not df_raw.empty:
        df = df_raw[df_raw['date'] >= '2020-01-01']

        # 4. Interactive Chart
        fig = px.line(df, x='date', y='value', markers=True,
                      title=f"{selected_name} (2020 - Present)",
                      labels={'value': 'Value', 'date': 'Date'})
        fig.update_traces(line_color='#8C1D40') # ASU Maroon
        st.plotly_chart(fig, use_container_width=True)

        # 5. Briefing Note Generator
        st.subheader("💡 Legislative Briefing Note")
        current_val = df['value'].iloc[-1]
        prev_val = df['value'].iloc[-2]
        diff = current_val - prev_val
        latest_date = df['date'].iloc[-1].strftime('%B %Y')

        st.info(f"As of **{latest_date}**, the {selected_name} stands at **{current_val}**. "
                f"Compared to the previous reporting period, this indicator changed by **{diff:+.2f}**. "
                f"This dataset is utilized to monitor regional macroeconomic shocks for the state budget.")
    else:
        st.warning("No data returned from the API. Please double check if your FRED API key is active or if the network is clear.")

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
