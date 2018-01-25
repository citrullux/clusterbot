#!/usr/bin/env python3
import telebot
import time
import json
import requests
from threading import Thread

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

    def camera_loop():
        while True:
            print("Update camera")
            camera.shot_to_buffer()
            time.sleep(0.5)

    def sensor_loop():
        while True:
            print("Update sensor")
            sensor.update()

    camera_thread = Thread(target=camera_loop)
    sensor_thread = Thread(target=sensor_loop)
    camera_thread.setDaemon(True)
    sensor_thread.setDaemon(True)
    camera_thread.start()
    sensor_thread.start()

    while True:
        if sensor.state['move']:
            time.sleep(1) # make more shots with detected objects
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
        time.sleep(0.5)
