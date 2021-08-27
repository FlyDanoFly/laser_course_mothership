import os
from random import choice


SOUND_BANKS = {
    'cruel': {
        'break_beam': [
            "Thats what you get for TRYING!",
            "I mean, I expected you to be terrible, but is that seriously the best you can do?",
            "You clearly didn't understand the instructions. You're supposed to be AVOIDING the laser beams. Duh!",
            "Every time you break a beam, a puppy cries.",
            "A for effort, F- for execution.",
        ],
        'win': [
            "Buh buh buh but thats impossible! You totally cheated! Cheater! Cheater!",
            "Did I say this was hard? I could do this in my sleep! How dare you think you accomplished anything!",
            "Wipe that smile off your face. No one cares. Its not that interesting to win anyway.",
            "The LAST person beat it in half the time it took you.",
        ]
    },
    'encouraging': {
        'break_beam': [
            "Next times the charm!",
            "Try again!",
            "Mistakes help you learn!",
            "So close! You almost got it!",
        ],
        'win': [
            "Your perseverance, hard work, and amazing skill have payed off!",
            "We knew you could do it! You were clearly destined to be a winner!",
            "Victory! Youve done what many could hardly dare to dream of!",
            "Beautiful! Youve conquered the star of death! Such skill is rare.",
            "Take your place among the champions. You truly deserve to be here!",
        ]
    }
}
def say(words):
    os.system("say " + words)
a = "a"
b = "b"
while a == "a":
    sas = input("Would you like us to be cruel or encouraging?")
    while b == "b":
        if sas.lower() == "cruel":
            dos = input("Type 'b' to break a beam and 'w' to win.")
            if dos.lower() == "b":
                say(choice(SOUND_BANKS['cruel']['break_beam']))
            elif dos.lower() == "w":
                say(choice(SOUND_BANKS['cruel']['win']))
            else:
                print("Input not recognized. Please try again.")
                dos = input("Type 'b' to break a beam and 'w' to win.")
        elif sas.lower() == "encouraging":
            dos = input("Type 'b' to break a beam and 'w' to win.")
            if dos.lower() == "b":
                say(choice(SOUND_BANKS['encouraging']['break_beam']))
            elif dos.lower() == "w":
                say(choice(SOUND_BANKS['encouraging']['win']))
        else:
            print("Input not recognized. Please try again.")
            sas = input("Would you like us to be cruel or encouraging?")