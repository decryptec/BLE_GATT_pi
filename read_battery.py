import asyncio
import argparse
from bleak import BleakClient, BleakScanner, BleakError

BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

async def get_address_from_name(name):
    print(f"Scanning for device named: {name}")
    devices = await BleakScanner.discover(timeout=10)
    for d in devices:
        if d.name == name:
            print(f"Found device: {d.name} @ {d.address}")
            return d.address
    print("Device not found")
    return None

async def main(address=None, name=None):
    if not address and name:
        address = await get_address_from_name(name)
        if not address:
            return

    command = ''
    while command != 'q':
        try:
            client = BleakClient(address)
            await client.connect(pair=True)
            if client.is_connected:
                try:
                    battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
                    print(f"Battery level: {int(battery_level[0])}%")
                except BleakError as e:
                    print(f"Failed to read battery level: {e}")
            else:
                print("Failed to connect to device.")
        except Exception as e:
            print(f"Connection failed: {e}")
        finally:
            try:
                await client.disconnect()
            except Exception as e:
                print(f"Disconnection error: {e}")
        command = input("Command (q to quit): ").strip().lower()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get battery level from a BLE device")
    parser.add_argument("--address", type=str, help="Bluetooth address of the device")
    parser.add_argument("--name", type=str, help="Name of the device (e.g. 'Don’s iPhone')")
    args = parser.parse_args()

    if not args.address and not args.name:
        print("Error: You must specify at least --address or --name")
    else:
        asyncio.run(main(address=args.address, name=args.name))
