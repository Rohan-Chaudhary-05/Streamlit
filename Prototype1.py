import streamlit as st
import pandas as pd
import plotly.express as px

# Load cleaned dataset 
df = pd.read_csv('/Users/unofficial_storm/Desktop/Cleaned_Data.csv')

# Convert fmDate to datetime and extract year for time analysis
df['fmDate'] = pd.to_datetime(df['fmDate'], errors='coerce')
df['Start Year'] = df['fmDate'].dt.year

st.set_page_config(layout="wide")
st.title("Air Discharge Consents Dashboard")

# Section 1: Summary
st.subheader("Summary Metrics")
st.metric("Total Consents", df.shape[0])
st.metric("Unique Activity Types", df['FeatureType'].nunique())
st.metric("Regions", df['GIS_TerritorialAuthority'].nunique())

# Section 2: Bar Chart – Consents by Activity Type
st.subheader("Consent Count by Activity Type")
activity_counts = df['FeatureType'].value_counts().reset_index()
activity_counts.columns = ['Activity Type', 'Count']
fig1 = px.bar(activity_counts, x='Activity Type', y='Count', title="Discharges by Activity Type")
st.plotly_chart(fig1, use_container_width=True)

# Section 3: Pie Chart – Consent Type Distribution
st.subheader("Consent Type Proportions")
consent_type_counts = df['ConsentType'].value_counts().reset_index()
consent_type_counts.columns = ['Consent Type', 'Count']
fig2 = px.pie(consent_type_counts, names='Consent Type', values='Count', title='Consent Type Distribution')
st.plotly_chart(fig2, use_container_width=True)

# Section 4: Map Visualisation – Consent Locations
st.subheader("Map of Discharge Locations (NZTM Coordinates Approximate)")
fig3 = px.scatter_geo(
    df,
    lon='NZTMX',
    lat='NZTMY',
    hover_name='GIS_TerritorialAuthority',
    color='FeatureType',
    title="Geographic Spread of Air Discharge Consents"
)
fig3.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig3, use_container_width=True)

# Section 5: Histogram – Consent Start Dates
st.subheader("Distribution of Consent Start Dates")
fig4 = px.histogram(
    df.dropna(subset=['Start Year']),
    x='Start Year',
    title='Consents Issued per Year'
)
st.plotly_chart(fig4, use_container_width=True)

# Section 6: Show raw data
st.subheader("Raw Data Preview")
st.dataframe(df.head())
st.download_button(
    label="Download Raw Data",
    data=df.to_csv(index=False),
    file_name='Cleaned_Data.csv',
    mime='text/csv'
)

# Section 7: Filtered Data
st.subheader("Filtered Data")
activity_type = st.selectbox("Select Activity Type", df['FeatureType'].unique())
filtered_data = df[df['FeatureType'] == activity_type]
st.dataframe(filtered_data)
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name=f'Filtered_Data_{activity_type}.csv',
    mime='text/csv'
)

# Section 8: User Input for Custom Analysis
st.subheader("Custom Analysis")
custom_activity = st.selectbox("Select Custom Activity Type", df['FeatureType'].unique(), key="custom_select")
custom_filtered_data = df[df['FeatureType'] == custom_activity]
st.dataframe(custom_filtered_data)
st.download_button(
    label="Download Custom Filtered Data",
    data=custom_filtered_data.to_csv(index=False),
    file_name=f'Custom_Filtered_Data_{custom_activity}.csv',
    mime='text/csv'
)

# Section 9: Feedback
st.subheader("Feedback")
feedback = st.text_area("Please provide your feedback or suggestions:")
if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
    # Optionally save feedback

# Section 10: Conclusion
st.subheader("Conclusion")
st.write("This dashboard provides insights into air discharge consents, including summary metrics, visualisations, and options for data download. For any questions or further analysis, please contact us.")

# Section 11: Contact Information
st.subheader("Contact Information")
st.write("For any inquiries or support, please reach out to us at:")
st.write("Email: support@example.com")  
