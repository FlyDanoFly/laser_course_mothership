import random
from enum import Enum

import pygame
from pprint import pprint
from transitions import Machine
from transitions.core import MachineError, State

from enums import Sas, GameDifficulty, GameState, Trigger
from sound_banks import SOUNDBANKS
from utils import say



# I want Transitions to support enum like Trigger.PRESS_RESET not Trigger.PRESS_RESET.name
# From https://stackoverflow.com/a/68297055
class EnumTransitionMachine(Machine):
    def add_transition(self, trigger, *args, **kwargs):
        super().add_transition(getattr(trigger, 'name', trigger), *args, **kwargs)


class BankPlayingState(State):
    def __init__(self, bank_enum, *args, **kwargs):
        bank_name = f'{bank_enum.value}'
        super().__init__()

        
class LaserStateMachine():
    # states = ['watching', 'waiting_for_reset', 'win']

    def __init__(self, screen):
        self.screen = screen

        self.sas = Sas.CRUEL
        self.difficulty_level = GameDifficulty.EASY

        self.bank = SOUNDBANKS

        transitions = [
            # Resseting from any state: say "Reset!"
            {'trigger': Trigger.PRESS_RESET, 'source': '*', 'dest': GameState.DORMANT, 'before': 'say_reset'},

            # Transitioning into dormant: say "press the red button to start, yellow is reset"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.DORMANT, 'dest': GameState.START_CHOOSE_SAS},
            # {'trigger': Trigger.PRESS_SELECT, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"
            # {'trigger': Trigger.PRESS_WIN, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"
            # {'trigger': Trigger.TRIP_BEAM, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"

            # Transitioning into start_choose_sas: say "Select your level of sas with the blue button, when you're on the setting you want press the red button"
            # Transitory state, just play the sound and transition to "CHOOSE_SAS"

            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_SAS, 'dest': GameState.INSTRUCTIONS}, # say "choice made"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_SAS, 'dest': GameState.CHANGE_SAS, 'after': 'play_bank_selecting_sas'}, # say the next option

            # Transitioning into instructions: say "Instructions blah blah blah press red to skip blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.INSTRUCTIONS, 'dest': GameState.START_CHOOSE_DIFFICULTY}, # say "it's your funeral"

            # Transitioning into choose_mode: say "Select your level of difficulty with the blue button, when you're on the setting you want press the red button"
            # start_choose_difficulty tranisitons into choosing difficulty

            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_DIFFICULTY, 'dest': GameState.READY_TO_PLAY_GAME}, # say "mode selected"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_DIFFICULTY, 'dest': GameState.CHANGE_DIFFICULTY},# say next option

            # Transitioning into start_play_game: say "Press the red button to play!"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.READY_TO_PLAY_GAME, 'dest': GameState.PLAY_GAME},

            # Transitioning into play_game: say "Play!"
            {'trigger': Trigger.PRESS_WIN, 'source': GameState.PLAY_GAME, 'dest': GameState.WIN},
            {'trigger': Trigger.TRIP_BEAM, 'source': GameState.PLAY_GAME, 'dest': GameState.LOSE},  # say "You messed up lots! Go back and press the button or else"

            # Transitioning into win: say "You win! Amazing or you suck depending on mode!"
            # TODO: currently ignores all input and must reset to get out
            # {'trigger': Trigger.PRESS_YELLOW, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_SELECT, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_WIN, 'source': GameState.WIN, 'dest': '----'}, # say "You already won, idiot."
            # {'trigger': Trigger.TRIP_BEAM, 'source': GameState.WIN, 'dest': GameState.START_PLAY_GAME},

            # Transitioning into lose: say "You messed up lots! Go back and press the button or else"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.LOSE, 'dest': GameState.READY_TO_PLAY_GAME},
        ]

        self.machine = EnumTransitionMachine(model=self, states=GameState, transitions=transitions, initial=GameState.DORMANT)

        # Immediatly switch to the dormant state
        self.to_DORMANT()

    # Prototype for sound banks
    def __getattr__(self, name):
        play_bank_prefix = 'play_bank_'
        if name.startswith(play_bank_prefix):
            bank_name = name[len(play_bank_prefix):]
            def method(*args, **kwargs):
                print(f'{self.__class__.__name__} playing from bank {bank_name}')
                say(random.choice(self.bank[self.sas][bank_name]))
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")        

    def pay_attention(self):
        say('Wrong! Pay attention!')

    def say_reset(self):
        say('Resetting!')
        
    def on_enter_DORMANT(self):
        say('press the red button to start, yellow is reset')

    def on_enter_START_CHOOSE_SAS(self):
        say("Select your level of sas with the blue button, when you\'re on the setting you want press the red button")
        self.to_CHOOSE_SAS(self)

    def on_enter_CHANGE_SAS(self):
        if self.sas == Sas.CRUEL:
            self.sas = Sas.ENCOURAGING
        elif self.sas == Sas.ENCOURAGING:
            self.sas = Sas.CRUEL
        say(self.sas.value)
        self.to_CHOOSE_SAS()

    def on_enter_INSTRUCTIONS(self):
        say(f'You have chosen sas level: {self.sas.value}')
        self.play_bank_instructions()

    def on_enter_START_CHOOSE_DIFFICULTY(self):
        say("Select your level of difficulty with the blue button, when you're on the setting you want press the red button")
        self.to_CHOOSE_DIFFICULTY()

    def on_enter_CHANGE_DIFFICULTY(self):
        if self.difficulty_level == GameDifficulty.EASY:
            self.difficulty_level = GameDifficulty.HARD
        elif self.difficulty_level == GameDifficulty.HARD:
            self.difficulty_level = GameDifficulty.EASY
        say(self.difficulty_level.value)
        self.to_CHOOSE_DIFFICULTY()

    def on_enter_READY_TO_PLAY_GAME(self):
        say(f'You have chosen difficulty level: {self.difficulty_level.value}')
        say("You're all set, press the red button to play!")

    def on_enter_PLAY_GAME(self):
        say("Ready, set, go!")

    def on_enter_WIN(self):
        self.play_bank_win()

    def on_enter_LOSE(self):
        say("You messed up lots! Go back and press the button or else")


def main():
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

    img_ready = pygame.image.load('are_you_ready__616x353.jpg')
    screen.blit(img_ready, (50, 50))
    pygame.display.flip()



    # Try out the state machine
    maze = LaserStateMachine(screen)

    keymap = {
        pygame.K_1: Trigger.PRESS_SELECT.name,
        pygame.K_2: Trigger.PRESS_CHANGE.name,
        pygame.K_3: Trigger.PRESS_WIN.name,
        pygame.K_SPACE: Trigger.TRIP_BEAM.name,
        pygame.K_RETURN: Trigger.PRESS_RESET.name,
    }

    running = True
    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            elif event.type == pygame.KEYDOWN:
                trigger = keymap.get(event.key)
                if trigger:
                    try:
                        pre_state = maze.state
                        maze.trigger(trigger)
                    except MachineError as e:
                        print('Error:', e)
                        maze.play_bank_wrong()
                        # raise
                    print(f'Key: {pygame.key.name(event.key):5}  Trigger: {trigger:12}  From state:  {pre_state:23}  To state: {maze.state:23}')
                elif event.key == pygame.K_ESCAPE:
                    running = False

    print('done')

if __name__ == '__main__':
    main()