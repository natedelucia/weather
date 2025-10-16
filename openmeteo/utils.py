# Constants
heightSteps: list[int] = [
    110,
    320,
    500,
    800,
    1000,
    1500,
    1900,
    3000,
    4200,
    5600,
    7200,
    9200,
]

coordinates: dict[str, tuple[float, float]] = {
    "Spaceport America": (32.938358, -106.912406),
    "Utah1": (37.931728, -113.053677),
    "Utah2": (37.945524, -113.033278),
    "Texas": (31.049802, -103.547313),
    "UB": (43.000139, -78.790739),
}

validProperties: list[str] = ["temp", "humidity", "windSpeed", "windDirection"]
validDays: list[int] = [1, 3, 7, 14, 16]

def validateProperties(properties: list[str]) -> None:
    """Determines is given properties are valid, throws exception if not"""
    validSet = set(validProperties)
    actualSet = set(properties)
    if not actualSet.issubset(validSet):
        raise Exception(
            f"{list(actualSet - validSet)} are not valid properties\nValid properties are {validProperties}"
        )


def validateDays(days: int) -> None:
    """Determines if given number of days is valid, throws exception if not"""
    if days not in validDays:
        raise Exception(
            f"{days} is not a valid forecast range\nDays must be 1, 3, 7, 14, or 16"
        )
