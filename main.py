from pprint import pprint
from time import time

import pygame
from transitions.core import MachineError

from ButtonMachine import ButtonMachine
from data_transfer import LASER_STRUCT_SIZE_BYTES, NUM_LASERS, AllStates, ButtonStates, ON_LINUX
from constants import ButtonState, ButtonStateRaw, GameState, Trigger
from LaserStateMachine import LaserStateMachine
from utils import say
from LaserTripper import LaserTripper


def get_button_states(button_machine):
    button_states = getattr(get_button_states, '_button_states', None)
    if not button_states:
        button_states = ButtonStates(0x7)
        setattr(get_button_states, '_button_states', button_states)

    bs = button_states.get_button_states()
    for idx, button_state in enumerate(bs):
        try:
            raw = ButtonStateRaw(button_state)
            button_machine[idx].trigger(raw.name)
        except ValueError:
            print(f'Error: bad button state {button_state}')


def get_keyboard_button_states(button_machine, get_key_func):
    # index of key is the equivalent button
    keymap = ['1', '2', '3', ' ', '\n']
    # keymap = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]

    # pygame.event.pump()
    fetched_key = get_key_func()
    if fetched_key is None:
        for m in button_machine:
            m.trigger(ButtonStateRaw.OFF.name)
        return

    # keys = pygame.key.get_pressed()
    for idx, key in enumerate(keymap):
        # print('==', idx, key, fetched_key, button_machine[idx].state)
        if fetched_key == key:
            s = ButtonStateRaw.ON
        else:
            s = ButtonStateRaw.OFF
        button_machine[idx].trigger(s.name)
        # print('==', idx, key, fetched_key, button_machine[idx].state)


import tty
import termios
import select
import sys


def main():
    maze = None
    running = True

    print('='*80)
    pygame.init()

    # TODO: YAY! I got rid of PyGame!
    # It was the non-breaking character input from a console/terminal that made it possible
    # There's still one problem, I'm not sure how to build it into a component, so it is
    # in with the main loop. Ah well, do it after I'm not pulling all nighters.
    #
    # info = pygame.display.Info()
    # w = info.current_w
    # h = info.current_h
    # print(w,h)
    # print('='*80)
    # screen = pygame.display.set_mode((300, 300))
    # screen = pygame.display.set_mode((w,h), pygame.FULLSCREEN)

    # logo = pygame.image.load('pikacha_square.png')
    # pygame.display.set_icon(logo)
    # pygame.display.set_caption("minimal program")

    # img_ready = pygame.image.load('are_you_ready__616x353.jpg')
    # screen.blit(img_ready, (50, 50))
    # pygame.display.flip()

    pygame.mixer.init()
    voice_channel = pygame.mixer.Channel(0)
    # voice_channel.set_endevent(pygame.USEREVENT)

    laser_tripper = LaserTripper(NUM_LASERS)
    als = AllStates()
    laser_tripper.calibrate(als, 2)
    input('Press return to do readings - ')
    laser_tripper.get_readings(als)
    
    print('--that is all for now')
    return 

    # Try out the state machine
    maze = LaserStateMachine(voice_channel)

    # keymap = {
    #     pygame.K_1: Trigger.PRESS_SELECT.name,
    #     pygame.K_2: Trigger.PRESS_CHANGE.name,
    #     pygame.K_3: Trigger.PRESS_WIN.name,
    #     pygame.K_SPACE: Trigger.TRIP_BEAM.name,
    #     pygame.K_RETURN: Trigger.PRESS_RESET.name,
    # }

    button_machine = [ButtonMachine() for i in range(6)]
    keyboard_button_machine = [ButtonMachine() for i in range(6)]

    # TODO: change these to not be embedde
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        def get_key():
            key = None
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)
            return key

        while running:
            if voice_channel.get_busy() and maze.state != GameState.INSTRUCTIONS:
                # Only allow buttons skipping the instructions
                continue

            if ON_LINUX:
                # TODO: this sorta exists in the loop() function, bring it here and get rid of the thread so either buttons or keyboard can work
                pass
                #get_button_states(button_machine)

            get_keyboard_button_states(keyboard_button_machine, get_key)

            trigger = None
            if keyboard_button_machine[5].state == ButtonState.DOWN or button_machine[5].state == ButtonState.DOWN:
                running = False
            elif keyboard_button_machine[0].state == ButtonState.DOWN or button_machine[0].state == ButtonState.DOWN:
                trigger = Trigger.PRESS_SELECT.name
            elif keyboard_button_machine[1].state == ButtonState.DOWN or button_machine[1].state == ButtonState.DOWN:
                trigger = Trigger.PRESS_CHANGE.name
            elif keyboard_button_machine[2].state == ButtonState.DOWN or button_machine[2].state == ButtonState.DOWN:
                trigger = Trigger.PRESS_WIN.name
            elif keyboard_button_machine[3].state == ButtonState.DOWN or button_machine[3].state == ButtonState.DOWN:
                trigger = Trigger.TRIP_BEAM.name
            elif keyboard_button_machine[4].state == ButtonState.DOWN or button_machine[4].state == ButtonState.DOWN:
                trigger = Trigger.PRESS_RESET.name
            if trigger:
                try:
                    pre_state = maze.state
                    maze.trigger(trigger)
                except MachineError as e:
                    print('Error:', e)
                    maze.play_bank_disobedience()

                print(f'Trigger: {trigger:12}  From state:  {pre_state:23}  To state: {maze.state:23}')

            # events = pygame.event.get()
            # for event in events:
            #     if event.type == pygame.USEREVENT:
            #         print('sound stopped')
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    main()