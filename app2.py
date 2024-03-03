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

# Calculate the minimum and maximum dates for the date range slider
min_dates = []
for fund in filtered_info['name']:
    fund_dates = nav[nav['name'] == fund].index
    if not fund_dates.empty:
        min_dates.append(fund_dates.min())
fund_min_date = max(min_dates) if min_dates else nav.index.min()
max_date = nav.index.max()

date_range_option = st.radio('Select Predefined Date Range',
                             ['all', '10y', '7y', '5y', '3y', '2y', '1y'], horizontal=True)

today = pd.to_datetime('today').normalize()
if date_range_option == '10y':
    predefined_min_date = today - pd.DateOffset(years=10)
elif date_range_option == '7y':
    predefined_min_date = today - pd.DateOffset(years=7)
elif date_range_option == '5y':
    predefined_min_date = today - pd.DateOffset(years=5)
elif date_range_option == '3y':
    predefined_min_date = today - pd.DateOffset(years=3)
elif date_range_option == '2y':
    predefined_min_date = today - pd.DateOffset(years=2)
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

# Update start_date and end_date based on the selected date range option
start_date = min_date.to_pydatetime().date()
end_date = max_date.to_pydatetime().date()

# Filter the nav DataFrame based on the selected date range
filtered_nav = nav[(nav.index.date >= start_date) & (nav.index.date <= end_date)]

# Define a function to calculate annualized return
def calculate_annualized_return(group):
    initial_nav = group.iloc[0]['nav']
    final_nav = group.iloc[-1]['nav']
    num_years = (group.index[-1] - group.index[0]).days / 365.25
    annualized_return = (final_nav / initial_nav) ** (1 / num_years) - 1
    return annualized_return

# Group by 'name' and apply the function to calculate annualized return for each fund
annualized_returns = filtered_nav.groupby('name').apply(calculate_annualized_return)

# Convert the result to a DataFrame
returns_df = annualized_returns.reset_index()
returns_df.columns = ['Fund', 'Annualized Return']

# Display the DataFrame
st.dataframe(returns_df.sort_values('Annualized Return', ascending=False))