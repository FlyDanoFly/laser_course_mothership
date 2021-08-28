
from transitions import Machine


# I want Transitions to support enum like Trigger.PRESS_RESET not Trigger.PRESS_RESET.name
# From https://stackoverflow.com/a/68297055
class EnumTransitionMachine(Machine):
    def add_transition(self, trigger, *args, **kwargs):
        super().add_transition(getattr(trigger, 'name', trigger), *args, **kwargs)


