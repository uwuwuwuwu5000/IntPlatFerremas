import requests
from datetime import datetime

class BancoCentralAPI:
    BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def obtener_valores(self, series_id, start_date, end_date):
        params = {
            "user": self.user,
            "pass": self.password,
            "timeseries": series_id,
            "startdate": start_date,
            "enddate": end_date,
            "output": "json"
        }

        # Imprimir la URL generada para verificar los parámetros
        url = requests.Request('GET', self.BASE_URL, params=params).prepare().url
        print(f"URL generada: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data

        except requests.RequestException as e:
            print(f"Error al conectar con la API del Banco Central: {e}")
            return None

