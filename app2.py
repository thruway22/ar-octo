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

# Determine the maximum date for the slider
max_date = nav.index.max()

# Predefined date range selector
date_range_option = st.radio('Select Predefined Date Range',
                             ['all', '10y', '7y', '5y', '3y', '2y', '1y'], horizontal=True)

today = pd.to_datetime('today').normalize()
if date_range_option == '10y':
    start_date = today - pd.DateOffset(years=10)
elif date_range_option == '7y':
    start_date = today - pd.DateOffset(years=7)
elif date_range_option == '5y':
    start_date = today - pd.DateOffset(years=5)
elif date_range_option == '3y':
    start_date = today - pd.DateOffset(years=3)
elif date_range_option == '2y':
    start_date = today - pd.DateOffset(years=2)
elif date_range_option == '1y':
    start_date = today - pd.DateOffset(years=1)
else:
    start_date = pd.Timestamp('1990-01-01')

# Date range slider
start_date, end_date = st.slider("Select Date Range",
                                 min_value=start_date.to_pydatetime().date(),
                                 max_value=max_date.to_pydatetime().date(),
                                 value=(start_date.to_pydatetime().date(), max_date.to_pydatetime().date()))

# Filter the nav DataFrame based on the selected date range
filtered_nav = nav[(nav.index.date >= start_date) & (nav.index.date <= end_date)]

# Define a function to calculate annualized return
def calculate_annualized_return(group):
    if len(group) < 2:
        return None  # Not enough data to calculate return
    initial_nav = group.iloc[0]['nav']
    final_nav = group.iloc[-1]['nav']
    num_years = (group.index[-1] - group.index[0]).days / 365.25
    if num_years == 0:
        return None  # Avoid division by zero
    annualized_return = (final_nav / initial_nav) ** (1 / num_years) - 1
    return annualized_return


# Group by 'name' and apply the function to calculate annualized return for each fund
annualized_returns = filtered_nav.groupby('name').apply(calculate_annualized_return)

# Convert the result to a DataFrame
returns_df = annualized_returns.reset_index()
returns_df.columns = ['Fund', 'Annualized Return']

# Display the DataFrame
st.dataframe(returns_df.sort_values('Annualized Return', ascending=False))
