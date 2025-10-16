"""
Fetches data from APIs
Currently (and probably permanently) only uses OpenMeteo API
"""

from datetime import date
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse, VariablesWithTime

from utils import *

DATA_DIR = "data/"

# Used in construction of the API call
propertiesMap: dict[str, list[str]] = {
    "temp": [
        "temperature_1000hPa",  # 110 m
        "temperature_975hPa",  # 320 m
        "temperature_950hPa",  # 500 m
        "temperature_925hPa",  # 800 m
        "temperature_900hPa",  # 1000 m
        "temperature_850hPa",  # 1500 m
        "temperature_800hPa",  # 1900 m
        "temperature_700hPa",  # 3000 m
        "temperature_600hPa",  # 4200 m
        "temperature_500hPa",  # 5600 m
        "temperature_400hPa",  # 7200 m
        "temperature_300hPa",  # 9600 m
    ],
    "humidity": [
        "relative_humidity_1000hPa",  # 110 m
        "relative_humidity_975hPa",  # 320 m
        "relative_humidity_950hPa",  # 500 m
        "relative_humidity_925hPa",  # 800 m
        "relative_humidity_900hPa",  # 1000 m
        "relative_humidity_850hPa",  # 1500 m
        "relative_humidity_800hPa",  # 1900 m
        "relative_humidity_700hPa",  # 3000 m
        "relative_humidity_600hPa",  # 4200 m
        "relative_humidity_500hPa",  # 5600 m
        "relative_humidity_400hPa",  # 7200 m
        "relative_humidity_300hPa",  # 9600 m
    ],
    "windSpeed": [
        "wind_speed_1000hPa",  # 110 m
        "wind_speed_975hPa",  # 320 m
        "wind_speed_950hPa",  # 500 m
        "wind_speed_925hPa",  # 800 m
        "wind_speed_900hPa",  # 1000 m
        "wind_speed_850hPa",  # 1500 m
        "wind_speed_800hPa",  # 1900 m
        "wind_speed_700hPa",  # 3000 m
        "wind_speed_600hPa",  # 4200 m
        "wind_speed_500hPa",  # 5600 m
        "wind_speed_400hPa",  # 7200 m
        "wind_speed_300hPa",  # 9600 m
    ],
    "windDirection": [
        "wind_direction_1000hPa",  # 110 m
        "wind_direction_975hPa",  # 320 m
        "wind_direction_950hPa",  # 500 m
        "wind_direction_925hPa",  # 800 m
        "wind_direction_900hPa",  # 1000 m
        "wind_direction_850hPa",  # 1500 m
        "wind_direction_800hPa",  # 1900 m
        "wind_direction_700hPa",  # 3000 m
        "wind_direction_600hPa",  # 4200 m
        "wind_direction_500hPa",  # 5600 m
        "wind_direction_400hPa",  # 7200 m
        "wind_direction_300hPa",  # 9600 m
    ],
}


def fetch_data(url: str, params: dict) -> WeatherApiResponse:
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    client = openmeteo_requests.Client(session=retry_session)
    response: WeatherApiResponse = client.weather_api(url, params=params)[0]
    return response


def process_data(
    properties: list[str], hours: int, numHeightSteps: int, hourly: VariablesWithTime, dataDir: str
):
    out: dict[str, np.ndarray] = {}
    for property in properties:
        out[property] = np.zeros(
            (hours, numHeightSteps)
        )  # Each property in the output will be (hours x heightSteps) size

    for i in range(len(properties)):  # for each property
        var = np.zeros((hours, numHeightSteps))
        for j in range(
            numHeightSteps * i, numHeightSteps * (i + 1)
        ):  # for each height step of that property
            var[:, j % numHeightSteps] = hourly.Variables(j).ValuesAsNumpy()
        out[properties[i]] = var
    for prop, data in out.items():
        filename = dataDir + f"{prop}_data.csv"
        np.savetxt(filename, data, delimiter=",", fmt="%.5f")
        print(f"Exported {filename}")
    return out


def fetch_historical_data(
    lat: float, lon: float, properties: list[str], start_date: date, end_date: date
) -> dict[str, np.ndarray]:
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    callProperties = [propertiesMap[prop] for prop in properties]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": callProperties,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "ms",
    }

    response: WeatherApiResponse = fetch_data(url, params)

    hourly: VariablesWithTime = response.Hourly()

    numHeightSteps = len(heightSteps)
    hours = ((end_date - start_date).days + 1) * 24

    return process_data(properties, hours, numHeightSteps, hourly, DATA_DIR + "historical/")


# Calls the open-meteo api and returns a dictionary of each of the requested properties
def fetch_current_data(
    lat: float, lon: float, properties: list[str], days: int
) -> dict[str, np.ndarray]:
    """Fetch data from openMeteo API"""

    # This isn't very good practice and should probably be changed
    validateDays(days)
    validateProperties(properties)

    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Construct the properties that are desired in the necessary format for the API call
    callProperties = [propertiesMap[prop] for prop in properties]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": callProperties,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "ms",
        "forecast_days": days,
    }

    response: WeatherApiResponse = openmeteo.weather_api(url, params=params)[0]

    hourly: VariablesWithTime = response.Hourly()

    numHeightSteps = len(heightSteps)
    hours = days * 24

    return process_data(properties, hours, numHeightSteps, hourly, DATA_DIR)
