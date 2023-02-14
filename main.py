from mem_edit import Process
import ctypes
from typing import *
import time


pid = input("Enter the process id or name to read, use 'ps -aux' to see options for names: ")

if not pid.isnumeric():
    process_name = pid
    pid = Process.get_pid_by_name(process_name)
    while pid is None:
        print("Couldn't find pid, trying again in 10 seconds...")
        time.sleep(10)
        pid = Process.get_pid_by_name(process_name)

with Process.open_process(pid) as requested_process:
    addresses: List[int] = None
    while True:
        current_value: int = int(input("Enter current value to search: "))

        addresses = requested_process.search_all_memory(ctypes.c_int(current_value)) if not addresses else\
                    requested_process.search_addresses(addresses, ctypes.c_int(current_value))
        
        address_expression = "\n".join([hex(address) for address in addresses][:100])
        print(f"Found {len(addresses)} matches for value {current_value}:\n{address_expression}\n")

        user_input = input("Enter 'r' to reset the current search, enter 't' to track the current addresses, anything else to continue filtering: ")
        if user_input == "r":
            addresses = None
            current_value = print("Addresses were reset.")
        if user_input == "t":
            while True:
                print("\nCurrent values:")
                address_value = ctypes.c_int()
                for address in addresses:
                    requested_process.read_memory(address, address_value)
                    print(f"{hex(address)}: {address_value.value}")
                time.sleep(5)
