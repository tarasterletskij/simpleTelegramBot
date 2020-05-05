import pyowm

from filehandler import FileHandler
from settings import W_TOKEN


class Weather:
    def __init__(self):
        self.owm = pyowm.OWM(W_TOKEN, language="EN")
        self.file_handler = FileHandler()

    def get_city_weather(self, city: str):
        observation = self.owm.weather_at_place(city)
        w = observation.get_weather()
        # Weather details
        wind = w.get_wind()  # {"speed": 4.6, "deg": 330}
        temp = w.get_temperature("celsius")

        return temp["temp"], wind["speed"], w.get_detailed_status()

    def get_weather_message(self, city: str, user_id: int):
        try:
            temperature, wind_speed, status = self.get_city_weather(city)
            self.file_handler.save_location(user_id, city)

            mes = f"In city '{city.capitalize()}' now is {status}. \n" \
                  f"Air temperature: {temperature} °C ,\n" \
                  f"Wind speed: {wind_speed} m/s\n" \
                  f"Maybe you want to know the weather in another city? \n\n"
            return {
                "success": True,
                "message": mes
            }
        except:
            return {
                "success": False,
                "message": f"I can't find such city like:  {city}. Try typing on English \n"
            }
