from matplotlib import pyplot as plt
import requests

base = "https://api.weather.gov"
endpoint = "/points"

latitude = 43.00139
longitude = -78.7907

url = base + endpoint + "/" + str(latitude) + "," + str(longitude)
headers = {"Accept": "application/geo+json"}
response = requests.get(url, headers=headers).json()

forcast_url = response["properties"]["forecastHourly"]
weather_data = requests.get(forcast_url, headers=headers).json()

temps = [period["temperature"] for period in weather_data["properties"]["periods"]]

plt.plot(temps)
plt.show()
