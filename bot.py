#!/usr/bin/env python3
import telebot
import time
import json
import requests
from threading import Thread

from camera import Camera
from sensor import Sensor
from power import Power


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
    power = Power()
    public_period = 1800
    last_report = None
    bad_voltage_period = 1800
    last_bad_voltage = None
    bad_temperature_period = 1800
    last_bad_temperature = None
    possible_powerless = False

    def camera_loop():
        while True:
            camera.shot_to_buffer()
            time.sleep(0.5)

    def sensor_loop():
        while True:
            sensor.update()

    def power_loop():
        while True:
            power.update()
            time.sleep(2)

    camera_thread = Thread(target=camera_loop, daemon=True)
    sensor_thread = Thread(target=sensor_loop, daemon=True)
    power_thread = Thread(target=power_loop, daemon=True)
    camera_thread.start()
    sensor_thread.start()
    power_thread.start()

    while True:
        if max(filter(bool, sensor.temperature)) > 30:
            if (last_bad_temperature is None or
                   (time.time() - last_bad_temperature > bad_temperature_period)):
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Температура за пределами нормальных значений*\n'
                        '%s' % power, parse_mode='Markdown')
                if last_bad_temperature is None:
                    last_bad_temperature = time.time()
                else:
                    last_bad_temperature += bad_temperature_period
        else:
            if not last_bad_temperature is None:
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Температура вернулось в норму*\n'
                        '%s' % power, parse_mode='Markdown')
                last_bad_temperature = None


        if sensor.state['move']:
            sensor.state['move'] = False
            time.sleep(1)  # make more shots with detected objects
            movie = camera.movie()
            safe_send(5, bot.send_video, config["secret_channel"], movie,
                      caption='обнаружено движение')

        if power.should_be_enabled():
            power.enable()
        if power.possible_powerless():
            if not possible_powerless:
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Внимание, возможен обрыв питания*\n'
                        'Если кто-то есть на месте, проверьте кластерную\n'
                        '%s' % power, parse_mode='Markdown')
                possible_powerless = True
        else:
            if possible_powerless:
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Помнишь я визжал про обрыв питания?'
                        'Так вот, теперь вроде всё норм*\n'
                        '%s' % power, parse_mode='Markdown')
                possible_powerless = False
        if power.should_be_disabled():
            safe_send(5, bot.send_message, config["secret_channel_power"],
                    '*Начата процедура отключения*\n'
                    '%s' % power, parse_mode='Markdown')
            power.disable()
        if power.bad_voltage():
            if (last_bad_voltage is None or
                   (time.time() - last_bad_voltage > bad_voltage_period)):
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Напряжение за пределами нормальных значений*\n'
                        '%s' % power, parse_mode='Markdown')
                if last_bad_voltage is None:
                    last_bad_voltage = time.time()
                else:
                    last_bad_voltage += bad_voltage_period
        else:
            if not last_bad_voltage is None:
                safe_send(5, bot.send_message, config["secret_channel_power"],
                        '*Напряжение вернулось в норму*\n'
                        '%s' % power, parse_mode='Markdown')
                last_bad_voltage = None

        if last_report is None or (time.time() - last_report > public_period):
            safe_send(5, bot.send_message, config["public_channel"],
                      '%s\n\n%s' % (sensor, power), parse_mode='Markdown')
            if last_report is None:
                last_report = time.time()
            else:
                last_report += public_period
        time.sleep(0.25)
