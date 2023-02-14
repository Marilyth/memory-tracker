from mem_edit import Process
import ctypes
from typing import *
import time
import sys


pid = " ".join(sys.argv[1:])

if not pid.isnumeric():
    process_name = pid
    pid = Process.get_pid_by_name(process_name)
    while pid is None:
        print("Couldn't find pid, trying again in 10 seconds...")
        time.sleep(10)
        pid = Process.get_pid_by_name(process_name)
else:
    pid = int(pid)

with Process.open_process(pid) as requested_process:
    addresses: List[int] = None
    while True:
        current_value = input("Enter current value to search: ")

        if current_value.startswith("0x"):
            print("Assuming memory")
            addresses = [int(current_value.replace("s", ""), 16)]
            current_value = (ctypes.c_char * 2).from_buffer(bytearray(2)) if "s" in current_value else ctypes.c_int()
        else:
            if current_value.isnumeric():
                print("Assuming integer")
                current_value = ctypes.c_int(int(current_value))
            else:
                print("Assuming string")
                b = bytearray()
                b.extend(current_value.encode("utf-8"))
                current_value = (ctypes.c_char * len(b)).from_buffer(b)

            addresses = requested_process.search_all_memory(current_value) if not addresses else\
                        requested_process.search_addresses(addresses, current_value)
        
        address_expression = "\n".join([hex(address) for address in addresses][:100])
        print(f"Found {len(addresses)} matches for value {current_value.value}:\n{address_expression}\n")

        while True:
            if len(addresses) == 0:
                break

            user_input = input("Enter 'r' to reset the current search, enter 'v' to show the value of the current addresses, enter 'a' to find addresses which point to the current matches, anything else to continue filtering: ")
            print(user_input)
            if user_input == "a":
                pointer_addresses = set()
                for address in addresses:
                    pointer_addresses.update(requested_process.search_all_memory(ctypes.c_int(address)))
                addresses = pointer_addresses

            elif user_input == "r":
                addresses = []
                print("Addresses were reset.")
                break

            elif user_input == "v":
                # Allow reading bigger strings than the initial value.
                if type(current_value).__name__.startswith("c_char_Array"):
                    b = bytearray(100000)
                    current_value = (ctypes.c_char * 100000).from_buffer(b)

                # Avoid writing same values again, in case they are big.
                string_occurrences = {}

                print("\nCurrent values:")
                for address in addresses:
                    starting_address = address

                    # Continue string to the left until null byte.
                    if type(current_value).__name__.startswith("c_char_Array"):
                        raw_value = (ctypes.c_byte * 1024)()
                        
                        while True:
                            requested_process.read_memory(starting_address - 1024, raw_value)
                            
                            terminal_position = -1
                            try:
                                terminal_position = bytes(raw_value).rindex(0)
                            except Exception:
                                pass
                            
                            if terminal_position > -1:
                                starting_address -= 1024 - terminal_position - 1
                                break
                            else:
                                starting_address -= 1024

                    requested_process.read_memory(starting_address, current_value)

                    print()
                    if current_value.value in string_occurrences:
                        print(f"{hex(address)}: same as {hex(string_occurrences[current_value.value])}")
                    else:
                        print(f"{hex(address)}: {current_value.value}")
                        string_occurrences[current_value.value] = address

            else:
                break
