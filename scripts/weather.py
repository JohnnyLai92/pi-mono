"""
Weather query module for PiBot.
Uses wttr.in (free, no API key required).
Usage:
  from weather import get_weather
  get_weather("台中市")

Run directly to send a weather report email:
  python weather.py
"""

import logging
import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

from send_email import send_email

logger = logging.getLogger(__name__)


def get_weather(location: str = "台中市") -> dict | None:
    """
    Get current weather information for a location.
    Uses wttr.in (free, no API key required).
    Returns a dict with weather info or None on failure.
    """
    # Map location to English for wttr.in
    location_map = {
        "台北": "Taipei",
        "台北市": "Taipei",
        "台中": "Taichung",
        "台中市": "Taichung",
        "高雄": "Kaohsiung",
        "高雄市": "Kaohsiung",
        "台南": "Tainan",
        "台南市": "Tainan",
        "桃園": "Taoyuan",
        "桃園市": "Taoyuan",
        "新竹": "Hsinchu",
        "新竹市": "Hsinchu",
    }
    
    wttr_location = location_map.get(location, "Taichung")
    url = f"https://wttr.in/{wttr_location}?format=j1"
    
    try:
        # Disable SSL verification for corporate proxy environments
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        
        weather_info = {
            "location": area["areaName"][0]["value"],
            "temperature": int(current["temp_C"]),
            "feels_like": int(current["FeelsLikeC"]),
            "humidity": int(current["humidity"]),
            "description": current["weatherDesc"][0]["value"],
            "wind_speed": int(current["windspeedKmph"]),
            "cloud_cover": int(current["cloudcover"]),
            "precipitation": float(current["precipMM"]),
        }
        
        logger.info("Weather retrieved for %s: %s°C, %s", 
                   weather_info["location"], 
                   weather_info["temperature"],
                   weather_info["description"])
        
        return weather_info
        
    except Exception as exc:  # noqa: BLE001
        logger.error("Weather query failed: %s", exc)
        return None


def format_weather_report(weather_info: dict) -> str:
    """Format weather info into a readable report."""
    # Translate weather description to Chinese
    desc_map = {
        "Sunny": "晴朗",
        "Clear": "晴朗",
        "Partly cloudy": "多雲時晴",
        "Cloudy": "多雲",
        "Overcast": "陰天",
        "Mist": "薄霧",
        "Fog": "霧",
        "Light rain": "小雨",
        "Moderate rain": "中雨",
        "Heavy rain": "大雨",
        "Rain": "雨",
        "Thundery outbreaks possible": "可能有雷陣雨",
        "Patchy rain possible": "可能有雨",
    }
    
    desc_zh = desc_map.get(weather_info["description"], weather_info["description"])
    
    # Estimate rain probability from cloud cover and precipitation
    rain_prob = min(100, weather_info["cloud_cover"] // 2 + int(weather_info["precipitation"]) * 10)
    
    report = f"""Weather Report - {weather_info['location']}

Location: {weather_info['location']}
Temperature: {weather_info['temperature']}C (Feels like {weather_info['feels_like']}C)
Condition: {desc_zh}
Humidity: {weather_info['humidity']}%
Wind Speed: {weather_info['wind_speed']} km/h
Cloud Cover: {weather_info['cloud_cover']}%
Rain Probability: ~{rain_prob}%

Query Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Have a nice day!
"""
    return report


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    location = sys.argv[1] if len(sys.argv) > 1 else "台中市"
    
    print(f"Querying weather for {location}...")
    weather_info = get_weather(location)
    
    if weather_info:
        report = format_weather_report(weather_info)
        print(report)
        
        # Send email report
        email_sent = send_email(
            subject=f"[小白報報] {location} 天氣預報",
            body=report,
        )
        
        if email_sent:
            print("Weather report sent to your email successfully!")
            sys.exit(0)
        else:
            print("Weather report displayed above, but email sending failed.")
            sys.exit(1)
    else:
        print("Weather query failed. Please check your network connection.")
        sys.exit(1)
