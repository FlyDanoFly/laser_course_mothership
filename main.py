import struct
import serial
from tkinter import *
import time
import threading
import sys
import pygame


SOUND_LOOP_FILENAME = '397787__sieuamthanh__alarm-0.wav'
#SOUND_LOOP_FILENAME = '16445__kkz__redub.wav'
LASER_OPEN = '#0f0'
LASER_BLOCKED = '#f00'
LASER_INIT = '#aaa'

#SERIAL_BAUD_RATE = 9600
SERIAL_BAUD_RATE = 115200

# Binary structure:
#    1 byte: 0xff - record separator
#    4 byte: bit stream for laser switch state, 0 = no laser, 1 = laser
STRUCT = '5B'

class BitMask:
    def __init__(self, number_of_bits, starting_value=0x0):
        self.number_of_bits = number_of_bits
        self.bitmask = starting_value
    
    def get(self, bit_index):
        return self.bitmask & (1 << bit_index)

    def get_normalized(self, bit_index):
        return (self.bitmask >> bit_index) & 1

    def set(self, bit_index):
        self.bitmask |= (1 << bit_index)

    def set_all(self, value):
        self.bitmask = value

    def toggle(self, bit_index):
        self.bitmask ^= (1 << bit_index)

    def clear(self, bit_index):
        self.bitmask &= ~(1 << bit_index)

    def clear_all(self, bit_index):
        self.bitmask = 0


def thread_fun4(laser_labels, stop_event):
    s = serial.Serial(port=sys.argv[1], baudrate=SERIAL_BAUD_RATE)
    packet = struct.Struct('<BL')
    struct_separator = struct.Struct('<B')
    nt = time.time() + 1
    lazer_switches = BitMask(4)

    pygame.mixer.init()
    sound = pygame.mixer.Sound(SOUND_LOOP_FILENAME)
    channel = pygame.mixer.find_channel()
    channel = sound.play(-1)
    channel.pause()
    is_playing = False

    num_updates = 0
    num_secs = 0
    while not stop_event.is_set():
        num_updates += 1
        separator, packet2 = packet.unpack(s.read(5))
        if separator != 0xff:
            print('Invalid separator, resyncing...')
            while separator != 0xff:
                separator = struct_separator.unpack(s.read(1))[0]
                print('    received: {}'.format(hex(separator)))
            s.read(4)
            print('    ...resyncing complete')
            continue

        lazer_switches.set_all(packet2)

        if lazer_switches.get(0):
            channel.pause()
            color = LASER_OPEN
        else:
            channel.unpause()
            color = LASER_BLOCKED
        if color != laser_labels[0][1]:
            laser_labels[0][0].config(background=color)
            laser_labels[0][1] = color

        t = time.time()
        if t > nt:
            num_secs += 1
            print(f'num_updates={num_updates} updates/sec={int(num_updates/num_secs)}', '0x{:032b}'.format(packet2), packet2, hex(packet2), lazer_switches.get_normalized(9))
            nt = t + 1
            
def main():
    #Define the tkinter instance
    win= Tk()

    #Define the size of the tkinter frame
    win.geometry("700x500")

    laser_labels = [
        [Label(win, text=f'Laser {d}', width=95, height=5, background=LASER_INIT), LASER_INIT]
        for d in range(10)]

    for laser_label in laser_labels:
        laser_label[0].pack(pady=5)

    label= Label(win)
    label.pack(pady=20)
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=thread_fun4, args=(laser_labels, stop_event))
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        win.mainloop()
    except KeyboardInterrupt:
        pass
    print('stopping event...')
    stop_event.set()
    monitor_thread.join()

if __name__ == '__main__':
    main()