#!/usr/bin/env python3
import telebot
import time
import json
import requests
from threading import Thread

from camera import Camera
from sensor import Sensor


def safe_send(attempts, f, *args, **kwargs):
    sent = False
    for _ in range(attempts):
        try:
            f(*args, **kwargs)
            sent = True
        except requests.exceptions.ConnectionError as e:
            print(e)
        if sent:
            break
        time.sleep(0.5)
    return sent


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
            camera.shot_to_buffer()
            time.sleep(0.5)

    def sensor_loop():
        while True:
            sensor.update()

    camera_thread = Thread(target=camera_loop, daemon=True)
    sensor_thread = Thread(target=sensor_loop, daemon=True)
    camera_thread.start()
    sensor_thread.start()

    while True:
        if sensor.state['move']:
            sensor.state['move'] = False
            time.sleep(1)  # make more shots with detected objects
            movie = camera.movie()
            safe_send(5, bot.send_video, config["secret_channel"], movie,
                      caption='обнаружено движение')

        if last_report is None or (time.time() - last_report > public_period):
            safe_send(5, bot.send_message, config["public_channel"],
                      str(sensor), parse_mode='Markdown')
            last_report = time.time()
        time.sleep(0.25)
