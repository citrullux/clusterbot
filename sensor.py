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
        self.indexes = {'3a': 0, '3b': 1, '48': 2}
        self.state = {'temperature': [None, None, None],
                      'humidity': [None, None, None],
                      'smoke': [None, None],
                      'move': False}
        self.move_detected = 0
        for _ in range(3):
            self.update()

    def update(self):
        self.state['move'] = False
        line = self.ser.readline().decode("utf-8")
        while not line.startswith('{"id"'):
            line = self.ser.readline().decode("utf-8")
        else:
            line = re.sub(r"0x00(\w{2})\w+", r'"\1"', line)
            line = re.sub(r"undefined", r"null", line)

            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError:
                return self.update()

            index = self.indexes[data['id']]
            self.state['temperature'][index] = data['temperature']
            self.state['humidity'][index] = data['humidity']
            if data['id'] == '48':
                if data['move']:
                    self.move_detected += 1
                else:
                    self.move_detected = 0
                if self.move_detected == 2:
                    self.state['move'] = True
            else:
                self.state['smoke'][index] = data['smoke']

    def __str__(self):
        s = ["*Отчёт по датчикам*",
             "Температуры: %s %s %s" % tuple(self.state['temperature']),
             "Влажность: %s %s %s" % tuple(self.state['humidity']),
             "Задымлённость: %s %s" % tuple(self.state['smoke']),
             "Движение: %s" % self.state['move']]
        return "\n".join(s)

