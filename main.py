from mem_edit import Process
import ctypes
from typing import *
import time
import sys
from memory_reader import MemoryReader


def get_user_value(reader: MemoryReader, input_text: str) -> Any:
    current_value = input(input_text)

    if current_value.startswith("0x"):
        print("Assuming address")
        reader.addresses = [int(current_value.replace("s", ""), 16)]
        reader.buffer = (ctypes.c_char * 2).from_buffer(bytearray(2)) if "s" in current_value else ctypes.c_int()

        return current_value, True
    if current_value.startswith("bytes:"):
        print("Assuming byte array")

        literal_value = current_value[6:].replace(" ", "")
        current_value = bytearray()
        for i in range(0, len(literal_value), 2):
            current_value.append(int(literal_value[i:i+2], 16))
    else:
        if current_value.isnumeric():
            print("Assuming integer")
            current_value = int(current_value)
        else:
            print("Assuming string")

    return current_value, False


if __name__ == "__main__":
    pid = " ".join(sys.argv[1:])
    reader: MemoryReader = None

    if not pid.isnumeric():
        reader = MemoryReader(p_name=pid)
    else:
        reader = MemoryReader(int(pid))

    while True:
        current_value, was_address = get_user_value(reader, "Enter value to search for: ")

        if not was_address:
            reader.filter_value(current_value)
        
        address_expression = "\n".join([hex(address) for address in reader.addresses][:15])
        print(f"Found {len(reader.addresses)} matches for value {current_value}:\n{address_expression}")

        while True:
            if len(reader.addresses) == 0:
                break

            user_input = input("\n[r] reset, [v] show current values, [c] show context around values, [w] overwrite values, [Enter] continue filtering: ")
            if user_input == "r":
                reader.reset_filter()
                print("Addresses were reset.")
                break

            elif user_input == "v":
                values = reader.read_values(True)
                print()
                for i, value in enumerate(values):
                    print(f"{hex(reader.addresses[i])}: {value}\n")

            elif user_input == "c":
                context_length = int(input("Enter context length: "))

                for address in reader.addresses:
                    context = reader.get_context(address, context_length)
                    byte_array_hex = ""
                    for address in sorted(context.keys()):
                        byte = context[address]
                        byte_array_hex += format(byte.value, "02x")
                    
                    print(f"{hex(address)} +- {context_length}: {byte_array_hex}")

            elif user_input == "w":
                value, was_address = get_user_value(reader, "Enter value to write: ")

                if not was_address:
                    reader.write_values(value)
                    print("Values were written.")

            else:
                break
