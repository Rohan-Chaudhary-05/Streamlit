import streamlit as st
import pandas as pd
import plotly.express as px
from pyproj import Transformer
from datetime import datetime

# Set layout and title
st.set_page_config(layout="wide")
st.title("Air Discharge Consents Dashboard")

# Load cleaned dataset
csv_path = '/Users/unofficial_storm/Desktop/Cleaned_Data.csv'
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(f"File not found at path: {csv_path}")
    st.stop()

# Preprocess dates
df['fmDate'] = pd.to_datetime(df['fmDate'], errors='coerce')
df['StartYear'] = df['fmDate'].dt.year
df['toDate'] = pd.to_datetime(df['toDate'], errors='coerce')

# Transform coordinates
if {'X', 'Y'}.issubset(df.columns):
    transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
    df['Longitude'], df['Latitude'] = transformer.transform(df['X'].values, df['Y'].values)

# Sidebar page selector
page = st.sidebar.selectbox("Choose a page:", ["Discharge Activity Overview", "Regional & Geographic Overview"])

# ========== PAGE 1 ==========
if page == "Discharge Activity Overview":
    st.header("Discharge Activity Overview")

    # Interactive Filter: FeatureType
    feature_filter = st.multiselect("Select Discharge Activity Type(s):", df['FeatureType'].unique(), default=df['FeatureType'].unique())
    filtered_df = df[df['FeatureType'].isin(feature_filter)]

    # Chart 1: Top Activity Types
    st.subheader("Top 10 Selected Activity Types")
    top_activity_counts = filtered_df['FeatureType'].value_counts().nlargest(10).reset_index()
    top_activity_counts.columns = ['Activity Type', 'Count']
    fig1 = px.bar(top_activity_counts, x='Activity Type', y='Count', title="Top Activity Types")
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Consent Status by Activity
    st.subheader("Consent Status Breakdown")
    top5 = filtered_df['FeatureType'].value_counts().nlargest(5).index
    status_data = filtered_df[filtered_df['FeatureType'].isin(top5)]
    grouped = status_data.groupby(['FeatureType', 'ConsentStatus']).size().reset_index(name='Count')
    fig2 = px.bar(grouped, x='FeatureType', y='Count', color='ConsentStatus', barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: RMA Section Frequencies
    st.subheader("RMA Legal Sections")
    rma_counts = filtered_df['RMASection'].value_counts().reset_index()
    rma_counts.columns = ['RMA Section', 'Count']
    fig3 = px.bar(rma_counts, x='RMA Section', y='Count', title="Legal Basis Frequency")
    st.plotly_chart(fig3, use_container_width=True)

    # Custom Visualisation Tool
    st.subheader("Custom Categorical Breakdown")
    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    x_col = st.selectbox("Select X-axis category:", categorical_cols)
    fig_custom = px.histogram(filtered_df, x=x_col, title=f"Distribution by {x_col}")
    st.plotly_chart(fig_custom, use_container_width=True)

# ========== PAGE 2 ==========
elif page == "Regional & Geographic Overview":
    st.header("Regional & Geographic Overview")

    # Filter: Year Range
    st.sidebar.markdown("### Filter by Consent Start Year")
    min_year, max_year = int(df['StartYear'].min()), int(df['StartYear'].max())
    year_range = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))
    df_time = df[(df['StartYear'] >= year_range[0]) & (df['StartYear'] <= year_range[1])]

    # Filter: Region
    selected_regions = st.sidebar.multiselect("Select Region(s)", df['GIS_TerritorialAuthority'].unique(), default=df['GIS_TerritorialAuthority'].unique())
    df_time = df_time[df_time['GIS_TerritorialAuthority'].isin(selected_regions)]

    # Filter: Expiring Soon
    if st.sidebar.checkbox("Show only consents expiring in the next 5 years"):
        current_year = datetime.now().year
        df_time = df_time[(df_time['toDate'].dt.year >= current_year) & (df_time['toDate'].dt.year <= current_year + 5)]

    # Chart 1: Consents by Region
    st.subheader("Consents by Territorial Authority")
    region_counts = df_time['GIS_TerritorialAuthority'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Count']
    fig4 = px.bar(region_counts, x='Region', y='Count', title="Consents per Region")
    fig4.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig4, use_container_width=True)

    # Chart 2: Trend Over Time
    st.subheader("Consent Issuance Over Time")
    fig5 = px.histogram(df_time, x='StartYear', title='Yearly Consent Trend')
    st.plotly_chart(fig5, use_container_width=True)

    # Map Filter: FeatureType selection
    st.subheader("Consent Locations Map")
    selected_features = st.multiselect("Select Feature Types for Map", df['FeatureType'].unique(), default=df['FeatureType'].unique())
    df_map = df_time[df_time['FeatureType'].isin(selected_features)]

    if df_map['Latitude'].notnull().any() and df_map['Longitude'].notnull().any():
        fig6 = px.scatter_mapbox(
            df_map,
            lat='Latitude',
            lon='Longitude',
            color='FeatureType',
            hover_name='GIS_TerritorialAuthority',
            mapbox_style="carto-positron",
            zoom=5,
            height=600,
            title="Discharge Locations by Activity"
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("Map data unavailable. Latitude/Longitude conversion may have failed.")
