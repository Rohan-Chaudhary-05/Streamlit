import streamlit as st
import pandas as pd
import plotly.express as px
from pyproj import Transformer

# Load the cleaned dataset
df = pd.read_csv('/Users/unofficial_storm/Desktop/Cleaned_Data.csv')

# Convert date column and extract start year
df['fmDate'] = pd.to_datetime(df['fmDate'], errors='coerce')
df['StartYear'] = df['fmDate'].dt.year

# Convert NZTM (X, Y) to latitude and longitude
transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
df['Longitude'], df['Latitude'] = transformer.transform(df['X'].values, df['Y'].values)

# Set up the dashboard layout
st.set_page_config(layout="wide")
st.title("Air Discharge Consents Dashboard")

page = st.sidebar.selectbox(
    "Choose a page:",
    ["Activity & Consent Overview", "Geographic Distribution", "Time-Based Analysis"]
)

# Page 1: Activity & Consent Overview
if page == "Activity & Consent Overview":
    st.header("Activity & Consent Overview")

    # Top 10 activity types
    st.subheader("Top 10 Discharge Activity Types")
    activity_counts = df['FeatureType'].value_counts().nlargest(10).reset_index()
    activity_counts.columns = ['Activity Type', 'Count']
    fig1 = px.bar(activity_counts, x='Activity Type', y='Count', title="Top 10 Activity Types")
    st.plotly_chart(fig1, use_container_width=True)

    # Consent Type Distribution
    st.subheader("Consent Type Distribution")
    consent_type_counts = df['ConsentType'].value_counts().reset_index()
    consent_type_counts.columns = ['Consent Type', 'Count']
    fig2 = px.pie(consent_type_counts, names='Consent Type', values='Count', title='Consent Types')
    st.plotly_chart(fig2, use_container_width=True)

    # Consent Status Breakdown
    st.subheader("Consent Status Breakdown")
    status_counts = df['ConsentStatus'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig3 = px.bar(status_counts, x='Status', y='Count', title="Consent Status Overview")
    st.plotly_chart(fig3, use_container_width=True)

# Page 2: Geographic Distribution
elif page == "Geographic Distribution":
    st.header("Geographic Distribution")

    # Bar chart of consents by territorial authority
    st.subheader("Consent Distribution by Region")
    region_counts = df['GIS_TerritorialAuthority'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Count']
    fig_region = px.bar(
        region_counts.sort_values('Count', ascending=False),
        x='Region', y='Count', color='Count', color_continuous_scale='Viridis',
        title="Consents per Region"
    )
    fig_region.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_region, use_container_width=True)

    # Map of consent locations (if lat/lon exists)
    if 'Latitude' in df.columns and df['Latitude'].notnull().any():
        st.subheader("Consent Locations Map")
        fig_map = px.scatter_mapbox(
            df,
            lat='Latitude',
            lon='Longitude',
            color='FeatureType',
            hover_name='GIS_TerritorialAuthority',
            mapbox_style="carto-positron",
            zoom=5,
            height=600,
            title="Discharge Locations by Activity Type"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Map data unavailable. Latitude/Longitude conversion may have failed.")

    # Optional: Runanga distribution
    st.subheader("Distribution by Runanga")
    runanga_counts = df['GIS_Runanga'].value_counts().nlargest(10).reset_index()
    runanga_counts.columns = ['Runanga', 'Count']
    fig_runanga = px.bar(runanga_counts, x='Runanga', y='Count', title="Top 10 Runanga Regions")
    st.plotly_chart(fig_runanga, use_container_width=True)

# Page 3: Time-Based Analysis
elif page == "Time-Based Analysis":
    st.header("Time-Based Analysis")

    # Histogram of consents per year
    st.subheader("Consents Issued per Year")
    df_time = df.dropna(subset=['StartYear'])
    fig_time = px.histogram(df_time, x='StartYear', title='Consents Over Time')
    st.plotly_chart(fig_time, use_container_width=True)

    # Bar chart of expiring consents
    st.subheader("Expiring Consents by Year")
    df['Expires'] = pd.to_datetime(df['Expires'], errors='coerce')
    df['ExpiryYear'] = df['Expires'].dt.year
    expiry_counts = df['ExpiryYear'].value_counts().sort_index().reset_index()
    expiry_counts.columns = ['Year', 'Count']
    fig_expire = px.bar(expiry_counts, x='Year', y='Count', title='Consents Expiring Each Year')
    st.plotly_chart(fig_expire, use_container_width=True)

    # Optional: Table of soon-expiring consents
    st.subheader("Upcoming Expiries (Next 5 Years)")
    upcoming = df[(df['ExpiryYear'] >= pd.Timestamp.now().year) & 
                  (df['ExpiryYear'] <= pd.Timestamp.now().year + 5)]
    st.dataframe(upcoming[['ConsentNo', 'FeatureType', 'GIS_TerritorialAuthority', 'Expires']].sort_values('Expires'))
