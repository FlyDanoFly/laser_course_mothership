from EnumTransitionMachine import EnumTransitionMachine
from constants import ButtonState, ButtonStateRaw


class ButtonMachine(EnumTransitionMachine):
    transitions = [
        # {'trigger': ButtonStateRaw.NONE, 'source': ButtonState.NONE, 'dest': ButtonState.NONE},
        {'trigger': ButtonStateRaw.OFF, 'source': ButtonState.NONE, 'dest': ButtonState.OFF},
        {'trigger': ButtonStateRaw.ON, 'source': ButtonState.NONE, 'dest': ButtonState.ON},

        # {'trigger': ButtonStateRaw.NONE, 'source': ButtonState.NONE, 'dest': ButtonState.NONE},
        # {'trigger': ButtonStateRaw.OFF, 'source': ButtonState.OFF, 'dest': ButtonState.OFF},
        {'trigger': ButtonStateRaw.ON, 'source': ButtonState.OFF, 'dest': ButtonState.DOWN},

        # {'trigger': ButtonStateRaw.NONE, 'source': ButtonState.NONE, 'dest': ButtonState.NONE},
        {'trigger': ButtonStateRaw.OFF, 'source': ButtonState.DOWN, 'dest': ButtonState.UP},
        {'trigger': ButtonStateRaw.ON, 'source': ButtonState.DOWN, 'dest': ButtonState.ON},

        # {'trigger': ButtonStateRaw.NONE, 'source': ButtonState.NONE, 'dest': ButtonState.NONE},
        {'trigger': ButtonStateRaw.OFF, 'source': ButtonState.ON, 'dest': ButtonState.UP},
        # {'trigger': ButtonStateRaw.ON, 'source': ButtonState.ON, 'dest': ButtonState.ON},

        # {'trigger': ButtonStateRaw.NONE, 'source': ButtonState.NONE, 'dest': ButtonState.NONE},
        {'trigger': ButtonStateRaw.OFF, 'source': ButtonState.UP, 'dest': ButtonState.OFF},
        {'trigger': ButtonStateRaw.ON, 'source': ButtonState.UP, 'dest': ButtonState.DOWN},
    ]

    def __init__(self):
        super().__init__(self, states=ButtonState, transitions=ButtonMachine.transitions,
            ignore_invalid_triggers=True, initial=ButtonState.NONE)

