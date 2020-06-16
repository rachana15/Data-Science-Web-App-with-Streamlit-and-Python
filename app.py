import streamlit as st
import pandas as pd 
import numpy as np 
import pydeck as pdk 
import plotly.express as px
import datetime

DATA_URL = (
    "/Users/rachanabhaskar/Desktop/Streamlit/Motor_Vehicle_Collisions_-_Crashes.csv.crdownload"
)

st.title("Motor Vehicle Collisions in New York")
st.markdown(" This is a Streamlit Dashboard used to analyze Motor Vehicle Collisions in NYC 🗽💥 ")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH DATE','CRASH TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash date_crash time': 'date/time'}, inplace=True)
    data.columns =[column.replace(" ", "_") for column in data.columns]
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most numebr of persons injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query('number_of_persons_injured >= @injured_people')[['latitude','longitude']].dropna(how = "any"))


st.header("How many collisions occur during a given time of day?")
# hour = st.selectbox("Hour to look at", range(1,24), 1)
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour ]
st.markdown("Collisions between %i:00 and %i:00" % (hour  , (hour+1) % 24) )

#initialize the map with correct points 
midpoint = (np.average(data['latitude']), np.average(data['longitude'])) 
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[["date/time","latitude","longitude"]],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range= [0,1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1)% 24))
filtered = data [
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height=400)
st.write(fig)


st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected Type", ['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("number_of_pedestrians_injured >= 1 ")[["on_street_name","number_of_pedestrians_injured"]].sort_values(by = ['number_of_pedestrians_injured'], ascending = False).dropna(how = 'any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("number_of_cyclist_injured >= 1 ")[["on_street_name","number_of_cyclist_injured"]].sort_values(by = ['number_of_cyclist_injured'], ascending = False).dropna(how = 'any')[:5])

else:
    st.write(original_data.query("number_of_motorist_injured >= 1 ")[["on_street_name","number_of_motorist_injured"]].sort_values(by = ['number_of_motorist_injured'], ascending = False).dropna(how = 'any')[:5])


st.header("Number of persons killed in the year?")
year_range = (np.min(original_data['date/time'].dt.year), np.max(original_data['date/time'].dt.year))
# st.write(year_range[0])
year_slider = st.slider("Year to look at", int(year_range[0]), int(year_range[1]))
kill_data = original_data[['number_of_persons_killed','date/time']].sort_values(by = ['date/time']).dropna(how = 'any')
kill_data['year'] = pd.DatetimeIndex(kill_data['date/time']).year



if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)