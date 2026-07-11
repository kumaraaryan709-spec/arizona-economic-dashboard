import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Config
st.set_page_config(page_title="Arizona Economic Dashboard", layout="wide")
st.title("🌵 Arizona Legislative & Regional Economic Dashboard")
st.markdown("Designed for public policy data analysis and legislative briefing.")

# 2. API Key Configuration
try:
    API_KEY = st.secrets["FRED_API_KEY"]
except:
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
    url = f"https://api.stlouisfed.org/api/fred/series/observations?series_id={series}&api_key={API_KEY}&file_type=json"
    response = requests.get(url).json()
    observations = response['observations']
    df = pd.DataFrame(observations)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.dropna()

try:
    # Get data from 2020 onward
    df_raw = fetch_fred_data(series_id)
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

except Exception as e:
    st.error("Could not fetch data. Verify your internet connection or API key.")