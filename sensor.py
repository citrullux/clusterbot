import serial
import re
import json


class Sensor:
    def __init__(self, device, baudrate):
        self.ser = serial.Serial(device, baudrate)
        self.indicator_names = {
           'humidity': 'Влажность воздуха (%)',
           'smoke': 'Задымлённость',
           'move': 'Движение',
           'temperature': 'Температура (С)'
        }
        self.state = {}

    def update(self):
        line = self.ser.readline().decode("utf-8")
        line = re.sub(r"0x00(\w{2})\w+", r'"\1"', line)
        line = re.sub(r"undefined", r"null", line)
        if line.startswith('{"id"'):
            data = json.loads(line)
            self.state[data['id']] = data
