import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title('Test')

info = pd.read_csv('info.csv')
info.columns = ['mgr', 'name', 'code', 'date', 'cat', 'short_name',
                'sub_cat', 'obj', 'bm', 'risk', 'inception_price',
                'unit_holder', 'investment']

nav1 = pd.read_csv('nav1.csv')
nav2 = pd.read_csv('nav2.csv')
nav3 = pd.read_csv('nav3.csv')
nav = pd.concat([nav1, nav2, nav3])
nav = nav.drop(0)

nav.columns = ['mgr', 'name', 'nav', 'ccy', 'date', 'ytd', 'aum']
nav['date'] = pd.to_datetime(nav['date'])
nav = nav.set_index('date')

cat = st.multiselect('cat', info.cat.unique(), default=None)
mgr = st.multiselect('mgr', info.mgr.unique(), default=None)
selected_funds = st.multiselect('Select Funds', info['name'].unique())

filtered_info = info
if cat:
    filtered_info = filtered_info[filtered_info['cat'].isin(cat)]
if mgr:
    filtered_info = filtered_info[filtered_info['mgr'].isin(mgr)]


min_dates = []
for fund in selected_funds:
    fund_dates = nav[nav['name'] == fund]['date']
    if not fund_dates.empty:
        min_dates.append(fund_dates.min())
min_date = max(min_dates) if min_dates else nav['date'].min()
max_date = nav['date'].max()

start_date, end_date = st.slider("Select Date Range", 
                                 min_value=min_date.to_pydatetime().date(), 
                                 max_value=max_date.to_pydatetime().date(), 
                                 value=(min_date.to_pydatetime().date(), max_date.to_pydatetime().date()))


fig = go.Figure()

for fund in selected_funds:
    fund_df = nav[(nav['name'] == fund) & (nav.index.date >= start_date) & 
                  (nav.index.date <= end_date)]
    
    # Calculate daily percentage change
    fund_df['pct_change'] = fund_df['nav'].pct_change()

    # Calculate cumulative percentage change
    cumulative_pct_change = (1 + fund_df['pct_change']).cumprod() - 1

    fig.add_trace(go.Scatter(x=fund_df.index, y=cumulative_pct_change, mode='lines', name=fund))


# Update layout
fig.update_layout(
    xaxis=dict(rangeslider=dict(visible=True), type="date"),
    yaxis_title='Normalized NAV (%)',
    title='NAV Comparison of Selected Funds',
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    height=600 
)

# Plot
st.plotly_chart(fig) 