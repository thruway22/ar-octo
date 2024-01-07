import streamlit as st

st.title('Test')

info = pd.read_csv('info.csv')

nav1 = pd.read_csv('nav1.csv')
nav2 = pd.read_csv('nav2.csv')
nav3 = pd.read_csv('nav3.csv')
nav = pd.concat([nav1, nav2, nav3])

fund = st.selectbox(info[['Fund Name']])

st.plot(nav[nav['name'] == fund].nav.plot())