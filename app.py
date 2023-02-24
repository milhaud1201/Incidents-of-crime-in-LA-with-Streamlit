import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


# API Endpoint
DATA_URL = (
	"https://data.lacity.org/resource/2nrs-mtv8.csv?$query=SELECT%0A%20%20%60dr_no%60%2C%0A%20%20%60date_rptd%60%2C%0A%20%20%60date_occ%60%2C%0A%20%20%60time_occ%60%2C%0A%20%20%60area%60%2C%0A%20%20%60area_name%60%2C%0A%20%20%60rpt_dist_no%60%2C%0A%20%20%60part_1_2%60%2C%0A%20%20%60crm_cd%60%2C%0A%20%20%60crm_cd_desc%60%2C%0A%20%20%60mocodes%60%2C%0A%20%20%60vict_age%60%2C%0A%20%20%60vict_sex%60%2C%0A%20%20%60vict_descent%60%2C%0A%20%20%60premis_cd%60%2C%0A%20%20%60premis_desc%60%2C%0A%20%20%60weapon_used_cd%60%2C%0A%20%20%60weapon_desc%60%2C%0A%20%20%60status%60%2C%0A%20%20%60status_desc%60%2C%0A%20%20%60crm_cd_1%60%2C%0A%20%20%60crm_cd_2%60%2C%0A%20%20%60crm_cd_3%60%2C%0A%20%20%60crm_cd_4%60%2C%0A%20%20%60location%60%2C%0A%20%20%60cross_street%60%2C%0A%20%20%60lat%60%2C%0A%20%20%60lon%60")

st.title("Incidents of crime in the City of LA")
st.markdown("Streamlit dashboard를 이용한 LA의 범죄 사건 Application 🚗💥")

# row개수에 따라 데이터 보여주기
@st.cache(persist=True)
def load_data(nrows):
	data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=['date_rptd'])
	data = data.dropna(subset=['lat', 'lon'])
	lowercase = lambda x: str(x).lower()
	data = data.rename(lowercase, axis='columns')
	data = data.sort_values(by='date_rptd', ascending=False)
	return data

data = load_data(100000)

st.header("Where is the most place for crime in LA?")
crime = st.slider("Number of crime in LA", 0, 19)
st.map(data.query("area >= @crime")[['lat', 'lon']].dropna(how='any'))

st.header("What is the number of victims by age?")
age_range = st.slider("Victims by age to look at", 0, 100, (0, 100))
data = data[(data['vict_age'] >= age_range[0]) & (data['vict_age'] <= age_range[1])]

st.markdown("희생자의 나이는 %i부터 %i까지입니다" % (age_range[0], age_range[1]))
st.markdown("총 %i명 입니다" % len(data))
midpoint = (np.average(data['lat']), np.average(data['lon']))

st.write(pdk.Deck(
	map_style="mapbox://styles/mapbox/light-v9",
	initial_view_state={
		"latitude": midpoint[0],
		"longitude": midpoint[1],
		"zoom": 11,
		"pitch": 50,
	},
	layers=[
		pdk.Layer(
		"HexagonLayer", 
		data=data[['vict_age', 'lat', 'lon']],
		get_position=['lon', 'lat'],
		radius=100,
		extruded=True,
		pickable=True,
		elevation_scale=4,
		elevation_range=[0, 1000],
		),
	],
))

st.subheader("The number of victims by descent and sex")
chart_data = pd.DataFrame({
	'crime_cd': data['crm_cd'],
	'type': data['crm_cd_desc'],
	'descent': data['vict_descent'],
	'sex': data['vict_sex'],
})
chart_data = chart_data.groupby(by=['descent', 'sex']).size().reset_index(name='counts')
fig = px.bar(chart_data, x='descent', y='counts' , color='sex', barmode='group', height=800)
# fig.update_layout(yaxis={'categoryorder':'total ascending'})
st.write(fig)

st.header("Top 5 type of crimes")
select = st.selectbox('The types of crimes & area', 
	['Vehicle - Stolen', 'Battery - Simple assault', 'Theft of identity', 'Burglary from vehicle', 'Andalism - Felony']
)

if select == 'Vehicle - Stolen':
	st.write(data.query("crm_cd_desc == 'VEHICLE - STOLEN'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'), width=1000)

elif select == 'Battery - Simple assault':
	st.write(data.query("crm_cd_desc == 'BATTERY - SIMPLE ASSAULT'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'), width=1000)

elif select == 'Theft of identity':
	st.write(data.query("crm_cd_desc == 'THEFT OF IDENTITY'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'), width=1000)

elif select == 'Burglary from vehicle':
	st.write(data.query("crm_cd_desc == 'BURGLARY FROM VEHICLE'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'), width=1000)

elif select == 'Andalism - Felony':
	st.write(data.query("crm_cd_desc == 'VANDALISM - FELONY ($400 & OVER, ALL CHURCH VANDALISMS)'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'), width=1000)


if st.checkbox("Show Raw Data", False):
	st.subheader('Raw Data')
	st.write(data)