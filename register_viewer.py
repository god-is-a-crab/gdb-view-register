from cmsis_svd.parser import SVDParser
from collections import namedtuple
import gdb
import os

Peripheral = namedtuple("Peripheral", ["address_base", "registers"])
Register = namedtuple("Register", ["address_offset", "fields"])
BitField = namedtuple("BitField", ["name", "bit_offset", "bit_width", "enum_values"])
EnumValue = namedtuple("EnumValue", ["description"])

class Device:
    def __init__(self, svdpath: str):
        """Parse device SVD to generate a device instance containing information
        about peripherals, registers and fields."""

        device = SVDParser.for_xml_file(svdpath).get_device()
        self.peripherals = dict()
        for p in device.peripherals:
            registers = dict()
            peripheral = Peripheral(p.base_address, registers)

            for r in p.registers:
                fields = []
                register = Register(r.address_offset, fields)

                for f in r.fields:
                    if f.enumerated_values is not None:
                        enum_values = dict()
                        for e in f.enumerated_values:
                            enum_values[e.value] = e.description.strip()
                        fields.append(BitField(f.name, f.bit_offset, f.bit_width, enum_values))
                    else:
                        fields.append(BitField(f.name, f.bit_offset, f.bit_width, None))
                registers[r.name] = register

            self.peripherals[p.name] = peripheral

    def get_register_address(self, full_register_name: str):
        """Given a full register name like `GPDMA1.GPDMA_C1TR1`, get its address."""
        peripheral_name, register_name = full_register_name.split(".")
        peripheral = self.peripherals.get(peripheral_name)
        if peripheral is not None:
            register = peripheral.registers.get(register_name)
            if register is not None:
                return peripheral.address_base + register.address_offset

    @staticmethod
    def display_register_field(field: BitField, value):
        """Print the value of a field and its description."""
        field_mask = (1 << field.bit_width) - 1
        field_value = (value >> field.bit_offset) & field_mask
        display_string = f"{field.name:<10} (bit {field.bit_offset:<2}): {field_value:<5}"

        if field.enum_values is not None:
            description = field.enum_values[field_value]
            display_string += f"({description})"

        print(display_string)

    def view_register(self, full_register_name: str, value: int):
        """Print information about a register."""
        peripheral_name, register_name = full_register_name.split(".")
        peripheral = self.peripherals.get(peripheral_name)
        if peripheral is not None:
            register = peripheral.registers.get(register_name)
            if register is not None:
                for f in register.fields:
                    Device.display_register_field(f, value)

class ViewRegister(gdb.Command):
    """GDB plugin: view register fields."""

    def __init__(self):
        super(ViewRegister, self).__init__("view", gdb.COMMAND_DATA)
        cwd_files = os.listdir(".")
        svd_file = next((file for file in cwd_files if file.rfind(".svd") != -1), None)
        self.device = Device(svd_file)

    def invoke(self, args, from_tty):
        args = gdb.string_to_argv(args)
        if len(args) < 1:
            print("Usage: view <REGISTER_NAME> e.g. `view GPDMA1.GPDMA_C1TR1`")
            return

        register_name = args[0]
        reg_address = self.device.get_register_address(register_name)
        if reg_address is None:
            print("Invalid register name")
            return

        try:
            # Read 4 bytes from register address
            inferior = gdb.selected_inferior()
            reg_value = int.from_bytes(inferior.read_memory(reg_address, 4), byteorder='little')
        except gdb.error as e:
            print(f"Error: {str(e)}")
            return

        self.device.view_register(register_name, reg_value)

ViewRegister()
