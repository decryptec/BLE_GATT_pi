import argparse
import asyncio
import signal
from typing import List, Dict
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

# A global event to signal shutdown
shutdown_event = asyncio.Event()

async def graceful_shutdown(sig: signal.Signals, loop: asyncio.AbstractEventLoop):
    """Sets the shutdown event and cancels running tasks."""
    print(f"\nReceived exit signal {sig.name}, shutting down...")
    shutdown_event.set()
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    if loop.is_running():
        loop.stop()

async def select_device(verbose: bool) -> BLEDevice:
    """Scans for devices and prompts the user to select one."""
    print("Scanning for devices...")
    devices = await BleakScanner.discover(timeout=5.0)
    
    # Filter for devices with a name and create a numbered list
    named_devices: List[BLEDevice] = [d for d in devices if d.name]
    if not named_devices:
        print("No named devices found. Try again or check BLE device visibility.")
        return None

    print("Please select a device:")
    for i, device in enumerate(named_devices):
        print(f"  {i}: {device.name} ({device.address})")
        if verbose:
            print(f"     Details: {device.details}")

    while not shutdown_event.is_set():
        try:
            # Use asyncio.to_thread to run blocking 'input' without blocking the event loop
            selection = await asyncio.to_thread(input, "Enter number, 's' to scan again, or 'q' to quit: ")
            if selection.lower() == 'q':
                return None
            if selection.lower() == 's':
                return await select_device(verbose) # Recursive call to rescan
            
            device_index = int(selection)
            if 0 <= device_index < len(named_devices):
                return named_devices[device_index]
            else:
                print("Invalid number, please try again.")
        except ValueError:
            print("Invalid input, please enter a number.")
        except asyncio.CancelledError:
            break # Exit if the task is cancelled

    return None

async def explore_and_interact(device: BLEDevice, verbose: bool):
    """Connects to a device and provides a menu for GATT interaction."""
    print(f"\nConnecting to {device.name} ({device.address})...")
    
    try:
        async with BleakClient(device) as client:
            print(f"Connected. Type 'help' for commands.")
            
            # Map characteristics to a number for easy interaction
            char_map: Dict[int, object] = {}
            current_char_index = 1
            
            for service in client.services:
                # Filter for characteristics that are readable or writable
                rw_chars = [c for c in service.characteristics if any(p in c.properties for p in ['read', 'write', 'write-without-response'])]
                if rw_chars or verbose:
                    print(f"\n[Service] {service.uuid}")
                    for char in service.characteristics:
                        props = ", ".join(char.properties)
                        print(f"  {current_char_index}: {char.uuid} ({props})")
                        char_map[current_char_index] = char
                        current_char_index += 1

            # Interaction loop
            while client.is_connected and not shutdown_event.is_set():
                cmd_input = await asyncio.to_thread(input, "> ")
                cmd, *params = cmd_input.split()

                if cmd == 'help':
                    print("Commands: read <num> | write <num> <value> | list | quit")
                    print("  <value> can be text (e.g., 'hello') or hex (e.g., '0x01af')")
                elif cmd == 'list':
                    # This could be improved to re-print the service list
                    print("Use the numbers listed above to interact with characteristics.")
                elif cmd == 'quit':
                    break
                elif cmd in ['read', 'write']:
                    try:
                        char_num = int(params[0])
                        char = char_map.get(char_num)
                        if not char:
                            print("Invalid characteristic number.")
                            continue

                        if cmd == 'read':
                            value = await client.read_gatt_char(char.uuid)
                            print(f"  Value: {value.hex()} | {value.decode(errors='ignore')}")
                        elif cmd == 'write':
                            if len(params) < 2:
                                print("Write command needs a value.")
                                continue
                            
                            val_str = params[1]
                            if val_str.startswith("0x"):
                                data_to_write = bytearray.fromhex(val_str[2:])
                            else:
                                data_to_write = val_str.encode('utf-8')
                            
                            await client.write_gatt_char(char.uuid, data_to_write)
                            print(f"  Wrote {data_to_write} to {char.uuid}")

                    except ValueError:
                        print("Invalid number.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                else:
                    print("Unknown command. Type 'help'.")

    except asyncio.CancelledError:
        print("Connection task cancelled.")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")
    
    print("Disconnected.")

async def main(args: argparse.Namespace, loop: asyncio.AbstractEventLoop):
    """Main application orchestrator."""
    while not shutdown_event.is_set():
        device = await select_device(args.verbose)
        if not device:
            break # User chose to quit
        
        await explore_and_interact(device, args.verbose)
        
        # Ask if the user wants to connect to another device
        if not shutdown_event.is_set():
            res = await asyncio.to_thread(input, "\nConnect to another device? (y/n): ")
            if res.lower() != 'y':
                break

    shutdown_event.set() # Signal all other parts to stop
    # Small delay to ensure other tasks see the event before loop stops
    await asyncio.sleep(0.1) 
    if loop.is_running():
        loop.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple, interactive BLE GATT tool.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for more details.")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(graceful_shutdown(s, loop)))

    try:
        main_task = asyncio.create_task(main(args, loop))
        loop.run_forever()
    finally:
        print("Application finished.")
        loop.close()
