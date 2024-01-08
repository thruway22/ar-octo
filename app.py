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


min_dates = []
for fund in selected_funds:
    fund_dates = nav[nav['name'] == fund].index
    if not fund_dates.empty:
        min_dates.append(fund_dates.min())
fund_min_date = max(min_dates) if min_dates else nav.index.min()
max_date = nav.index.max()

date_range_option = st.radio('Select Predefined Date Range',
    ['all', '10y', '7y', '5y', '3y', '1y'], horizontal=True)

today = pd.to_datetime('today').normalize()
if date_range_option == '10y':
    predefined_min_date = today - pd.DateOffset(years=10)
elif date_range_option == '7y':
    predefined_min_date = today - pd.DateOffset(years=7)
elif date_range_option == '5y':
    predefined_min_date = today - pd.DateOffset(years=5)
elif date_range_option == '3y':
    predefined_min_date = today - pd.DateOffset(years=3)
elif date_range_option == '1y':
    predefined_min_date = today - pd.DateOffset(years=1)
else:
    predefined_min_date = fund_min_date

# Use the later of the two min dates (fund_min_date or predefined_min_date)
min_date = max(fund_min_date, predefined_min_date)


# Date range slider
start_date, end_date = st.slider("Select Date Range", 
                                 min_value=min_date.to_pydatetime().date(), 
                                 max_value=max_date.to_pydatetime().date(), 
                                 value=(min_date.to_pydatetime().date(), max_date.to_pydatetime().date()))

fig = go.Figure()

annualized_returns = []

for fund in selected_funds:
    fund_df = nav[(nav['name'] == fund) & (nav.index.date >= start_date) & 
                  (nav.index.date <= end_date)]
    
    # Calculate daily percentage change
    fund_df['pct_change'] = fund_df['nav'].pct_change()

    # Calculate cumulative percentage change
    cumulative_pct_change = (1 + fund_df['pct_change']).cumprod() - 1

    fig.add_trace(go.Scatter(x=fund_df.index, y=cumulative_pct_change, mode='lines', name=fund))

    if not fund_df.empty:
        initial_nav = fund_df.iloc[0]['nav']
        final_nav = fund_df.iloc[-1]['nav']
        num_years = (fund_df.index[-1] - fund_df.index[0]).days / 365.25
        annualized_return = (final_nav / initial_nav) ** (1 / num_years) - 1
        annualized_returns.append({'Fund': fund, 'Annualized Return': annualized_return})

# Create DataFrame for display
returns_df = pd.DataFrame(annualized_returns)


# Update layout
fig.update_layout(
    yaxis_title='Normalized NAV (%)',
    title='NAV Comparison of Selected Funds',
    legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
    height=700
)

# Plot
st.plotly_chart(fig, use_container_width=True) 

st.write("Annualized Rate of Return for Selected Funds:", returns_df * 100)