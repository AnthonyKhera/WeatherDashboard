import streamlit as st
import requests
from datetime import datetime, timedelta, date, time
import altair as alt
import pandas as pd
import numpy as np
import json
from city_data import city_data
from unit_dictionary import unit_dictionary


def floor_to_nearest_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def format_column_with_unit(value, column, selected_unit):
    unit_symbol = unit_dictionary[selected_unit][column]
    return f"{value} {unit_symbol}"


def map_current_api_call(city_name: str, raw_data: dict, city_json: dict, past_present: bool, selected_unit: str):
    raw_data["Cities"].append(city_name)

    if not past_present:
        raw_data["Temperature"].append(city_json["current"]["temp"])
        raw_data["Feels Like"].append(city_json["current"]["feels_like"])
        raw_data["UV Index"].append(city_json["current"]["uvi"])
        raw_data["Humidity"].append(city_json["current"]["humidity"])
        raw_data["Cloudiness"].append(city_json["current"]["clouds"])
        raw_data["Wind Speed"].append(city_json["current"]["wind_speed"])
        raw_data["Air Pressure"].append(round(city_json["current"]["pressure"] * 0.029529983071, 2))
        raw_data["Description"].append(city_json["current"]["weather"][0]["description"])
        raw_data["Icon"].append(city_json["current"]["weather"][0]["icon"])

    else:
        raw_data["Temperature"].append(city_json["data"][0]["temp"])
        raw_data["Feels Like"].append(city_json["data"][0]["feels_like"])
        raw_data["UV Index"].append(city_json["data"][0]["uvi"])
        raw_data["Humidity"].append(city_json["data"][0]["humidity"])
        raw_data["Cloudiness"].append(city_json["data"][0]["clouds"])
        raw_data["Wind Speed"].append(city_json["data"][0]["wind_speed"])
        raw_data["Air Pressure"].append(round(city_json["data"][0]["pressure"] * 0.029529983071, 2))
        raw_data["Description"].append(city_json["data"][0]["weather"][0]["description"])
        raw_data["Icon"].append(city_json["data"][0]["weather"][0]["icon"])


def get_weather(city_name, units="Imperial", include_forecast=False, get_earlier_hour=False, hour_time=0):
    city_info = city_data.get(city_name)
    units = units.lower()
    exclude_daily = "daily,"
    hour_time = hour_time

    if include_forecast:
        exclude_daily = ""

    if city_info:
        lat, lon = city_info["latitude"], city_info["longitude"]
        file = open("api_keys.json")
        json_file = json.load(file)
        api_key = json_file["api_key"]
        if get_earlier_hour:
            url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={hour_time}&units={units}&appid={api_key}"
        else:
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,{exclude_daily}alerts&units={units}&appid={api_key}"
        response = requests.get(url).json()
        return response
    else:
        st.write("City data not available.")


def get_historical_weather(city_name, chosen_date, units="Imperial"):
    city_info = city_data.get(city_name)
    units = units.lower()
    date = chosen_date

    if city_info:
        lat, lon = city_info["latitude"], city_info["longitude"]
        file = open("api_keys.json")
        json_file = json.load(file)
        api_key = json_file["api_key"]
        url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&units={units}&appid={api_key}"
        response = requests.get(url).json()
        return response
    else:
        st.write("City data not available.")


def get_bar_chart(df, y_axis):
    max_value = df[y_axis].max()

    chart = alt.Chart(df).mark_bar().encode(
        x='Cities:O',
        y=f"{y_axis}:Q",
        # The highlight will be set on the result of a conditional statement
        color=alt.condition(
            alt.datum[y_axis] == max_value,
            alt.value('orange'),
            alt.value('steelblue')
        )
    )

    return chart


def get_temp_line_chart(data, title):
    data_long = data.melt(id_vars=["Dates"], var_name="Temperature", value_name="Temp")

    hover = alt.selection_single(
        fields=["Dates"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data_long, title=title)
        .mark_line()
        .encode(
            x="Dates:T",
            y="Temp:Q",
            color="Temperature:N"
        )
    )

    points = lines.transform_filter(hover).mark_circle(size=65)

    tooltips = (
        alt.Chart(data_long)
        .mark_rule()
        .encode(
            x="Dates:T",
            y="Temp:Q",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Dates:T", title="Date"),
                alt.Tooltip("Temp:Q", title="Temperature"),
                alt.Tooltip("Temperature:N", title="Temperature Type"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()


def get_line_chart(data, title, y_axis: str):
    hover = alt.selection_single(
        fields=["Dates"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title=title)
        .mark_line()
        .encode(
            x="Dates:T",
            y=y_axis + ":Q",
        )
    )

    points = lines.transform_filter(hover).mark_circle(size=65)

    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="Dates:T",
            y=y_axis + ":Q",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Dates:T", title="Date"),
                alt.Tooltip(y_axis + ":Q", title=y_axis),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()


def main():
    city_names = list(city_data.keys())
    submit_disabled = True

    st.title("Weather Dashboard :mostly_sunny:")
    st.subheader("_View Weather Data from the Past and Present_")
    st.divider()
    st.subheader("Customize Your Dashboard")

    multi_location_filter = "Current Weather Data and Forecasts (Multiple Locations)"
    day_filter = "Historical Weather Data (Single Location)"

    selected_data_filter = st.selectbox("Select data:", [multi_location_filter, day_filter],
                                        help="Due to API plan limitations, we cannot retrieve historical weather data "
                                             "for multiple"
                                             "locations and multiple days at the same time.")

    selected_unit = st.radio("Units", ["Imperial (Fahrenheit, Mph)",
                                       "Metric (Celsius, Meters/sec)",
                                       "Standard (Kelvin, Meters/sec)"], horizontal=True)

    st.info('Measurements for Air Pressure and Precipitation are only available in inches and millimeters respectively.')

    if selected_unit == "Imperial (Fahrenheit, Mph)":
        selected_unit = "imperial"
    elif selected_unit == "Metric (Celsius, Meters/sec)":
        selected_unit = "metric"
    elif selected_unit == "Standard (Kelvin, Meters/sec)":
        selected_unit = "standard"

    st.divider()

    if selected_data_filter is day_filter:
        st.subheader("Historical Weather")
        selected_cities = st.selectbox("Select a city:", city_names)

        yesterday = datetime.today() - timedelta(days=2)
        default_start = yesterday - timedelta(days=6)

        dates_chosen = st.date_input("Select Date Range (Max. 7 Days):",
                                     min_value=datetime(1990, 1, 1), max_value=yesterday,
                                     value=(default_start, yesterday), format="MM/DD/YYYY",
                                     help="Historical weather data may take multiple days to become available.")

        if len(dates_chosen) != 2:
            st.stop()

        start_date, end_date = dates_chosen
        max_allowed_end = start_date + timedelta(days=6)

        if end_date > max_allowed_end:
            st.error("Error: Date range must be 7 days or less.")
        else:
            submit_disabled = False

        submit_button = st.button("Submit", disabled=submit_disabled)

        if submit_button:

            raw_data = {
                "Dates": [],
                "High Temp": [],
                "Low Temp": [],
                "Humidity": [],
                "Precipitation": [],
                "Max Wind Speed": [],
                "Air Pressure": []
            }

            current_date = start_date
            loop_counter = 0

            with st.spinner("Loading data..."):
                while current_date <= end_date and loop_counter < 7:
                    weather_data = get_historical_weather(city_name=selected_cities, chosen_date=current_date,
                                                          units=selected_unit)
                    saved_date = datetime.strptime(weather_data["date"], "%Y-%m-%d")

                    raw_data["Dates"].append(saved_date.strftime("%m/%d/%Y"))
                    raw_data["High Temp"].append(weather_data["temperature"]["max"])
                    raw_data["Low Temp"].append(weather_data["temperature"]["min"])
                    raw_data["Humidity"].append(weather_data["humidity"]["afternoon"])
                    raw_data["Precipitation"].append(weather_data["precipitation"]["total"])
                    raw_data["Max Wind Speed"].append(weather_data["wind"]["max"]["speed"])
                    raw_data["Air Pressure"].append(round(weather_data["pressure"]["afternoon"] * 0.029529983071, 2))

                    current_date += timedelta(days=1)
                    loop_counter += 1

            columns_with_units = ["High Temp", "Low Temp", "Max Wind Speed", "Air Pressure", "Humidity",
                                  "Precipitation"]

            df = pd.DataFrame(raw_data)
            for column in columns_with_units:
                df[column] = df[column].apply(lambda x: format_column_with_unit(x, column, selected_unit))

            temp_fields = ["Dates", "High Temp", "Low Temp"]
            temp_data = pd.DataFrame({field: raw_data[field] for field in temp_fields})

            humidity_fields = ["Dates", "Humidity"]
            humidity_data = pd.DataFrame({field: raw_data[field] for field in humidity_fields})

            precip_fields = ["Dates", "Precipitation"]
            precip_data = pd.DataFrame({field: raw_data[field] for field in precip_fields})

            wind_fields = ["Dates", "Max Wind Speed"]
            wind_data = pd.DataFrame({field: raw_data[field] for field in wind_fields})

            pressure_fields = ["Dates", "Air Pressure"]
            pressure_data = pd.DataFrame({field: raw_data[field] for field in pressure_fields})

            st.divider()
            start_date = start_date.strftime("%m/%d/%Y")
            end_date = end_date.strftime("%m/%d/%Y")

            st.subheader("Weather Data")

            st.dataframe(df,
                         hide_index=True,
                         use_container_width=True)

            if loop_counter > 1:
                data_tabs = ["Temperatures", "Humidity", "Precipitation", "Max Wind Speed", "Air Pressure"]
                tab1, tab2, tab3, tab4, tab5 = st.tabs(data_tabs)

                with tab1:
                    temp_chart = get_temp_line_chart(temp_data, title="Change in High and Low Temperatures")
                    st.altair_chart(temp_chart, use_container_width=True)

                with tab2:
                    humidity_chart = get_line_chart(humidity_data, title="Change in Humidity", y_axis="Humidity")
                    st.altair_chart(humidity_chart, use_container_width=True)

                with tab3:
                    precip_chart = get_line_chart(precip_data, title="Change in Precipitation", y_axis="Precipitation")
                    st.altair_chart(precip_chart, use_container_width=True)

                with tab4:
                    wind_chart = get_line_chart(wind_data, title="Change in Max Wind Speed", y_axis="Max Wind Speed")
                    st.altair_chart(wind_chart, use_container_width=True)

                with tab5:
                    pressure_chart = get_line_chart(pressure_data, title="Change in Air Pressure",
                                                    y_axis="Air Pressure")
                    st.altair_chart(pressure_chart, use_container_width=True)
                st.success(f"Displaying weather data for:\n\n{selected_cities} ({start_date} - {end_date})")

            else:
                st.success(f"Displaying weather data for:\n\n{selected_cities} ({start_date} - {end_date})")
                st.warning("Warning: Select multiple days to view comparison charts.")

    else:
        st.subheader("Today's Weather")
        current_date = datetime.now().date()
        start_of_day = datetime.combine(current_date, datetime.min.time())
        unix_timestamp = start_of_day.timestamp()

        max_hour = floor_to_nearest_hour(datetime.now()) - timedelta(hours=1)
        min_hour = datetime.combine(date.today(), time.min)

        selected_cities = st.multiselect("Select Cities (Max. 5 Cities):", city_names, max_selections=5,
                                         placeholder="None selected.")

        selected_city_data = [{"latitude": city_data[city]["latitude"], "longitude": city_data[city]["longitude"]} for
                              city in selected_cities]

        df1 = pd.DataFrame(selected_city_data)
        st.map(df1, latitude="latitude", longitude="longitude", size=7500, color=(245, 39, 145, 0.7))

        col1, col2 = st.columns(2)

        if datetime.now().hour - 1 > 0:
            disable_checkbox = False
        else:
            disable_checkbox = True
            st.warning("It is currently too early in the day to display an earlier hour")

        view_earlier_hour = col1.checkbox("View earlier hour", disabled=disable_checkbox)

        if view_earlier_hour:
            selected_hour = col2.slider("Select an earlier hour from today:",
                                        min_value=min_hour,
                                        max_value=max_hour, value=max_hour, step=timedelta(hours=1), format="hh:mm A")

            unix_timestamp = selected_hour.timestamp()

        if selected_cities:
            submit_disabled = False

        submit_button = col1.button("Submit", disabled=submit_disabled)

        if submit_button:

            raw_data = {
                "Cities": [],
                "Temperature": [],
                "Feels Like": [],
                "UV Index": [],
                "Humidity": [],
                "Cloudiness": [],
                "Wind Speed": [],
                "Air Pressure": [],
                "Description": [],
                "Icon": []
            }

            columns_with_units = ["Temperature", "Feels Like", "Wind Speed", "Air Pressure", "Cloudiness", "Humidity"]

            with st.spinner("Loading data..."):

                cities_str = " | ".join(selected_cities)
                st.divider()

                st.subheader("Weather Data")

                for city in selected_cities:
                    city_json = get_weather(city, selected_unit, get_earlier_hour=view_earlier_hour,
                                            hour_time=int(unix_timestamp))

                    map_current_api_call(city, raw_data, city_json, view_earlier_hour, selected_unit)

                df = pd.DataFrame(raw_data)
                for column in columns_with_units:
                    df[column] = df[column].apply(lambda x: format_column_with_unit(x, column, selected_unit))

                st.dataframe(df, column_config={"Description": None,"Icon": None}, use_container_width=True,
                             hide_index=True)

                data_tabs = ["Temperature", "Feels Like", "Humidity", "UV Index",
                             "Cloudiness", "Wind Speed", "Air Pressure"]

                tab_fields_map = {
                    "Temperature": ["Cities", "Temperature"],
                    "Feels Like": ["Cities", "Feels Like"],
                    "Humidity": ["Cities", "Humidity"],
                    "UV Index": ["Cities", "UV Index"],
                    "Cloudiness": ["Cities", "Cloudiness"],
                    "Wind Speed": ["Cities", "Wind Speed"],
                    "Air Pressure": ["Cities", "Air Pressure"],
                }

                if len(selected_cities) < 2:
                    st.success(f"Displaying weather data for the following cities:\n\n{cities_str}")
                    st.warning("Warning: Select multiple cities to view comparison charts.")

                else:
                    tabs = st.tabs(data_tabs)

                    # Loop through each tab and create the corresponding DataFrame and chart
                    for i, tab in enumerate(data_tabs):
                        fields = tab_fields_map[tab]
                        data = pd.DataFrame({field: raw_data[field] for field in fields})

                        # Set the active tab to display the corresponding chart
                        with tabs[i]:
                            st.subheader(tab)
                            st.caption("Orange bar represents the max value in the data set.")
                            chart = get_bar_chart(data, tab)
                            st.altair_chart(chart, use_container_width=True)

                    st.success(f"Displaying weather data for the following cities:\n\n{cities_str}")


if __name__ == "__main__":
    main()
