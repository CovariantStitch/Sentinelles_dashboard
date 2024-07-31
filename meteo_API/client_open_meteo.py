import requests


class ClientOpenMeteo:
    def __init__(self):
        self.url = "https://archive-api.open-meteo.com/v1/era5?"

    def get_meteo(self, latitude, longitude, start_date, end_date):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["temperature_2m_mean"],
            "timezone": "Europe/Berlin",
            "start_date": start_date,
            "end_date": end_date
        }

        response = requests.get(self.url, params=params)
        return response.json()
