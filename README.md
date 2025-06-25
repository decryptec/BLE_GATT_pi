# Simple Python BLE GATT Menu on Raspberry Pi for iPhone/iOS

This project provides a minimalist Python interface using [Bleak](https://github.com/hbldh/bleak) to create a Bluetooth Low Energy (BLE) GATT menu system on a Raspberry Pi. Designed for communication with iPhones and other iOS devices, it allows you to build custom BLE services and characteristics with menu-driven navigation.

## Features

- 📱 iPhone/iOS compatibility with native BLE scanning and connection
- 🍓 Raspberry Pi ready (tested on Raspberry Pi 4 with Raspberry Pi OS)
- 🧭 Command-line menu for easy service and characteristic configuration
- 🔗 GATT server behavior (custom services and characteristics)
- 🧪 Clean architecture for easy experimentation or extension

## Prerequisites

- Python 3.7+
- Raspberry Pi with Bluetooth enabled (e.g., Raspberry Pi 4)
- iPhone with BLE scanning app (e.g., LightBlue, nRF Connect)
- Dependencies installed via `pip`

```bash
pip install bleak
