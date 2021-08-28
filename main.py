from pprint import pprint
import threading

import pygame
from transitions.core import MachineError

from ButtonMachine import ButtonMachine
from data_transfer import ButtonStates
from constants import ButtonState, ButtonStateRaw, Trigger
from LaserStateMachine import LaserStateMachine


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


def get_keyboard_button_states(button_machine):
    # index of key is the equivalent button
    keymap = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]

    pygame.event.pump()
    keys = pygame.key.get_pressed()
    for idx, key in enumerate(keymap):
        raw = ButtonStateRaw(keys[key])
        button_machine[idx].trigger(raw.name)


def main():
    maze = None
    running = True

    print('='*80)
    pygame.init()
    info = pygame.display.Info()
    w = info.current_w
    h = info.current_h
    print(w,h)
    print('='*80)
    screen = pygame.display.set_mode((300, 300))
    # screen = pygame.display.set_mode((w,h), pygame.FULLSCREEN)

    logo = pygame.image.load('pikacha_square.png')
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # img_ready = pygame.image.load('are_you_ready__616x353.jpg')
    # screen.blit(img_ready, (50, 50))
    # pygame.display.flip()

    # Try out the state machine
    maze = LaserStateMachine()

    keymap = {
        pygame.K_1: Trigger.PRESS_SELECT.name,
        pygame.K_2: Trigger.PRESS_CHANGE.name,
        pygame.K_3: Trigger.PRESS_WIN.name,
        pygame.K_SPACE: Trigger.TRIP_BEAM.name,
        pygame.K_RETURN: Trigger.PRESS_RESET.name,
    }

    from data_transfer import ON_LINUX
    if False: #ON_LINUX:
        print('This is on linux, starting the thread to monitor buttons')
        x = threading.Thread(target=loop)
        x.start()

    button_machine = [ButtonMachine() for i in range(6)]
    keyboard_button_machine = [ButtonMachine() for i in range(6)]

    while running:
        if ON_LINUX:
            # TODO: this sorta exists in the loop() function, bring it here and get rid of the thread so either buttons or keyboard can work
            get_button_states(button_machine)

        get_keyboard_button_states(keyboard_button_machine)

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

if __name__ == '__main__':
    main()