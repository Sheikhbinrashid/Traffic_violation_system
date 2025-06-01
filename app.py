# app.py

import os
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Constants
TOWNS = [
    'Harare', 'Bulawayo', 'Mutare', 'Gweru', 'Kadoma', 'Chinhoyi',
    'Bindura', 'Marondera', 'Norton', 'Masvingo', 'Chiredzi',
    'Mutoko', 'Chipinge', 'Rusape'
]
CSV_PATH = 'violations.csv'
SNAPSHOT_DIR = 'snapshots'

# Streamlit page config
st.set_page_config(
    page_title='Red-Light Violation Dashboard',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Sidebar navigation
page = st.sidebar.radio('Go to', ['Home', 'Dashboard'])

# Common styles
def load_data():
    # Read CSV with correct column names (including city)
    cols = ['timestamp','city','plate','light_color','snapshot']
    df = pd.read_csv(CSV_PATH, names=cols, header=0)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['week'] = df['timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
    return df

if page == 'Home':
    st.title('🚦 Video Analysis')
    st.markdown(
        """
        Upload a traffic video, select a town, and click **Analyze**.
        """
    )
    col1, col2 = st.columns([3,1])
    with col1:
        video_file = st.file_uploader('Upload Video', type=['mp4','avi'])
    with col2:
        location = st.selectbox('Town', ['National'] + TOWNS)
        analyze = st.button('Analyze', use_container_width=True)

    if analyze:
        if not video_file:
            st.error('Please upload a video.')
        else:
            st.info(f'Analyzing **{location}** video...')
            # TODO: integrate real analysis
            progress = st.progress(0)
            for i in range(1, 101):
                progress.progress(i)
            st.success('✅ Analysis complete!')
            st.balloons()
            st.markdown('Switch to **Dashboard** to see results.')

elif page == 'Dashboard':
    st.title('📊 Violation Analytics')
    if not os.path.exists(CSV_PATH):
        st.warning('No data found. Run analysis first on the Home page.')
        st.stop()

    df = load_data()
    # Filters
    col1, col2 = st.columns([2,3])
    with col1:
        selected_town = st.selectbox('Filter by Town', ['National'] + TOWNS)
        date_range = st.date_input(
            'Date Range',
            [df['timestamp'].min().date(), df['timestamp'].max().date()]
        )
    # Apply filters
    mask = (df['timestamp'].dt.date >= date_range[0]) & (df['timestamp'].dt.date <= date_range[1])
    if selected_town != 'National':
        mask &= (df['city'] == selected_town)
    data = df.loc[mask]

    # KPI cards
    total = len(data)
    avg_week = data.groupby('week').size().mean() if total else 0
    col3, col4, _ = st.columns([1,1,2])
    col3.metric('Total Violations', total)
    col4.metric('Avg per Week', f"{avg_week:.1f}")

    # Weekly Trend
    st.subheader('Weekly Trend')
    weekly = data.groupby('week').size().reset_index(name='count')
    brush = alt.selection(type='interval', encodings=['x'])
    base = alt.Chart(weekly).encode(
        x=alt.X('week:T', title='Week'),
        y=alt.Y('count:Q', title='Violations')
    )
    line = base.mark_line(point=True).add_selection(brush)
    bars = base.mark_bar().transform_filter(brush)
    st.altair_chart((line & bars).properties(height=300), use_container_width=True)

    # Heatmap by Town
    st.subheader('Weekly Violations by Town')
    heat_data = df.groupby(['week','city']).size().reset_index(name='count')
    if selected_town != 'National':
        heat_data = heat_data[heat_data['city'] == selected_town]
    heat = alt.Chart(heat_data).mark_rect().encode(
        x=alt.X('week:T', title='Week'),
        y=alt.Y('city:N', title='Town'),
        color=alt.Color('count:Q', title='Violations', scale=alt.Scale(scheme='reds'))
    ).properties(height=400)
    st.altair_chart(heat, use_container_width=True)

    # Detailed Table
    st.subheader('Detailed Logs')
    st.dataframe(data[['timestamp','city','plate','light_color','snapshot']].sort_values('timestamp', ascending=False))

    # Download CSV
    csv = data.to_csv(index=False)
    st.download_button('Download Data', csv, file_name='filtered_violations.csv')
