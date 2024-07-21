import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(layout="wide", page_title="CO2 Emissions Dashboard", page_icon="🌍")

# Cache the data to improve dashboard performance
@st.cache_data
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv')
    return df

df = load_data()

# Fill NAs with 0s and create GDP per capita column
df = df.fillna(0)
df['gdp_per_capita'] = np.where(df['population'] != 0, df['gdp'] / df['population'], 0)

# Sidebar widgets
st.sidebar.header("Settings")
st.sidebar.markdown("""
# CO2 Emissions and Climate Change

#### Carbon dioxide emissions are the primary driver of global climate change. It’s widely recognized that to avoid the worst impacts of climate change, the world needs to urgently reduce emissions. But, how this responsibility is shared between regions, countries, and individuals has been an endless point of contention in international discussions.
""")

year_slider = st.sidebar.slider('Year', 1750, 2020, 1850, step=5)
yaxis_co2 = st.sidebar.radio('Y-axis', ['co2', 'co2_per_capita'], index=0)
yaxis_co2_source = st.sidebar.radio('CO2 Source Y-axis', ['coal_co2', 'oil_co2', 'gas_co2'], index=0)

# List of continents
continents = ['World', 'Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']
continents_excl_world = ['Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']

# Filter data for CO2 emissions
co2_pipeline = (
    df[(df.year <= year_slider) & (df.country.isin(continents))]
    .groupby(['country', 'year'])[yaxis_co2].mean().reset_index()
)

# CO2 emissions plot
co2_plot = alt.Chart(co2_pipeline).mark_line().encode(
    x='year:Q',
    y=alt.Y(f'{yaxis_co2}:Q', title=yaxis_co2.replace('_', ' ').title()),
    color='country:N'
).properties(
    title='CO2 Emission by Continent',
    height=500,
    width=1000
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    titleFontSize=14,
    labelFontSize=12
).configure_title(
    fontSize=20,
    anchor='start'
)

# Filter data for CO2 vs GDP scatter plot
co2_vs_gdp_pipeline = (
    df[(df.year == year_slider) & (~df.country.isin(continents))]
    .groupby(['country', 'year', 'gdp_per_capita'])['co2'].mean().reset_index()
)

# CO2 vs GDP scatter plot
co2_vs_gdp_scatterplot = alt.Chart(co2_vs_gdp_pipeline).mark_circle(size=80).encode(
    x=alt.X('gdp_per_capita:Q', title='GDP per Capita'),
    y=alt.Y('co2:Q', title='CO2 Emissions'),
    color='country:N',
    tooltip=['country', 'gdp_per_capita', 'co2']
).properties(
    title='CO2 vs GDP per Capita',
    height=500,
    width=450
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    titleFontSize=14,
    labelFontSize=12
).configure_title(
    fontSize=20,
    anchor='start'
)

# Filter data for CO2 source bar plot
co2_source_bar_pipeline = (
    df[(df.year == year_slider) & (df.country.isin(continents_excl_world))]
    .groupby(['year', 'country'])[yaxis_co2_source].sum().reset_index()
)

# CO2 source bar plot
co2_source_bar_plot = alt.Chart(co2_source_bar_pipeline).mark_bar().encode(
    x='country:N',
    y=alt.Y(f'{yaxis_co2_source}:Q', title=yaxis_co2_source.replace('_', ' ').title()),
    color='country:N'
).properties(
    title='CO2 Source by Continent',
    height=500,
    width=450
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    titleFontSize=14,
    labelFontSize=12
).configure_title(
    fontSize=20,
    anchor='start'
)

# Layout
st.title("🌍 CO2 Emissions Dashboard")
st.markdown("""
### Explore CO2 emissions and their sources globally and by continent. Adjust the settings in the sidebar to filter the data by year and CO2 emission types.
""")

st.altair_chart(co2_plot, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.altair_chart(co2_vs_gdp_scatterplot, use_container_width=True)

with col2:
    st.altair_chart(co2_source_bar_plot, use_container_width=True)
