import tkinter as tk
try:
    import requests
except ImportError:
    requests = None
import time

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather?q="
APP_ID = "06c921750b9a82d8f5d1294e1586276f"

textField = None
label1 = None
label2 = None


def parse_weather_data(json_data: dict) -> tuple[str, str]:
    """
    Pure data transformer parsing OpenWeather JSON response into UI strings.

    Contract:
    - Precondition: json_data contains 'weather', 'main', 'wind', and 'sys' fields.
    - Deterministic: Same JSON input produces identical formatted strings.
    - Output: tuple (final_info, final_data)
    """
    condition = json_data['weather'][0]['main']
    temp = int(json_data['main']['temp'] - 273.15)
    min_temp = int(json_data['main']['temp_min'] - 273.15)
    max_temp = int(json_data['main']['temp_max'] - 273.15)
    pressure = json_data['main']['pressure']
    humidity = json_data['main']['humidity']
    wind = json_data['wind']['speed']
    sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
    sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))

    final_info = condition + "\n" + str(temp) + "°C"
    final_data = ("\n" + "Min Temp: " + str(min_temp) + "°C" + "\n"
                  + "Max Temp: " + str(max_temp) + "°C" + "\n"
                  + "Pressure: " + str(pressure) + "\n"
                  + "Humidity: " + str(humidity) + "\n"
                  + "Wind Speed: " + str(wind) + "\n"
                  + "Sunrise: " + sunrise + "\n"
                  + "Sunset: " + sunset)
    return final_info, final_data


def fetch_weather(city: str, session=requests) -> dict:
    """Fetch weather json for city using injected HTTP session/client."""
    api = f"{OPENWEATHER_BASE_URL}{city}&appid={APP_ID}"
    response = session.get(api)
    return response.json()


def getWeather(canvas=None, text_field=None, lbl1=None, lbl2=None, session=requests):
    """
    Controller function reading text field, fetching weather, and updating labels.

    Preconditions:
    - Weather GUI/weather.py:1-3 establishes tkinter, requests, time imports
    - Weather GUI/weather.py:6 establishes getWeather signature
    - Weather GUI/weather.py:8 establishes OpenWeather endpoint URL
    """
    tf = text_field if text_field is not None else textField
    l1 = lbl1 if lbl1 is not None else label1
    l2 = lbl2 if lbl2 is not None else label2

    city = tf.get() if tf is not None else ""
    json_data = fetch_weather(city, session=session)
    final_info, final_data = parse_weather_data(json_data)

    if l1 is not None:
        l1.config(text=final_info)
    if l2 is not None:
        l2.config(text=final_data)

    return final_info, final_data


def main():
    global textField, label1, label2
    canvas = tk.Tk()
    canvas.geometry("600x500")
    canvas.title("Weather App")
    f = ("poppins", 15, "bold")
    t = ("poppins", 35, "bold")

    textField = tk.Entry(canvas, justify='center', width=20, font=t)
    textField.pack(pady=20)
    textField.focus()
    textField.bind('<Return>', getWeather)

    label1 = tk.Label(canvas, font=t)
    label1.pack()
    label2 = tk.Label(canvas, font=f)
    label2.pack()
    canvas.mainloop()


if __name__ == '__main__':
    main()
