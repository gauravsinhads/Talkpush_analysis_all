import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="iQor Talkpush Dashboard", layout="wide" )

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
    st.title("Overview data")

    # bar dropdown
    col = st.columns(3)
    with col[2]: aggregation_option = st.selectbox("Time Period", [ "Last 30 days","Last 12 Weeks","Last 12 Months"])
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

    # FIG1 Aggregate Data
    df_avg_overall = df_fil.groupby("DATE_GROUP", as_index=False)["TALKSCORE_OVERALL"].mean()
    df_avg_overall["TEXT_LABEL"] = df_avg_overall["TALKSCORE_OVERALL"].apply(lambda x: f"{x:.2f}")
    # FIG2 count of leads
    df_CountLeads = df.groupby(["DATE_GROUP"], as_index=False)["DATE_DAY"].count()

    # Create metrics columns
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Average Overall Talkscore")
        st.area_chart(df_avg_overall.set_index("DATE_GROUP")["TALKSCORE_OVERALL"], 
                 height=300, use_container_width=True)
    with cols[1]:
        st.subheader("Trend of Lead Counts")
        st.bar_chart(df_CountLeads.set_index("DATE_GROUP")["DATE_DAY"],
                 height=300, use_container_width=True)

    #FIG2 and FIG2w column stacked avg components
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
       
    # Display Charts
    st.plotly_chart(fig2)

    #FIG 3 Uncompleted and completed test
        # Create calculated fields
    test_summary = df.groupby(["DATE_GROUP", "CAMP_SITE"], as_index=False)["TEST_COMPLETED"].sum()

    # FIG 3 Create Line Chart
    fig3 =  px.bar(test_summary,
        x="DATE_GROUP", y="TEST_COMPLETED", 
        color="CAMP_SITE",  text="TEST_COMPLETED",
        barmode="group",  title="Test Completion Status",
        labels={"TEST_COMPLETED": "Total Tests Completed", "DATE_GROUP": "time", "CAMP_SITE": "Camp Site"}   )
        # Format labels (rounded values)
    fig3.update_traces(textposition="inside")
    fig3.update_layout(xaxis_title="time", yaxis_title="Total Test Completed", bargap=0.2)
    
    # Display Charts
    st.plotly_chart(fig3)

    # FIG 4 Create calculated fields - calculate percentages
    total_tests = df.groupby("DATE_GROUP", as_index=False)["TEST_COMPLETED"].count()
    test_summary = test_summary.merge(total_tests, on="DATE_GROUP", suffixes=('', '_TOTAL'))
    test_summary['PERCENTAGE_COMPLETED'] = (test_summary['TEST_COMPLETED'] / test_summary['TEST_COMPLETED_TOTAL']) * 100
    # FIG 4 Create Line Chart
    fig4 = px.line(test_summary,
        x="DATE_GROUP", y="PERCENTAGE_COMPLETED", 
        color="CAMP_SITE", 
        markers=True,  # Add markers to each data point
        title="Test Completion Status (%)",
        labels={
            "PERCENTAGE_COMPLETED": "Percentage of Tests Completed", 
            "DATE_GROUP": "Time", 
            "CAMP_SITE": "Camp Site"
        })
    # Format y-axis as percentage
    fig4.update_layout(xaxis_title="Time", yaxis_title="Percentage of Tests Completed", yaxis_ticksuffix="%")
    # Add data labels (percentage values)
    fig4.update_traces(text=test_summary['PERCENTAGE_COMPLETED'].round(1),
        textposition="top center")
    # Display Charts
    st.plotly_chart(fig4)

    # FIG 5
    df7_TSreviewM = df.groupby(["DATE_GROUP"], as_index=False)["FOR_TS_REVIEW"].sum()
    #fig
    fig5 = px.line(df7_TSreviewM,
                x="DATE_GROUP", y="FOR_TS_REVIEW", title="For TS Review Monthly"
                ,markers=True,labels={"DATE_GROUP": "Time", "FOR_TS_REVIEW": "For TS Review"}
                ,line_shape="linear",text="FOR_TS_REVIEW")
    fig5.update_traces(textposition="top center")
    # Display Charts
    st.plotly_chart(fig5)

#PAGE 1_______________________________________________________________________________________________
elif st.session_state.page == "Page 1":

    import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
tpci = pd.read_csv("TalkpushCI_data_fetch.csv")
tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'])

# Define colors for graphs
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Sidebar dropdown
st.sidebar.header("Select Time Period")
time_filter = st.sidebar.selectbox("Time Period", ["Last 30 days", "Last 12 Weeks", "Last 1 Year", "All Time"])

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

# Graph 7: Repeat Application Counts
repeat_applications = filtered_data[filtered_data['REPEATAPPLICATION'] == 't'].resample(date_freq, on='INVITATIONDT').count()
fig7 = px.bar(repeat_applications, x=repeat_applications.index, y='REPEATAPPLICATION', title='Repeat Application Counts', labels={'REPEATAPPLICATION': "Counts-'REPEATAPPLICATION'"}, color_discrete_sequence=[colors[7]])
st.plotly_chart(fig7, use_container_width=True)

# Graph 8: Top 5 Campaign Type Occurrences
top_campaign_types = filtered_data['CAMPAIGN_TYPE'].value_counts().nlargest(5)
fig8 = px.bar(top_campaign_types, x=top_campaign_types.index, y=top_campaign_types.values, title='Top 5 Campaign Type Occurrences', labels={'y': 'Counts'}, color_discrete_sequence=[colors[8]])
st.plotly_chart(fig8, use_container_width=True)

# Graph 9: Lead Counts by Campaign Site
top_campaign_sites = filtered_data['CAMPAIGN_SITE'].value_counts().nlargest(5)
fig9 = px.bar(top_campaign_sites, x=top_campaign_sites.index, y=top_campaign_sites.values, title='Lead Counts by Campaign Site', labels={'y': 'Counts'}, color_discrete_sequence=[colors[0]])
st.plotly_chart(fig9, use_container_width=True)
#________________________________________________________________________________________________________________________________________    

elif st.session_state.page == "page 2":
    st.title("page 2")
    # Your content here

elif st.session_state.page == "page 3":
    st.title("page 2")
    # Your content here

elif st.session_state.page == "page 4":
    st.title("page 2")
    # Your content here

# streamlit run TP_analysis_all.py
