import random
from time import sleep

from transitions import State
import pygame

from constants import DEFAULT_SOUND_BANK_NAME, GameDifficulty, GameState, Trigger
from sound_banks import get_default_sound_bank, get_sound_banks
from EnumTransitionMachine import EnumTransitionMachine
from utils import say


class BankPlayingState(State):
    def __init__(self, bank_enum, *args, **kwargs):
        bank_name = f'{bank_enum.value}'
        super().__init__(bank_enum, *args, **kwargs)

    def enter(self, data):
        data.model.play_bank(self.name.lower())
        super().enter(data)


class LaserStateMachine():
    def __init__(self):
        self.difficulty_level = GameDifficulty.EASY

        self.bank = get_sound_banks()
        self.bank_names = list(self.bank.keys())
        print(self.bank_names)

        self.default_bank = get_default_sound_bank()
        self.selected_bank_name = DEFAULT_SOUND_BANK_NAME
        self.selected_bank = self.default_bank

        transitions = [
            # Resseting from any state: say "Reset!"
            {'trigger': Trigger.PRESS_RESET, 'source': '*', 'dest': GameState.INTRODUCTION, 'before': 'say_reset'},

            # Transitioning into dormant: say "press the red button to start, yellow is reset"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.INTRODUCTION, 'dest': GameState.START_CHOOSE_SAS},
            # {'trigger': Trigger.PRESS_SELECT, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"
            # {'trigger': Trigger.PRESS_WIN, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"
            # {'trigger': Trigger.TRIP_BEAM, 'source': GameState.DORMANT, 'dest': GameState.DORMANT},  # say "pay attention"

            # Transitioning into start_choose_sas: say "Select your level of sas with the blue button, when you're on the setting you want press the red button"
            # Transitory state, just play the sound and transition to "CHOOSE_SAS"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.START_CHOOSE_SAS, 'dest': GameState.CHANGE_SAS}, # say "choice made"

            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_SAS, 'dest': GameState.CHOSE_SAS}, # say "choice made"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_SAS, 'dest': GameState.CHANGE_SAS},# 'before': 'play_bank_selecting_sas'}, # say the next option

            # Transitioning into choose_mode: say "Select your level of difficulty with the blue button, when you're on the setting you want press the red button"
            # start_choose_difficulty tranisitons into choosing difficulty

            # Transitioning into instructions: say "Instructions blah blah blah press red to skip blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.INSTRUCTIONS, 'dest': GameState.START_CHOOSE_DIFFICULTY}, # say "it's your funeral"

            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.START_CHOOSE_DIFFICULTY, 'dest': GameState.CHOOSE_EASY}, # say "it's your funeral"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_EASY, 'dest': GameState.CHOOSE_HARD}, # say "it's your funeral"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_EASY, 'dest': GameState.CHOSE_EASY, 'after': 'to_READY_TO_PLAY_GAME'}, # say "it's your funeral"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_HARD, 'dest': GameState.CHOOSE_EASY}, # say "it's your funeral"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_HARD, 'dest': GameState.CHOSE_HARD, 'after': 'to_READY_TO_PLAY_GAME'}, # say "it's your funeral"

            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.CHOOSE_DIFFICULTY, 'dest': GameState.READY_TO_PLAY_GAME}, # say "mode selected"
            {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.CHOOSE_DIFFICULTY, 'dest': GameState.CHANGE_DIFFICULTY},# say next option

            # Transitioning into start_play_game: say "Press the red button to play!"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.READY_TO_PLAY_GAME, 'dest': GameState.PLAY_GAME},

            # Transitioning into play_game: say "Play!"
            {'trigger': Trigger.PRESS_WIN, 'source': GameState.PLAY_GAME, 'dest': GameState.WIN},
            {'trigger': Trigger.TRIP_BEAM, 'source': GameState.PLAY_GAME, 'dest': GameState.TRIP_LASER},  # say "You messed up lots! Go back and press the button or else"

            # Transitioning into win: say "You win! Amazing or you suck depending on mode!"
            # TODO: currently ignores all input and must reset to get out
            # {'trigger': Trigger.PRESS_YELLOW, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_CHANGE, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_SELECT, 'source': GameState.WIN, 'dest': GameState.DORMANT},
            # {'trigger': Trigger.PRESS_WIN, 'source': GameState.WIN, 'dest': '----'}, # say "You already won, idiot."
            # {'trigger': Trigger.TRIP_BEAM, 'source': GameState.WIN, 'dest': GameState.START_PLAY_GAME},

            # Transitioning into lose: say "You messed up lots! Go back and press the button or else"
            {'trigger': Trigger.PRESS_SELECT, 'source': GameState.TRIP_LASER, 'dest': GameState.PLAY_GAME},
        ]

        processed_states = []
        for state in GameState:
            if True:
                s = BankPlayingState(state)
            else:
                if state in {GameState.CHOOSE_SAS, GameState.START_CHOOSE_SAS, GameState.CHOSE_SAS, GameState.INSTRUCTIONS,
                        GameState.INTRODUCTION}:
                    s = BankPlayingState(state)
                else:
                    s = state
            processed_states.append(s)
        print(processed_states)
        self.machine = EnumTransitionMachine(model=self, states=processed_states, transitions=transitions, initial=GameState.TOP)

        # Immediatly switch to the dormant state
        self.to_INTRODUCTION()

    # Prototype for sound banks
    def __getattr__(self, name):
        play_bank_prefix = 'play_bank_'
        if name.startswith(play_bank_prefix):
            bank_name = name[len(play_bank_prefix):]
            def method(*args, **kwargs):
                # print(f'{self.__class__.__name__} playing from bank {bank_name}')
                # say(random.choice(self.selected_bank[bank_name]))
                self.play_bank(bank_name)
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")        

    def play_bank(self, bank_name):
        print(f'{self.__class__.__name__} playing from bank {bank_name}')
        s = None
        b = self.selected_bank.get(bank_name)
        if b:
            s = random.choice(self.selected_bank[bank_name])

        else:
            # Try the fallback
            print('Trying default!')
            b = self.default_bank.get(bank_name)
            if b:
                s = random.choice(self.default_bank[bank_name])

        if s:
            s.play()
            # TODO: institute an actual callback, looks like it'll have to be sending an event and then catching the enevnt and doing something
            # Wait for the sound to finish playing before proceeding
            while pygame.mixer.get_busy():
                pass

    def say_reset(self):
        say('Resetting!')
        
    def on_enter_CHANGE_SAS(self):
        if self.selected_bank == self.default_bank:
            self.selected_bank_name = self.bank_names[0]
        else:
            self.selected_bank_name = self.bank_names[(self.bank_names.index(self.selected_bank_name) + 1) % len(self.bank_names)]
        self.selected_bank = self.bank[self.selected_bank_name]
        # say(self.selected_bank_name)
        self.to_CHOOSE_SAS()

    def on_enter_CHOSE_SAS(self):
        self.to_INSTRUCTIONS()

    # def on_enter_INSTRUCTIONS(self):
    #     say(f'You have chosen sas level: {self.selected_bank_name}')
    #     self.play_bank_instructions()

    # def on_enter_START_CHOOSE_DIFFICULTY(self):
    #     say("Select your level of difficulty with the blue button, when you're on the setting you want press the red button")
    #     self.to_CHOOSE_DIFFICULTY()

    def on_enter_CHANGE_DIFFICULTY(self):
        if self.difficulty_level == GameDifficulty.EASY:
            self.difficulty_level = GameDifficulty.HARD
        elif self.difficulty_level == GameDifficulty.HARD:
            self.difficulty_level = GameDifficulty.EASY
        say(self.difficulty_level.value)
        self.to_CHOOSE_DIFFICULTY()

    # def on_enter_READY_TO_PLAY_GAME(self):
    #     say(f'You have chosen difficulty level: {self.difficulty_level.value}')
    #     say("You're all set, press the red button to play!")

    # def on_enter_PLAY_GAME(self):
    #     say("Ready, set, go!")

    # def on_enter_WIN(self):
    #     self.play_bank_win()

    # def on_enter_LOSE(self):
    #     say("You messed up lots! Go back and press the button or else")
