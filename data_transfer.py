import struct


# MICROCONTROLLER A
#    controls 3 lasers
#    controls 4 buttons
# MICROCONTROLLER B
#    controls 12 lasers
#      1 bool - is the laser on?
#      2 bytes - analogo reading 
STRUCT_B = '?H'  # one bool and one unsined int
BIG_STRUCT_B = '>' + 10 * STRUCT_B


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
    class ButtonStates():
        def __init__(self, address):
            pass

        def get_button_states(self):
            print("mac ignored")
            return [0, 0, 0, 0, 0]

def main():
    address = 0x7
    num_bytes = 5
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
    main()