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
    ib = ImageBuffer(capacity=5)
    sensor = Sensor("/dev/ttyACM0", 115200)
    public_period = 1800
    last_report = None
    k = 0
    while True:
        k+=1
        sensor.update()
        img = get_image(config["img_url"],
                        auth=(config["login"], config["password"]))
        ib.append(img)
        # if '48' in sensor.state and sensor.state['48']['move']:
        if k == 5:
            k = 0
            bot.send_message(config["secret_channel"], 'обнаружено движение')
            print('send gif')
            bot.send_video(config["secret_channel"], ib.gif())

        if last_report is None or (time.time() - last_report > public_period):
            bot.send_message(config["public_channel"],
                             "```%s```" % str(sensor.state),
                             parse_mode='Markdown')
            last_report = time.time()
