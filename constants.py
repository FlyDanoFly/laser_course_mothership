from enum import Enum

DEFAULT_SOUND_BANK_NAME = '__default'

class Sas(Enum):
    CRUEL = 'cruel'
    ENCOURAGING = 'encouraging'


class GameDifficulty(Enum):
    EASY = 'cowardly'
    HARD = 'doomed'


class GameState(Enum):
    TOP = 'top'
    # DORMANT = 'dormant'
    INTRODUCTION = 'introduction'

    START_CHOOSE_SAS = 'start_choose_sas'
    CHOOSE_SAS = 'choose_sas'
    CHANGE_SAS = 'change_sas'
    CHOSE_SAS = 'chose_sas'

    INSTRUCTIONS = 'instructions'
    SKIP_INSTRUCTIONS = 'skip_instructions'

    START_CHOOSE_DIFFICULTY = 'start_choose_difficulty'
    CHOOSE_EASY = 'choose_easy'
    CHOOSE_HARD = 'choose_hard'
    CHOSE_EASY = 'chose_easy'
    CHOSE_HARD = 'chose_hard'
    # TODO: Remove these
    CHOOSE_DIFFICULTY = 'choose_difficulty'
    CHANGE_DIFFICULTY = 'change_difficulty'

    READY_TO_PLAY_GAME = 'ready_to_play_game'
    PLAY_GAME = 'play_game'
    WIN = 'win'
    TRIP_LASER = 'trip_laser'


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


class ButtonStateRaw(Enum):
    NONE = None
    OFF = 0
    ON = 1


class ButtonState(Enum):
    NONE = None  # not inited
    OFF = 0      # not pressed
    DOWN = 1     # transition from not pressed to pressed
    ON = 2       # button pressed
    UP = 3       # transition from pressed to not_pressed

