from mem_edit import Process
import ctypes
from typing import *
import time
import sys
from memory_reader import MemoryReader


if __name__ == "__main__":
    pid = " ".join(sys.argv[1:])
    reader: MemoryReader = None
    if not pid.isnumeric():
        reader = MemoryReader(p_name=pid)
    else:
        reader = MemoryReader(int(pid))

    while True:
        current_value = input("Enter current value to search: ")

        if current_value.startswith("0x"):
            print("Assuming memory")
            reader.addresses = [int(current_value.replace("s", ""), 16)]
            reader.buffer = (ctypes.c_char * 2).from_buffer(bytearray(2)) if "s" in current_value else ctypes.c_int()
        else:
            if current_value.isnumeric():
                print("Assuming integer")
                current_value = int(current_value)
            else:
                print("Assuming string")

            reader.filter_value(current_value)
        
        address_expression = "\n".join([hex(address) for address in reader.addresses][:15])
        print(f"Found {len(reader.addresses)} matches for value {current_value}:\n{address_expression}")

        while True:
            if len(reader.addresses) == 0:
                break

            user_input = input("\n[r] reset, [v] show current values, [Enter] continue filtering: ")
            if user_input == "r":
                reader.reset_filter()
                print("Addresses were reset.")
                break

            elif user_input == "v":
                values = reader.read_values(True)
                print()
                for i, value in enumerate(values):
                    print(f"{hex(reader.addresses[i])}: {value}\n")

            else:
                break
