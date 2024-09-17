# Weather Dashboard

## Description

Weather Dashboard is a Streamlit application designed for quick and easy weather data comparison across multiple cities. It also allows users to view and compare historical weather data from past date ranges (up to 7 days) using data pulled from OpenWeather's API.

## Video Demo

Check out the demo video of the Weather Dashboard: [Video Demo](https://youtu.be/9V0yUfE2lsk)

## Features

- User-friendly interface
- Interactive weather data tables
- Beautiful line and bar charts for visualizing weather comparisons
- View weather data from earlier that day or past date ranges
- Compare up to five US cities

## Installation

To install and run the Weather Dashboard, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/weather-dashboard.git
   cd weather-dashboard
   ```

2. **Install dependencies**:
   Make sure you have Python installed. Then install the required Python packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Obtain an API key**:
   Sign up for an API key from OpenWeather and add it to the api_keys.json file.

4. **Run the application**:
   Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

## Usage

Once the application is running, you can access the Weather Dashboard in your browser by navigating to `http://localhost:8501`. The dashboard can be accessed from both desktop and mobile devices as long as they are on the same network.
