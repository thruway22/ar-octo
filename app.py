import streamlit as st
import pandas as pd


st.title('Test')

info = pd.read_csv('info.csv')

nav1 = pd.read_csv('nav1.csv')
nav2 = pd.read_csv('nav2.csv')
nav3 = pd.read_csv('nav3.csv')
nav = pd.concat([nav1, nav2, nav3])
nav = nav.drop(0)

nav.columns = ['mgr', 'name', 'nav', 'ccy', 'date', 'ytd', 'aum']
nav['date'] = pd.to_datetime(nav['date'])
nav = nav.set_index('date')

fund = st.selectbox('fund', info[['Fund Name']])

# if fund:
#     df = nav[nav['name'] == fund]
#     fig, ax = plt.subplots()
#     df['nav'].plot(ax=ax)
#     st.pyplot(fig)