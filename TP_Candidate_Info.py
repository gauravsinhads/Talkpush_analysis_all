import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="TP_Candidate_Info Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and cache data
@st.cache_data
def load_data():
    return pd.read_csv('TalkpushCI_data_fetch.csv').query("INVITATIONDT >= '01/01/2024' & INVITATIONDT < '2/28/2025'")

tpci = load_data()
tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'])

# Generic data processing function
def get_top_data(tpci, column_name, period, top_n=10):
    if period:
        start_date = tpci['INVITATIONDT'].max() - pd.DateOffset(days=period)
        filtered_data = tpci[tpci['INVITATIONDT'] >= start_date]
    else:
        filtered_data = tpci
    
    counts = filtered_data[column_name].value_counts().nlargest(top_n).reset_index()
    counts.columns = [column_name, 'COUNT']
    return counts

# Color configuration
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", 
          "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Create unified dropdown
period_options = {
    "Daily (30 Days)": 30,
    "Weekly (12 Weeks)": 84,
    "Monthly (1 Year)": 365,
    "All Time": None
}

# Dashboard Title
st.title("TP_Candidate_Info Dashboard")

# Time period selector
selected_period = st.selectbox(
    "Select Time Period:",
    options=list(period_options.keys()),
    index=0,
    key="period_selector"
)

# Create charts
def create_chart(data, title, x_label, y_label='Count'):
    fig = px.bar(
        data,
        x=data.columns[0],
        y='COUNT',
        title=title,
        labels={data.columns[0]: x_label, 'COUNT': y_label},
        color='COUNT',
        color_continuous_scale=[colors[4], colors[2]]
    )
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        title_x=0.5
    )
    return fig

# Create columns for layout
col1, col2 = st.columns(2)
col3, _ = st.columns([2, 1])  # Adjust ratio for better spacing

with col1:
    campaign_data = get_top_data(tpci, 'CAMPAIGNTITLE', period_options[selected_period])
    st.plotly_chart(
        create_chart(campaign_data, 
                    'Top 10 Campaign Titles', 
                    'Campaign Title'),
        use_container_width=True
    )

with col2:
    source_data = get_top_data(tpci, 'SOURCE', period_options[selected_period])
    st.plotly_chart(
        create_chart(source_data, 
                    'Top 10 Sources', 
                    'Source'),
        use_container_width=True
    )

with col3:
    manager_data = get_top_data(tpci, 'ASSIGNEDMANAGER', period_options[selected_period])
    st.plotly_chart(
        create_chart(manager_data, 
                    'Top 10 Assigned Managers', 
                    'Assigned Manager'),
        use_container_width=True
    )

# Add some spacing
st.markdown("<br><br>", unsafe_allow_html=True)
