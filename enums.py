from enum import Enum


class Sas(Enum):
    CRUEL = 'cruel'
    ENCOURAGING = 'encouraging'


class GameDifficulty(Enum):
    EASY = 'cowardly'
    HARD = 'doomed'


class GameState(Enum):
    TOP = 'top'
    DORMANT = 'dormant'

    START_CHOOSE_SAS = 'start_choose_sas'
    CHOOSE_SAS = 'choose_sas'
    CHANGE_SAS = 'change_sas'

    INSTRUCTIONS = 'instructions'

    START_CHOOSE_DIFFICULTY = 'start_choose_difficulty'
    CHOOSE_DIFFICULTY = 'choose_difficulty'
    CHANGE_DIFFICULTY = 'change_difficulty'

    READY_TO_PLAY_GAME = 'ready_to_play_game'
    PLAY_GAME = 'play_game'
    WIN = 'win'
    LOSE = 'lose'


class Trigger(Enum):
    # By function
    PRESS_RESET = 'press_reset'
    PRESS_SELECT = 'press_select'
    PRESS_CHANGE = 'press_change'
    PRESS_WIN = 'press_win'
    TRIP_BEAM = 'trip_beam'

    # By button color
    PRESS_YELLOW = 'press_reset'
    PRESS_BLUE = 'press_change'
    PRESS_RED = 'press_select'
    PRESS_GREEN = 'press_win'
