import time
import re
import socket
import sys

import traceback

import paho.mqtt.client as mqtt
from threading import Thread

class TemperatureLogger:
    config = None
    mqtt_client = None
    mqtt_connected = False
    worker = None
    temperatures = {}

    def __init__(self, config):
        self.config = config

    def verbose(self, message):
        if self.config and 'verbose' in self.config and self.config['verbose'] == 'true':
            sys.stdout.write('VERBOSE: ' + message + '\n')
            sys.stdout.flush()

    def error(self, message):
        sys.stderr.write('ERROR: ' + message + '\n')
        sys.stderr.flush()

    def mqtt_connect(self):
        if self.mqtt_broker_reachable():
            self.verbose('Connecting to ' + self.config['mqtt_host'] + ':' + self.config['mqtt_port'])
            self.mqtt_client = mqtt.Client(self.config['mqtt_client_id'])
            if 'mqtt_user' in self.config and 'mqtt_password' in self.config:
                self.mqtt_client.username_pw_set(self.config['mqtt_user'], self.config['mqtt_password'])

            self.mqtt_client.on_connect = self.mqtt_on_connect
            self.mqtt_client.on_disconnect = self.mqtt_on_disconnect

            try:
                self.mqtt_client.connect(self.config['mqtt_host'], int(self.config['mqtt_port']), 60)
                self.mqtt_client.loop_forever()
            except:
                self.error(traceback.format_exc())
                self.mqtt_client = None
        else:
            self.error(self.config['mqtt_host'] + ':' + self.config['mqtt_port'] + ' not reachable!')

    def mqtt_on_connect(self, mqtt_client, userdata, flags, rc):
        self.mqtt_connected = True
        self.verbose('...mqtt_connected!')

    def mqtt_on_disconnect(self, mqtt_client, userdata, rc):
        self.mqtt_connected = False
        self.verbose('Diconnected! will reconnect! ...')
        if rc is 0:
            self.mqtt_connect()
        else:
            time.sleep(5)
            while not self.mqtt_broker_reachable():
                time.sleep(10)
            self.mqtt_client.reconnect()

    def mqtt_broker_reachable(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.config['mqtt_host'], int(self.config['mqtt_port'])))
            s.close()
            return True
        except socket.error:
            return False

    def update(self):
        while True:
            for source in self.config['sources']:
                serial = source['serial']
                topic = source['topic']
                device = open('/sys/bus/w1/devices/' + serial + '/w1_slave')
                raw = device.read()
                device.close()
                match = re.search(r't=([\d]+)', raw)
                if match:
                    temperature_raw = match.group(1)
                    temperature = round(float(temperature_raw)/1000, 2)

                    if 'offset' in source:
                        temperature += float(source['offset'])

                    if serial not in self.temperatures or self.temperatures[serial] != temperature:
                        self.temperatures[serial] = temperature
                        self.publish_temperature(topic, temperature)
                time.sleep(5)
            time.sleep(300)

    def publish_temperature(self, topic, temperature):
        if self.mqtt_connected:
            self.verbose('Publishing: ' + str(temperature))
            self.mqtt_client.publish(topic, str(temperature), 0, True)

    def start(self):
        self.worker = Thread(target=self.update)
        self.worker.setDaemon(True)
        self.worker.start()
        self.mqtt_connect()
