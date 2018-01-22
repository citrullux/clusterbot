#!/usr/bin/env python3
import telebot
import time
import json
import requests

from camera import Camera
from sensor import Sensor


if __name__ == '__main__':
    config = json.load(open('config.json'))
    bot = telebot.TeleBot(config["token"])
    camera = Camera(config["img_url"], (config["login"], config["password"]),
                    video_length=10)
    sensor = Sensor("/dev/ttyACM0", 115200)
    public_period = 1800
    last_report = None
    while True:
        sensor.update()
        camera.shot_to_buffer()

        if sensor.state['move']:
            sent = False
            while not sent:
                try:
                    bot.send_video(config["secret_channel"], camera.movie(),
                                   caption='обнаружено движение')
                    sent = True
                except requests.exceptions.ConnectionError as e:
                    print(e)
                time.sleep(0.5)

        if last_report is None or (time.time() - last_report > public_period):
            sent = False
            while not sent:
                try:
                    bot.send_message(config["public_channel"], str(sensor),
                                     parse_mode='Markdown')
                    sent = True
                except requests.exceptions.ConnectionError as e:
                    print(e)
                time.sleep(0.5)
            last_report = time.time()
