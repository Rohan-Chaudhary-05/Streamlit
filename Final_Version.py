import streamlit as st
import pandas as pd
import plotly.express as px
from pyproj import Transformer

# --- CONFIG ---
st.set_page_config(layout="wide")
st.title("🇳🇿 Air Discharge Consents Dashboard (New Zealand)")

# --- LOAD DATA ---
csv_path = "Cleaned_Data.csv"  
df = pd.read_csv(csv_path)

# --- CLEAN COLUMN NAMES ---
df.columns = df.columns.str.strip()

# --- TRANSFORM COORDINATES ---
if {'X', 'Y'}.issubset(df.columns):
    transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
    coords = df[['X', 'Y']].dropna().values
    transformed = [transformer.transform(x, y) for x, y in coords]

    df['Longitude'] = None
    df['Latitude'] = None
    df.loc[df[['X', 'Y']].dropna().index, ['Longitude', 'Latitude']] = transformed
else:
    df['Longitude'], df['Latitude'] = None, None

# --- PARSE DATES ---
if 'fmDate' in df.columns:
    df['fmDate'] = pd.to_datetime(df['fmDate'], errors='coerce')
    df['StartYear'] = df['fmDate'].dt.year
else:
    df['StartYear'] = None

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔎 Filters")

status_options = ["All"] + sorted(df['ConsentStatus'].dropna().unique().tolist())
selected_status = st.sidebar.selectbox("Consent Status", status_options)

min_year, max_year = int(df['StartYear'].min()), int(df['StartYear'].max())
year_range = st.sidebar.slider("Consent Start Year Range", min_year, max_year, (min_year, max_year))

# --- FILTER DATA ---
filtered_df = df.copy()
if selected_status != "All":
    filtered_df = filtered_df[filtered_df['ConsentStatus'] == selected_status]

filtered_df = filtered_df[
    (filtered_df['StartYear'] >= year_range[0]) &
    (filtered_df['StartYear'] <= year_range[1])
]

# --- SUMMARY METRICS ---
st.subheader("📊 Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Consents", len(filtered_df))
col2.metric("Active Consents", df[df['ConsentStatus'] == 'Issued - Active'].shape[0])
col3.metric("Regions Covered", df['GIS_TerritorialAuthority'].nunique())

# --- ACTIVITY TYPE CHART ---
st.subheader("⚙️ Top Discharge Activities")
top_n = st.slider("Top N Activity Types", 5, 20, 10)
activity_counts = filtered_df['FeatureType'].value_counts().nlargest(top_n).reset_index()
activity_counts.columns = ['Activity Type', 'Count']
fig1 = px.bar(activity_counts, x='Count', y='Activity Type', orientation='h', title=f"Top {top_n} Discharge Activities")
st.plotly_chart(fig1, use_container_width=True)

# --- REGIONAL DISTRIBUTION ---
st.subheader("🌐 Regional Distribution")
region_counts = filtered_df['GIS_TerritorialAuthority'].value_counts().nlargest(10).reset_index()
region_counts.columns = ['Region', 'Count']
fig2 = px.bar(region_counts, x='Region', y='Count', title="Top 10 Regions by Consent Volume")
fig2.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig2, use_container_width=True)

# --- TREND OVER TIME ---
st.subheader("📈 Consents Issued Over Time")
trend_df = filtered_df.dropna(subset=['StartYear'])
fig3 = px.histogram(trend_df, x='StartYear', title='Consent Frequency by Year')
st.plotly_chart(fig3, use_container_width=True)

# --- MAP VISUALISATION ---
st.subheader("🗺️ Consent Locations Map")
filtered_map_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

if not filtered_map_df.empty:
    fig_map = px.scatter_mapbox(
        filtered_map_df,
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
    st.info("No map data to display for the selected filters.")
