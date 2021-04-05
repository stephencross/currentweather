#!/usr/bin/python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logging.info("E-Ink weather API")

## Refresh rate in seconds
weather_refresh = 30 * 60;

# openweathermap API www.openweathermap.org
# Retrieves current weather by zipcode
baseurl = 'http://api.openweathermap.org/data/2.5/weather'
apikey = 'Your-apikey'
zip = '02809'
units = 'imperial'
apicall = baseurl + '?zip=' + zip + '&units=' + units + '&appid=' + apikey


def get_weather():

    global desc
    global temp
    global feels_like
    global low
    global high
    global degree
    
    logging.info("Getting current weather.")
    response = requests.get(apicall)
    if response.status_code == 200:
        try:
            jsonResponse = response.json()
            desc = jsonResponse["weather"][0]["description"]
            temp = jsonResponse["main"]["temp"]
            feels_like = jsonResponse["main"]["feels_like"]
            low = jsonResponse["main"]["temp_min"]
            high = jsonResponse["main"]["temp_max"]
            degree = "\N{DEGREE SIGN}"
            return True
        except:
            logging.debug("Weather JSON parsing error.")
            return False
    else:
        logging.debug("Weather API call error.")
        return False

try:
    epd = epd2in13b_V3.EPD()
    
    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    
    while True:
        
        if get_weather():
            
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            
            logging.info("Init and Clear " + dt_string)
            epd.init()
            epd.Clear()
            
            # Diplay weather data
            logging.info("Display weather data.") 
            HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
            HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image  
            drawblack = ImageDraw.Draw(HBlackimage)
            drawry = ImageDraw.Draw(HRYimage)
            drawblack.text((10, 0), dt_string, font = font20, fill = 0)
            drawblack.text((10, 20), 'Bristol', font = font20, fill = 0)
            drawblack.text((10, 40), desc.capitalize(), font = font20, fill =  0)
            drawblack.text((10, 60), str(temp) + degree + " Feels Like " + str(feels_like) + degree + " (" + str(low) + degree + "/" + str(high) + degree + ")", font = font20, fill = 0)
            drawblack.text((10, 80), "(" + str(low) + degree + "/" + str(high) + degree + ")", font = font20, fill = 0)

            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            time.sleep(2)
               
            logging.info("Goto Sleep...")
            epd.sleep()
            time.sleep(weather_refresh)
        else:
            raise KeyboardInterrupt
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13b_V3.epdconfig.module_exit()
    exit()