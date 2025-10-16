# defines the environment class, which contains all of the weather data for a given time and place

from datetime import date
from matplotlib import pyplot as plt
import numpy as np
from utils import *
from fetch import *


class Environment:
    """
    Initialize weather data given a specific latitude, longitude, and time.
    Currently tracks temperature, pressure, wind direction, and
    wind speed at stepped altitudes
    """

    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon
        self.atmosphere: dict[str, np.ndarray] = {}

    def fetchOpenMeteoData(
        self, properties: list[str], days: int
    ) -> dict[str, np.ndarray]:
        """
        Calls the openMeteo API for the desired properties
        Properties should be from list ["temp", "humidity", "windSpeed", "windDirection"]
        Days is number of days in the future to forecast, and should be in the list
        """
        self.atmosphere = fetch_current_data(self.lat, self.lon, properties, days)
        return self.atmosphere

    def getAtHeight(self, property: str, height: int, hour: int):
        """
        Return a given property from the atmosphere attribute given a specific height and time
        If height is below the minimum height step, returns the value at the minimum height step
        Otherwise, linearly approximates the property between the two nearest height steps
        """
        if self.atmosphere == {}:
            raise Exception("Call the API before accessing environment data")
        validateProperties([property])
        if property not in self.atmosphere.keys():
            raise Exception(
                f"{property} is valid, but was not given as a property to be retrieved from the API"
            )
        if not 0 <= height <= heightSteps[-1]:
            raise Exception(f"Height of {height} out of bounds")
        if not 0 <= hour < self.atmosphere[property].shape[0]:
            raise Exception(
                f"Hour {hour} is out of bounds\nMax hour for this API call is {self.atmosphere[property].shape[0]}"
            )

        return np.interp(height, heightSteps, self.atmosphere[property][hour])
    
    def graph(self, properties: list[str]):
        for property in properties:
            for i in range(self.atmosphere[property].shape[1]):
                plt.plot(self.atmosphere[property][:,i], label=f"{property} at {heightSteps[i]}m")
        plt.legend()
        plt.show()

class HistoricalEnvironment(Environment):
    def __init__(self, lat: float, lon: float, start_date: date, end_date: date) -> None:
        super().__init__(lat, lon)
        self.start_date = start_date
        self.end_date = end_date
    
    def fetchOpenMeteoData(
        self, properties: list[str], days=None
    ) -> dict[str, np.ndarray]:
        self.atmosphere = fetch_historical_data(self.lat, self.lon, properties, self.start_date, self.end_date)
        return self.atmosphere

# Mostly for testing, but it does show the proper use of some of the functions so I guess I'll leave it
def main():
    env = HistoricalEnvironment(*coordinates["Texas"], date(2024, 1, 1), date(2024, 12, 31))
    # env = Environment(*coordinates["Texas"])
    env.fetchOpenMeteoData(validProperties, 3)
    env.graph(["temp"])

    # env = Environment(*coordinates["UB"])
    # env.fetchOpenMeteoData(validProperties, days=1)
    # print(env.getAtHeight("windSpeed", 320, 3))
    # for height in range(0, 1000, 100):
    #     print(env.getAtHeight("windSpeed", height, 1))


if __name__ == "__main__":
    main()
