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

# Section 2: Bar Chart – Top 10 Consents by Activity Type
st.subheader("Top 10 Discharge Activities")
activity_counts = df['FeatureType'].value_counts().nlargest(10).reset_index()
activity_counts.columns = ['Activity Type', 'Count']
fig1 = px.bar(activity_counts, x='Activity Type', y='Count', title="Top 10 Discharge Activities")
st.plotly_chart(fig1, use_container_width=True)

# Section 3: Pie Chart – Consent Type Distribution
st.subheader("Consent Type Proportions")
consent_type_counts = df['ConsentType'].value_counts().reset_index()
consent_type_counts.columns = ['Consent Type', 'Count']
fig2 = px.pie(consent_type_counts, names='Consent Type', values='Count', title='Consent Type Distribution')
st.plotly_chart(fig2, use_container_width=True)

# Section 4: Map Visualisation – Consent Locations
st.subheader("Map of Discharge Locations (NZTM Coordinates Approximate)")
fig3 = px.scatter(
    df,
    x='NZTMX',
    y='NZTMY',
    color='FeatureType',
    hover_name='GIS_TerritorialAuthority',
    title="Mapped Discharge Locations (NZTM Projection)"
)
st.plotly_chart(fig3, use_container_width=True)

# Section 5: Histogram – Consent Start Dates
st.subheader("Distribution of Consent Start Dates")
fig4 = px.histogram(
    df.dropna(subset=['Start Year']),
    x='Start Year',
    title='Consents Issued per Year'
)
st.plotly_chart(fig4, use_container_width=True)


# Section 10: Conclusion
st.subheader("Conclusion")
st.write("This dashboard provides insights into air discharge consents, including summary metrics, visualisations, and options for data download. For any questions or further analysis, please contact us.")
