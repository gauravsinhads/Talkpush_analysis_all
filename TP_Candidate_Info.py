import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Iqor Talkpush Dashboard", layout="wide" )



# Custom CSS for button styling
st.markdown("""
<style>
    /* Button container styling */
    .sidebar .sidebar-content .block-container {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    
    /* Button styling */
    div.stButton > button {
        width: 80%;
        border-radius: 4px 4px 0 0;
        border: 1px solid #e0e0e0;
        background-color: #f0f2f6;
        color: black;
        text-align: left;
        padding: 8px 12px;
        margin: 0;
    }
    
    /* Selected button styling */
    div.stButton > button:focus {
        background-color: white;
        border-bottom: 2px solid #0d6efd;
        font-weight: bold;
    }
    
    /* Hover effect */
    div.stButton > button:hover {
        background-color: #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Set up input widgets
st.logo(image="Images/Iqorlogo.png", 
        icon_image="Images/iQor-corporate.png")    

# Sidebar navigation buttons
st.sidebar.title("Pages")

def set_page(page_name):
    st.session_state.page = page_name

pages = ["Home", "Page 1", "Page 2", "Page 3", "Page 4"]

for page in pages:
    st.sidebar.button(
        page,
        on_click=set_page,
        args=(page,),
        key=page
    )
#PAGE HOME_____________________________________________________________________________________________    
# Page content
if st.session_state.page == "Home":
    st.title("HOME")

    # bar dropdown
    col = st.columns(3)
    with col[2]: aggregation_option = st.selectbox("Time Period", ["Last 30 days", "Last 12 Weeks", "Last 12 Months"])
    today = pd.Timestamp.today() # Get today's date
    # Load data
    @st.cache_data
    def load_data(): return pd.read_csv("TP_raw_data1.csv")
    df = load_data()
    
    df["DATE_DAY"] = pd.to_datetime(df["DATE_DAY"])
    
    # Apply Aggregation based on Selection
    if aggregation_option == "Last 12 Months":
        df["DATE_GROUP"] = df["DATE_DAY"].dt.strftime("%b-%Y")  # Format as Feb-2024
    elif  aggregation_option == "Last 12 Weeks":
        df["DATE_GROUP"] = "W_" + (df["DATE_DAY"] + pd.to_timedelta(6 - df["DATE_DAY"].dt.weekday, unit="D")).dt.strftime("%b-%d")
    else:
        df["DATE_GROUP"] = pd.to_datetime(df["DATE_DAY"], format='%b-%d-%Y')
    # Apply Aggregation based on Selection2
    if aggregation_option == "Last 30 days":
        df = df[df["DATE_DAY"] >= today - pd.Timedelta(days=30)]
    elif  aggregation_option == "Last 12 Weeks":
        df = df[df["DATE_DAY"] >= today - pd.Timedelta(weeks=12)]
    else:
        df["DATE_GROUP2"] = pd.to_datetime(df["DATE_DAY"], format='%b-%d-%Y')

    df_fil = df[df["TALKSCORE_OVERALL"] > 0]

    # FIG1 and FIG1w Aggregate Data
    df_avg_overall = df_fil.groupby("DATE_GROUP", as_index=False)["TALKSCORE_OVERALL"].mean()
    df_avg_overall["TEXT_LABEL"] = df_avg_overall["TALKSCORE_OVERALL"].apply(lambda x: f"{x:.2f}")

     # FIG 1: Clustered Column (Talkscore Overall)
    fig1 = px.line(df_avg_overall, 
               x="DATE_GROUP", y ="TALKSCORE_OVERALL",      
               markers=True,  # Add points (vertices)
               title="Talkscore-Overall average", labels={"DATE_GROUP": "Time", "TALKSCORE_OVERALL": "Avg Talkscore"},
               line_shape="linear", text="TEXT_LABEL")  # Use formatted text
        # Update the trace to display the text on the chart
    fig1.update_traces( textposition="top center", fill='tozeroy' , fillcolor="rgba(0, 0, 255, 0.2)")

    #FIG2 and FIG2w column stacked avg components
            # Convert score columns to numeric
    score_columns = ["TALKSCORE_VOCAB", "TALKSCORE_FLUENCY", "TALKSCORE_GRAMMAR", "TALKSCORE_PRONUNCIATION"]
    df_fil[score_columns] = df_fil[score_columns].apply(pd.to_numeric, errors="coerce")
            # Group by DATE_GROUP and compute averages
    group_avg = df_fil.groupby("DATE_GROUP")[score_columns].mean().reset_index()
            # Melt the DataFrame for Plotly
    df_avg_components = group_avg.melt(id_vars=["DATE_GROUP"],  value_vars=score_columns, var_name="Score Type",  value_name="Average Score")
    df_avg_components["TEXT_LABEL"] = df_avg_components["Average Score"].apply(lambda x: f"{x:.2f}")

        # FIG 2: Stacked Column (Component Breakdown)
    fig2 = px.line(df_avg_components, 
        x="DATE_GROUP",     y="Average Score", 
        color="Score Type",  # Different lines for each component
        markers=True, title="Talkscore Components Month over Month", labels={"DATE_GROUP": "Time", "Average Score": "Score"},
        line_shape="linear",  text="TEXT_LABEL" ) # Show values on points
     # Position text labels on the chart
    fig2.update_traces(textposition="top center")
    
    # Input widgets
    col = st.columns(2)
    # Display Charts
    with col[0]:st.plotly_chart(fig1)
    with col[1]:st.plotly_chart(fig2)


#PAGE 1_______________________________________________________________________________________________
elif st.session_state.page == "Page 1":

    # Load data
    tpci = pd.read_excel("TalkpushCI_data_fetch.xlsx")
    tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'])

    # Define colors for graphs
    colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

    # bar dropdown
    cols = st.columns(3)
    with cols[2]: time_filter = st.selectbox("Time Period", ["Last 30 days", "Last 12 Weeks", "Last 1 Year", "All Time"])
    st.title("page 1")

    # Filter data based on selection
    max_date = tpci['INVITATIONDT'].max()
    if time_filter == "Last 30 days":
        filtered_data = tpci[tpci['INVITATIONDT'] >= max_date - pd.DateOffset(days=30)]
        date_freq = 'D'
    elif time_filter == "Last 12 Weeks":
        filtered_data = tpci[tpci['INVITATIONDT'] >= max_date - pd.DateOffset(weeks=12)]
        date_freq = 'W'
    elif time_filter == "Last 1 Year":
        filtered_data = tpci[tpci['INVITATIONDT'] >= max_date - pd.DateOffset(years=1)]
        date_freq = 'M'
    else:
        filtered_data = tpci.copy()
        date_freq = 'M'

    # Graph 1: Lead Count Trend
    lead_trend = filtered_data.resample(date_freq, on='INVITATIONDT').count()
    fig1 = px.line(lead_trend, x=lead_trend.index, y='RECORDID', title='Lead Count Trend', labels={'RECORDID': 'Counts'}, color_discrete_sequence=[colors[0]])
    st.plotly_chart(fig1, use_container_width=True)

    # Graph 2: Top 10 Campaign Titles
    top_campaigns = filtered_data['CAMPAIGNTITLE'].value_counts().nlargest(10)
    fig2 = px.bar(top_campaigns, x=top_campaigns.index, y=top_campaigns.values, title='Top 10 Campaign Titles', labels={'y': 'Counts'}, color_discrete_sequence=[colors[2]])
    st.plotly_chart(fig2, use_container_width=True)

    # Graph 3: Top 10 Source Counts
    top_sources = filtered_data['SOURCE'].value_counts().nlargest(10)
    fig3 = px.bar(top_sources, x=top_sources.index, y=top_sources.values, title='Top 10 Source Counts', labels={'y': 'Counts'}, color_discrete_sequence=[colors[3]])
    st.plotly_chart(fig3, use_container_width=True)

    # Graph 4: Top 10 Assigned Manager Counts
    top_managers = filtered_data['ASSIGNEDMANAGER'].value_counts().nlargest(10)
    fig4 = px.bar(top_managers, x=top_managers.index, y=top_managers.values, title='Top 10 Assigned Manager Counts', labels={'y': 'Counts'}, color_discrete_sequence=[colors[4]])
    st.plotly_chart(fig4, use_container_width=True)

    # Graph 5: Top 10 Folder Occurrences
    top_folders = filtered_data['FOLDER'].value_counts().nlargest(10)
    fig5 = px.bar(top_folders, x=top_folders.index, y=top_folders.values, title='Top 10 Folder Occurrences', labels={'y': 'Counts'}, color_discrete_sequence=[colors[5]])
    st.plotly_chart(fig5, use_container_width=True)

    # Graph 6: Top 5 Completion Methods
    top_completion_methods = filtered_data['COMPLETIONMETHOD'].value_counts().nlargest(5)
    fig6 = px.bar(top_completion_methods, x=top_completion_methods.index, y=top_completion_methods.values, title='Top 5 Completion Methods', labels={'y': 'Counts'}, color_discrete_sequence=[colors[6]])
    st.plotly_chart(fig6, use_container_width=True)

elif st.session_state.page == "page 2":
    st.title("page 2")
    # Your content here

elif st.session_state.page == "page 3":
    st.title("page 2")
    # Your content here

elif st.session_state.page == "page 4":
    st.title("page 2")
    # Your content here

# streamlit run TP_Candidate_Info.py
