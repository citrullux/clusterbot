#!/usr/bin/env python3
import telebot
import time
import json
import requests
import imageio
import io

from image_buffer import ImageBuffer
from sensor import Sensor


def get_image(url, auth=()):
    r = requests.get(url, auth=auth)
    return imageio.imread(io.BytesIO(r.content))


if __name__ == '__main__':
    config = json.load(open('config.json'))
    bot = telebot.TeleBot(config["token"])
    ib = ImageBuffer(capacity=10)
    sensor = Sensor("/dev/ttyACM0", 115200)
    public_period = 1800
    last_report = None
    for _ in range(ib.capacity):
        img = get_image(config["img_url"], (config["login"], config["password"]))
        ib.append(img)
    while True:
        sensor.update()

        img = get_image(config["img_url"], (config["login"], config["password"]))
        ib.append(img)

        if sensor.state['move']:
            bot.send_video(config["secret_channel"], ib.movie(), caption='обнаружено движение')

        if last_report is None or (time.time() - last_report > public_period):
            bot.send_message(config["public_channel"],
                             str(sensor),
                             parse_mode='Markdown')
            last_report = time.time()
