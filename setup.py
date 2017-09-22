# -*- coding: utf-8 -*-
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rpi-temperature-mqtt',
    version='0.0.3',
    description='Send temperature from DS18B20 sensors to mqtt broker',
    long_description=readme,
    author='David Uebelacker',
    author_email='david@uebelacker.ch',
    url='https://github.com/goodfield/rpi-temperature-mqtt.git',
    license=license,
    packages=['rpi_temperature_mqtt'],
    install_requires=['paho-mqtt'],
    scripts=['bin/rpi-temperature-mqtt']
)
