import streamlit as st
import pandas as pd
import plotly.express as px
from pyproj import Transformer

# Set Streamlit layout (must be first Streamlit command)
st.set_page_config(layout="wide")
st.title("Air Discharge Consents Dashboard")

# Load dataset
csv_path = '/Users/unofficial_storm/Desktop/Cleaned_Data.csv'
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(f"File not found at path: {csv_path}")
    st.stop()

# Clean and preprocess dates
if 'fmDate' in df.columns:
    df['fmDate'] = pd.to_datetime(df['fmDate'], errors='coerce')
    df['StartYear'] = df['fmDate'].dt.year
else:
    st.warning("Missing 'fmDate' column. StartYear-based visualisations may not work.")

# Coordinate transformation: NZTM to WGS84 (lon/lat)
if {'X', 'Y'}.issubset(df.columns):
    transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
    df['Longitude'], df['Latitude'] = transformer.transform(df['X'].values, df['Y'].values)
else:
    st.warning("Missing NZTM coordinate columns 'X' and/or 'Y'. Map visualisations may fail.")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page:", ["Discharge Activity Overview", "Regional & Geographic Overview"])

# Page 1: Discharge Activity Overview
if page == "Discharge Activity Overview":
    st.header("Discharge Activity Overview")

    st.subheader("Top 10 Discharge Activity Types")
    activity_counts = df['FeatureType'].value_counts().nlargest(10).reset_index()
    activity_counts.columns = ['Activity Type', 'Count']
    fig1 = px.bar(activity_counts, x='Activity Type', y='Count', title="Top 10 Activity Types")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Consent Status by Activity Type")
    top_features = df['FeatureType'].value_counts().nlargest(5).index
    filtered_df = df[df['FeatureType'].isin(top_features)]
    status_group = filtered_df.groupby(['FeatureType', 'ConsentStatus']).size().reset_index(name='Count')
    fig2 = px.bar(status_group, x='FeatureType', y='Count', color='ConsentStatus', barmode='group',
                  title="Consent Status Breakdown for Top Activities")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Legal Basis: RMA Section Frequency")
    rma_counts = df['RMASection'].value_counts().reset_index()
    rma_counts.columns = ['RMA Section', 'Count']
    fig3 = px.bar(rma_counts, x='RMA Section', y='Count', title="Frequency by RMA Section")
    st.plotly_chart(fig3, use_container_width=True)

# Page 2: Regional & Geographic Overview
elif page == "Regional & Geographic Overview":
    st.header("Regional & Geographic Overview")

    st.subheader("Consents by Territorial Authority")
    region_counts = df['GIS_TerritorialAuthority'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Count']
    fig4 = px.bar(region_counts, x='Region', y='Count', title="Consents per Region")
    fig4.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Yearly Trend of Issued Consents")
    df_time = df.dropna(subset=['StartYear'])
    fig5 = px.histogram(df_time, x='StartYear', title='Consents Over Time')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Consent Locations Map")
    if df['Latitude'].notnull().any() and df['Longitude'].notnull().any():
        fig6 = px.scatter_mapbox(
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
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("Map data unavailable. Latitude/Longitude conversion may have failed.")
