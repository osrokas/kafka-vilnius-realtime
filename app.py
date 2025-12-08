import streamlit as st
import pydeck
from dotenv import load_dotenv
import os
import geopandas as gpd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine

if os.path.exists(".env"):
    load_dotenv(".env", override=True)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
TABLE_NAME = os.getenv("TABLE_NAME", "gps_data")

BASE_LAT, BASE_LON = 54.6872, 25.2797  # Vilnius city center


# Page settings
st.set_page_config(layout="wide")
st.title("🗺️ Live Updating Map")

# Auto-refresh every 10 seconds
count = st_autorefresh(interval=1000, key="refresh")

# Show timestamp
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


@st.cache_resource
def get_engine():
    return create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


engine = get_engine()


# Load data
@st.cache_data
def load_data(trigger):
    with engine.connect() as conn:
        df = gpd.read_postgis(
            f"SELECT vehicle_id, timestamp, geometry FROM gps_data", conn, geom_col="geometry", crs="EPSG:4326"
        )
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        gdf["x"] = gdf.geometry.x
        gdf["y"] = gdf.geometry.y
    return gdf


st.title("Database Viewer and Updater")


df = load_data(count)


layer = pydeck.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[x, y]",
    get_color="[255, 0, 0]",
    get_radius=10,
)

# Map view state
view_state = pydeck.ViewState(
    latitude=BASE_LAT,  # vilnius coordinates
    longitude=BASE_LON,  # vilnius coordinates
    zoom=12,
    pitch=0,
)

# Render map
r = pydeck.Deck(
    initial_view_state=view_state,
    layers=[layer],
)

st.pydeck_chart(r)
