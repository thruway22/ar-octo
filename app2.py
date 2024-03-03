import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def load_data():
    info = pd.read_csv('info.csv')
    nav = pd.concat([pd.read_csv(f'nav{i}.csv') for i in range(1, 4)])
    nav = nav.drop(0)
    nav['date'] = pd.to_datetime(nav['date'])
    return info, nav.set_index('date')

def filter_data(info, nav, cat, mgr, start_date, end_date):
    filtered_info = info
    if cat:
        filtered_info = filtered_info[filtered_info['cat'].isin(cat)]
    if mgr:
        filtered_info = filtered_info[filtered_info['mgr'].isin(mgr)]
    selected_funds = filtered_info['name'].unique()
    return nav[(nav.index.date >= start_date) & (nav.index.date <= end_date) & (nav['name'].isin(selected_funds))]

def calculate_annualized_returns(filtered_nav):
    def annualized_return(group):
        if len(group) < 2:
            return None
        initial_nav = group.iloc[0]['nav']
        final_nav = group.iloc[-1]['nav']
        num_years = (group.index[-1] - group.index[0]).days / 365.25
        if num_years == 0:
            return None
        return (final_nav / initial_nav) ** (1 / num_years) - 1

    return filtered_nav.groupby('name')['nav'].apply(annualized_return).reset_index(name='Annualized Return')

def main():
    st.title('Test')

    info, nav = load_data()

    cat = st.multiselect('Category', info['cat'].unique())
    mgr = st.multiselect('Manager', info['mgr'].unique())

    max_date = nav.index.max().date()
    start_date, end_date = st.slider("Select Date Range", min_value=pd.Timestamp('1990-01-01').date(), max_value=max_date, value=(pd.Timestamp('1990-01-01').date(), max_date))

    filtered_nav = filter_data(info, nav, cat, mgr, start_date, end_date)
    returns_df = calculate_annualized_returns(filtered_nav)

    st.dataframe(returns_df.sort_values('Annualized Return', ascending=False))

if __name__ == "__main__":
    main()
