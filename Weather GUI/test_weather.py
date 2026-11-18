import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure Weather GUI directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Auto-add site-packages from .venv if requests is not installed in standard sys.path
try:
    import requests
except ImportError:
    for venv_path in [
        os.path.join(BASE_DIR, "..", "..", ".venv"),
        os.path.join(BASE_DIR, "..", ".venv"),
    ]:
        lib = os.path.join(venv_path, "lib")
        if os.path.exists(lib):
            for p in os.listdir(lib):
                sp = os.path.join(lib, p, "site-packages")
                if os.path.exists(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
    try:
        import requests
    except ImportError:
        from unittest.mock import MagicMock
        sys.modules["requests"] = MagicMock()

import weather as w_module


class TestWeatherRepeatability(unittest.TestCase):
    """
    Focused repeatable verification tests for getWeather (weather.py).
    Precondition source lines:
      - weather.py:1-3 establishes imports
      - weather.py:5 establishes OPENWEATHER_BASE_URL
      - weather.py:12 establishes parse_weather_data
      - weather.py:46 establishes getWeather
    """

    def test_preconditions(self):
        self.assertTrue(w_module.OPENWEATHER_BASE_URL.startswith("https://api.openweathermap.org/data/2.5/weather?q="))
        self.assertEqual(w_module.APP_ID, "06c921750b9a82d8f5d1294e1586276f")

    def test_smallest_valid_input(self):
        # Smallest valid input JSON payload
        small_payload = {
            "weather": [{"main": "Clear"}],
            "main": {"temp": 273.15, "temp_min": 273.15, "temp_max": 273.15, "pressure": 1000, "humidity": 0},
            "wind": {"speed": 0.0},
            "sys": {"sunrise": 21600, "sunset": 21600},
        }

        info, data = w_module.parse_weather_data(small_payload)
        expected_info = "Clear\n0°C"
        expected_data = "\nMin Temp: 0°C\nMax Temp: 0°C\nPressure: 1000\nHumidity: 0\nWind Speed: 0.0\nSunrise: 12:00:00\nSunset: 12:00:00"

        self.assertEqual(info, expected_info)
        self.assertEqual(data, expected_data)

    def test_ordinary_valid_input(self):
        # Ordinary valid input (London weather)
        ordinary_payload = {
            "weather": [{"main": "Clouds"}],
            "main": {"temp": 288.15, "temp_min": 285.15, "temp_max": 290.15, "pressure": 1013, "humidity": 72},
            "wind": {"speed": 4.5},
            "sys": {"sunrise": 43200, "sunset": 86400},
        }

        info, data = w_module.parse_weather_data(ordinary_payload)
        expected_info = "Clouds\n15°C"
        expected_data = "\nMin Temp: 12°C\nMax Temp: 17°C\nPressure: 1013\nHumidity: 72\nWind Speed: 4.5\nSunrise: 06:00:00\nSunset: 06:00:00"

        self.assertEqual(info, expected_info)
        self.assertEqual(data, expected_data)

    def test_repeatability_100_runs(self):
        # Verify 100 repeated executions yield identical deterministic results
        sample_payload = {
            "weather": [{"main": "Rain"}],
            "main": {"temp": 295.15, "temp_min": 293.15, "temp_max": 296.15, "pressure": 1008, "humidity": 85},
            "wind": {"speed": 3.2},
            "sys": {"sunrise": 36000, "sunset": 72000},
        }

        first_info, first_data = w_module.parse_weather_data(sample_payload)
        for _ in range(100):
            cur_info, cur_data = w_module.parse_weather_data(sample_payload)
            self.assertEqual(cur_info, first_info)
            self.assertEqual(cur_data, first_data)

    def test_get_weather_with_injected_dependencies(self):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "weather": [{"main": "Sunny"}],
            "main": {"temp": 303.15, "temp_min": 300.15, "temp_max": 305.15, "pressure": 1010, "humidity": 45},
            "wind": {"speed": 2.1},
            "sys": {"sunrise": 30000, "sunset": 75000},
        }
        mock_session.get.return_value = mock_response

        mock_tf = MagicMock()
        mock_tf.get.return_value = "Tokyo"

        mock_l1 = MagicMock()
        mock_l2 = MagicMock()

        info, data = w_module.getWeather(
            text_field=mock_tf, lbl1=mock_l1, lbl2=mock_l2, session=mock_session
        )

        self.assertIn("Sunny\n30°C", info)
        self.assertIn("Pressure: 1010", data)
        mock_l1.config.assert_called_once_with(text=info)
        mock_l2.config.assert_called_once_with(text=data)


if __name__ == "__main__":
    unittest.main()
