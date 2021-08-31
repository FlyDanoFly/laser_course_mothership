from pprint import pprint
import struct
import time

def clear_screen():
    import os
    os.system('clear')

def clear_screen2():
    print(chr(27)+'[2j')
    print('\033c')
    print('\x1bc')
    
# MICROCONTROLLER A
#    controls 3 lasers
#    controls 4 buttons
# MICROCONTROLLER B
#    controls 12 lasers
#      1 bool - is the laser on?
#      2 bytes - analogo reading 
NUM_LASERS_BANK_A = 10
NUM_LASERS_BANK_B = 7
NUM_LASERS = NUM_LASERS_BANK_A + NUM_LASERS_BANK_B
NUM_BUTTONS = 4
STRUCT_B = '?H'  # one bool and one unsined int
BIG_STRUCT_B = '>' + NUM_LASERS * STRUCT_B

LASER_STRUCT_SIZE_BYTES = 2
BUTTON_STRUCT_SIZE_BYTES = 1
BIG_STRUCT_C = '>' + 'H' * NUM_LASERS + '?' * NUM_BUTTONS

import subprocess
completed_process = subprocess.run('uname', capture_output=True)
ON_LINUX = b'linux' in completed_process.stdout.lower()
print('='*80)
print(ON_LINUX)
print(completed_process.stdout.lower())

if ON_LINUX:
    import smbus
    import sys
    from time import sleep

    print("Configuring buttons for Linux")

    class AllStates():
        def __init__(self):
            self.bus = self.init_bus()
            self.read_errors = 0
            self.total_reads = 0
            self.data_errors = 0

        def init_bus(self, bus=0x1):
            return smbus.SMBus(bus)

        def get_from_microcontroller(self, address, num_bytes):
            self.total_reads += 1
            raw_data = []
            try:
                # import pdb ; pdb.set_trace()
                # Can only read 32 bytes at a time
                bytes_to_read = num_bytes
                while bytes_to_read > 0:
                    bytes_to_read_this_time = min(bytes_to_read, 32)
                    raw_data.extend(self.bus.read_i2c_block_data(address, 0x0, bytes_to_read_this_time))
                    bytes_to_read -= bytes_to_read_this_time
            except OSError as e:
                self.read_errors += 1
                percentage = 100.0 * self.read_errors / self.total_reads
                print(f'Error reading i2c! Errors / Total Reads / Percentage: {self.read_errors} {self.total_reads} {percentage:.2f}, exception: ', e)
                raw_data = [None] * num_bytes
            # print(raw_data)
            return raw_data
        
        def get_button_states_old(self):
            # Buttons are all on Micro 0x7
            address = 0x7
            num_bytes = NUM_BUTTONS
            try:
                raw_data = self.get_from_microcontroller(address, num_bytes)
            except OSError as e:
                print('Error at get_button_states() level!', e)
            # print(raw_data)
            return raw_data

        def get_all_data(self):
            try:
                raw_data = []

                # Get 10 lasers from the first microcontroller
                address = 0x9
                num_bytes = LASER_STRUCT_SIZE_BYTES * NUM_LASERS_BANK_A
                raw_data.extend(self.get_from_microcontroller(address, num_bytes))
                ## print('-')
                ## print(raw_data)
                # Get 7 lasers from the first microcontroller + 4 buttons
                address = 0x7
                num_bytes = LASER_STRUCT_SIZE_BYTES * NUM_LASERS_BANK_B + BUTTON_STRUCT_SIZE_BYTES * NUM_BUTTONS
                raw_data2 = self.get_from_microcontroller(address, num_bytes)
                raw_data.extend(raw_data2)
                ## print(raw_data2)
            except OSError as e:
                print('Error at get_button_states() level!', e)

            # descructify the data
            try:
                ## print('Unpacking the data')
                comingled_data = struct.unpack(BIG_STRUCT_C, bytes(raw_data))
            except TypeError as e:
                print(f'Error unpacking the data, e = ', e)
                comingled_data = [None] * (NUM_LASERS + NUM_BUTTONS)
            laser_data = comingled_data[:NUM_LASERS]
            button_data = comingled_data[NUM_LASERS:]
            return comingled_data, laser_data, button_data

    class ButtonStates():
        def __init__(self, address):
            self.bus = self.init_bus()
            self.address = address
            self.read_errors = 0
            self.total_reads = 0

        def init_bus(self, bus=0x1):
            return smbus.SMBus(bus)

        def get_from_microcontroller(self, bus, address, num_bytes):
            raw_data = [None] * num_bytes
            self.total_reads += 1
            try:
                raw_data = bus.read_i2c_block_data(address, 0x0, num_bytes)
            except OSError as e:
                self.read_errors += 1
                percentage = 100.0 * self.read_errors / self.total_reads
                print(f'Error reading i2c! Errors / Total Reads / Percentage: {self.read_errors} {self.total_reads} {percentage:.2f}, exception: ', e)
            # print(raw_data)
            return raw_data

        def get_button_states(self, num_bytes=5):
            try:
                raw_data = self.get_from_microcontroller(self.bus, self.address, num_bytes)
            except OSError as e:
                print('Error at get_button_states() level!', e)
            # print(raw_data)
            return raw_data

    def get_from_microcontroller2(bus, address):
        try:
            raw_data = bus.read_i2c_block_data(address, 0x0, 30)
        except OSError:
            print('Error!')
            
        data = struct.unpack(BIG_STRUCT_B, bytes(raw_data))
        return data

else:
    # On Mac, do a NOOP
    print("Ignoring buttons for Mac")            
    class AllStates():
        def __init__(self):
            pass

        def get_laser_readings(self):
            return [True, 0] * NUM_LASERS

    class ButtonStates():
        def __init__(self, address):
            pass

        def get_button_states(self):
            print("mac ignored")
            return [0, 0, 0, 0, 0]


def main_read_lasers_from_just_lasers():
    all_states = AllStates()
    while True:
        data = all_states.get_laser_readings()
        for i in range(NUM_LASERS):
            print(f'i={i} data={data[i*2+1]}')
        time.sleep(1)


def main_read_all():
    all_states = AllStates()
    x = 0
    while True:
        comingled_data, laser_data, button_data = all_states.get_all_data()
        print(f'x={x}')
        x += 1
        for idx, laser in enumerate(laser_data):
            print(f'i={idx} data={laser}')
        for idx, button in enumerate(button_data):
            print(f'i={idx} data={button}')
        print('----')
        time.sleep(0.1)

def main():
    if len(sys.argv) == 3:
        address = int(sys.argv[1])
        num_bytes = int(sys.argv[2])
    else:
        print('usage: command address num_bytes')
        return
 
    button_getter = ButtonStates(address)
    while True:
        data = button_getter.get_button_states(num_bytes)
        print(f'Reading from address {address}')
        print(data)
        sleep(0.01)

if __name__ == '__main__':
    main_read_all()
    # main_read_buttons()
    # main_read_lasers_from_just_lasers()