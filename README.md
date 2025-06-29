# Interactive BLE GATT Debug Tool

A minimalist, cross-platform Python tool for discovering, connecting to, and interacting with Bluetooth Low Energy (BLE) devices directly from your terminal. Built with [Bleak](https://github.com/hbldh/bleak), this script provides a simple command-line alternative to GUI-based BLE explorers like LightBlue or nRF Connect.

It's designed to be a simple, easy-to-read tool for any developer or hobbyist needing to debug BLE peripherals.

### Demo

```text
# --- Simulated Terminal Session ---

$ python ble_tool.py
Scanning for devices...
Please select a device:
  0: My Smart Bulb (XX:XX:XX:XX:XX:XX)
  1: Fitness Tracker (XX:XX:XX:XX:XX:XX)
Enter number, 's' to scan again, or 'q' to quit: 0

Connecting to My Smart Bulb (XX:XX:XX:XX:XX:XX)...
Connected. Type 'help' for commands.

[Service] 0000180f-0000-1000-8000-00805f9b34fb
  1: 00002a19-0000-1000-8000-00805f9b34fb (read)

[Service] 00001523-1212-efde-1523-785feabcd123
  2: 00001524-1212-efde-1523-785feabcd123 (read, write)
  3: 00001525-1212-efde-1523-785feabcd123 (write-without-response)

> read 2
  Value: 01 | 

> write 2 0x01
  Wrote bytearray(b'\x01') to 00001524-1212-efde-1523-785feabcd123

> write 3 hello
  Wrote bytearray(b'hello') to 00001525-1212-efde-1523-785feabcd123

> quit
Disconnected.
```

## Features

-   **Discover:** Scans for nearby BLE peripherals and presents them in a numbered list.
-   **Connect:** Interactively select a device from the list to connect.
-   **Explore:** Automatically lists all services and their readable/writable characteristics upon connection.
-   **Interact:** A simple command menu (`read`, `write`) to send and receive data from any characteristic.
-   **Versatile Writes:** Write data as plain text or as hex byte strings (e.g., `0x01ef`).
-   **Cross-Platform:** Works on any OS supported by Bleak (Windows, macOS, Linux).
-   **Graceful Shutdown:** Cleanly disconnects and exits on `Ctrl+C` or crashes, preventing messy tracebacks.
-   **Optional Verbosity:** Use the `--verbose` flag for more detailed device information during discovery.

## Prerequisites

-   Python 3.8+
-   A Bluetooth Low Energy (BLE) peripheral device to connect to (e.g., a fitness tracker, IoT sensor, smart bulb, Arduino/ESP32 project).

## Installation

The only dependency is `bleak`.

```bash
pip install bleak
```

## Usage

1.  **Run the Script**
    Save the code as `ble_tool.py` and run it from your terminal.

    ```bash
    python ble_tool.py
    ```
    For more detailed output during the device discovery phase, use the verbose flag:
    ```bash
    python ble_tool.py --verbose
    ```

2.  **Select a Device**
    The script will scan for 5 seconds and display a list of named devices. Enter the number corresponding to the device you wish to connect to. You can also type `s` to scan again or `q` to quit.

3.  **Interact with the Device**
    Once connected, a list of services and their interactive characteristics will be displayed. Use the command prompt to interact.

    -   `help`: Shows the list of available commands.
    -   `list`: Reminds you to use the numbers from the initial list.
    -   `read <num>`: Reads the value from the characteristic with the given number.
        -   Example: `read 2`
    -   `write <num> <value>`: Writes a value to the characteristic.
        -   For text: `write 3 hello world`
        -   For hex bytes: `write 2 0x01ff`
    -   `quit`: Disconnects from the current device and returns to the device selection menu.

## Credits

This tool is built upon the excellent [Bleak](https://github.com/hbldh/bleak) library, which does all the heavy lifting for cross-platform Bluetooth communication.
