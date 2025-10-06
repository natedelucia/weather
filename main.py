import requests

base = "https://api.weather.gov"
endpoint = "/points"

latitude = 43.00139
longitude = -78.7907

url = base + endpoint + "/" + str(latitude) + "," + str(longitude)

headers = {"Accept": "application/geo+json"}

response: requests.Response = requests.get(url, headers=headers)

print(response.json())
