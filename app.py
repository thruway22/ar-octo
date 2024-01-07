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

filtered_info = info

if cat:
    filtered_info = filtered_info[filtered_info['cat'].isin(cat)]
if mgr:
    filtered_info = filtered_info[filtered_info['mgr'].isin(mgr)]

selected_funds = st.multiselect('Select Funds', filtered_info['name'].unique())

min_date = nav.index.min().to_pydatetime().date()
max_date = nav.index.max().to_pydatetime().date()

start_date, end_date = st.slider("Select Date Range", 
                                 min_value=min_date, 
                                 max_value=max_date, 
                                 value=(min_date, max_date))

fig = go.Figure()

for fund in selected_funds:
    df = nav[(nav.index.date >= start_date) & 
             (nav.index.date <= end_date) & 
             (nav['name'] == fund)]
    
    normalized_nav = (fund_df['nav'] / fund_df['nav'].iloc[0]) * 100
    
    fig.add_trace(go.Scatter(x=fund_df.index, y=normalized_nav, mode='lines', name=fund))

# Update layout
fig.update_layout(
    xaxis=dict(rangeslider=dict(visible=True), type="date"),
    yaxis_title='Normalized NAV (%)',
    title='NAV Comparison of Selected Funds'
)

# Plot
st.plotly_chart(fig) 