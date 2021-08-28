from itertools import chain
import os
from pprint import pprint
import subprocess
import sys
import time

import pygame

from constants import GameState, DEFAULT_SOUND_BANK_NAME


# TODO: remove this when all banks comply with standard
ONLY_DO_THESE_BANK_NAMES = {'Computer'}


def list_visible_files(path, ignore_starting_underscores=False):
    ignored_prefixes = {'.'}
    if ignore_starting_underscores:
        ignored_prefixes.add('_')
    return [d for d in os.listdir(path) if not d[0] in ignored_prefixes]


def _get_dynamic_sound_bank(root_directory, bank_name, ignore_starting_underscores=False, verbose=False):
    valid_section_names = [x.value for x in GameState]
    
    sound_bank = {}
    base_path = os.path.join(root_directory, bank_name)
    for section_name in list_visible_files(base_path, ignore_starting_underscores=ignore_starting_underscores):
        if verbose:
            print(f'    Found section {section_name}')
        if section_name not in valid_section_names:
            if verbose:
                print(f'        Not a valid section name, skipping')
                continue
        sound_bank[section_name] = []
        path = os.path.join(base_path, section_name)
        for sound_filename in list_visible_files(path, ignore_starting_underscores):
            if verbose:
                print(f'        Found filename {sound_filename}')
            if not sound_filename.endswith('.ogg'):
                if verbose:
                    print(f'            Not an OGG file, skipping')
                    continue
            s = pygame.mixer.Sound(os.path.join(root_directory, bank_name, section_name, sound_filename))
            sound_bank[section_name].append(s)

    return sound_bank


def _get_dynamic_sound_banks(root_directory, bank_names, ignore_starting_underscores=True, verbose=False):
    pygame.mixer.init()
    sound_bank = {}
    for bank_name in list_visible_files(root_directory, ignore_starting_underscores):
        if verbose:
            print(f'Found bank {bank_name}')
        sound_bank[bank_name] = _get_dynamic_sound_bank(root_directory, bank_name, verbose=verbose)
    return sound_bank


def get_sound_banks(root_directory='sound_banks', verbose=False):
    bank_names = list_visible_files(root_directory, ignore_starting_underscores=True)

    # TODO: for now only use a subset of banks, then remove this when all banks comply
    bank_names_processed = []
    for bank_name in bank_names:
        if verbose:
            print(f'Found bank {bank_name}')
        if ONLY_DO_THESE_BANK_NAMES and bank_name not in ONLY_DO_THESE_BANK_NAMES:
            if verbose:
                print(f'    Bank not allowed, skipping')
            continue
        bank_names_processed.append(bank_name)
    bank_names = bank_names_processed
    # TODO: end remove this section

    sound_banks = {}
    for bank_name in bank_names:
        sound_banks[bank_name] = _get_dynamic_sound_bank(root_directory, bank_name, verbose=verbose)

    return sound_banks


def get_default_sound_bank(root_directory='sound_banks', verbose=False):
    return _get_dynamic_sound_bank(root_directory, DEFAULT_SOUND_BANK_NAME, verbose=verbose)


NEW_DEFAULT_BANK_STATES = {
    'introduction': [
        "Do you want to play a game? Then press the red button!"
    ],
    'start_choose_sas': [
        "Default: Choose your level of sas with the red button, select with the blue button",
    ],
    'choose_sas': [
        "Robotic. I only state facts emotionlessly.",
    ],
    'chose_sas': [
        'You have chosen Robotic mode.',
    ],
    # DEFAULT! Same for all banks
    'instructions': [
        "Default instructions:",
        # " Press the green buttons without tripping the lasers or touching the fence. If you trip "
        # "a laser return to the beginning and press the red button. Press the red button now to continue.",
    ],
    'skip_instructions': [
        "Instructions skipped"
    ],
    'start_choose_difficulty': [
        "Choose easy mode or hard mode."
    ],
    'choose_easy': ["Easy mode."],
    'choose_hard': ["Hard mode."],
    'chose_easy': ["You have chosen easy mode."],
    'chose_hard': ["You have chosen hard mode."],
    'ready_to_play_game': ["You're all set, press the red button to play!"],
    'play_game': ["You may start Optical Course."],
    'win': ["You have won."],
    'trip_laser': ["You have tripped a laser. Go back to start and press the red button."],
    'disobedience': ["Do not push that button right now."],

    # Old world:
    'Idle': ["Continue."],
    'Win again': ["You have already won."],
}

def build_empty_bank(bank_name, prefill=False, directory='.'):
    for state_name, prefill_phrases in NEW_DEFAULT_BANK_STATES.items():
        path = os.path.join(directory, bank_name, state_name)
        print(f'Making path: {path}')
        os.makedirs(path)
        if prefill:
            for idx, prefill_phrase in enumerate(prefill_phrases):
                path = os.path.join(path, f'{idx}.wav')
                print(f'Making sound: {path}')
                subprocess.run(['say', '--rate=300', '--voice=Samantha', '--data-format=LEI32@22050', f'--output-file={path}', prefill_phrase])

def main():
    def print_usage():
        print('usage examples:')
        print('    command list')
        print('    command build bank_name [directory]')

    if len(sys.argv) < 2:
        print_usage()
        return
    elif sys.argv[1] not in {'list', 'build'}:
        print_usage()
        return

    if sys.argv[1] == 'list':
        import pygame
        pygame.mixer.init()

        print('** Doing default sound bank')
        default_sound_bank = get_default_sound_bank('sound_banks', verbose=True)
        pprint(default_sound_bank)
        
        print('** Doing sound banks')
        sound_banks = get_sound_banks('sound_banks', verbose=True)
        pprint(sound_banks)

        # for bank_name, bank in [('default', default_sound_bank), ('Computer', sound_bank['Computer'])]:
        # # for bank_name, bank in     :
        for bank_name, bank in chain((('default', default_sound_bank),), sound_banks.items()):
            print(f'Bank: {bank_name}')
            for section_name, sounds in bank.items():
                print(f'    Section: {section_name}')
                for idx, sound in enumerate(sounds):
                    print(f'        Playing sound {idx}...')
                    sound.play()
                    time.sleep(0.5)
                    sound.fadeout(200)

        print('end')
    elif sys.argv[1] == 'build':
        bank_name = sys.argv[2]
        directory = '.'
        if len(sys.argv) == 4:
            directory = sys.argv[3]
        build_empty_bank(bank_name, prefill=True, directory=directory)


if __name__ == '__main__':
    main()

SOUNDBANKS = {
    'Cruel': {
        # DEFAULT! Same for all banks
        'start_choose_sas': [
            "Default: Choose your level of sas with the red button, select with the blue button",
        ],
        'choose_sas': [
            "Cruel mode: You can't handle this level of sas, choose the other",
            "Cruel mode: I don't like you, this is going to be fun",
            "Cruel mode: You're sure you want to cry?",
        ],
        'chose_sas': [
            "Bad choice. You’ll regret it.",
            "You chose me and I’m stuck with you now? Ugh, you’re the worst...",
            "Sometimes I find it hard to insult people. Given who I’m working with, this is not one of those times.",
        ],
        # DEFAULT! Same for all banks
        'instructions': [
            "Default instructions: Press the green buttons without tripping the lasers or touching the fence. If you trip "
            "a laser return to the beginning and press the red button. Press the red button now to continue.",
        ],
        # -- Start specialized bank --
        'skip_instructions': [
            "Okay! I’m sure you’ll figure it out, you’re a natural!",
            "You can skip the instructions, you got this!",
            "I’ll bet you’ve been here before!",
            "You don’t need those instructions, you’ve got The Force on your side!",
            "I completely agree with your decision. Instructions are boring.",
        ],
        'wrong': [
            "Really? Reeaaallly?",
            "Don't touch that!",
            "Wrong!",
            "Hey you, pay attention!",
            "Stop touching that!",
        ],
        'win': [
            "You won using WAAY too much beginner's luck",
            "I don't want to say you won, let's say you didn't lose",
            "I didn't expect you to win",
            "You obviously got help to finish the course properly",
        ],
    },
    'Encouraging': {
        # DEFAULT! Same for all banks
        'start_choose_sas': [
            "Default: Choose your level of sas with the red button, select with the blue button",
        ],
        'start_choose_sas': [
            "Encouraging mode: Choose your level of sas with the red button, select with the blue button",
        ],
        'choose_sas': [
            "Encouraging mode: I can't wait to cheer you on!",
            "Encouraging mode: I'm gonna help you be a star!",
            "Encouraging mode: You're good enough and smart enough. You got this!",
        ],
        'chose_sas': [
            "Yay! We’ll be besties!",
            "Yay! Together to victory!",
            "Yay! Yay! Yay!",
        ],
        # DEFAULT! Same for all banks
        'instructions': [
            "Default instructions: Press the green buttons without tripping the lasers or touching the fence. If you trip "
            "a laser return to the beginning and press the red button. Press the red button now to continue.",
        ],
        'skip_instructions': [
            'It’s your funeral...',
            'You’re giving up my valuable advice? How ungrateful.',
            'The instructions bore me too. Although, to be fair, I doubt you understood what pushing that button meant',
            'Yeah skip the instructions. You’re doomed, nothing will change that.',
            'Skipping the instructions? Just this one time I was going to tell you the trick to win it all. Alas...',
        ],
        'wrong': [
            "You can't do that right now",
            "Bear with me, we're almost there",
            "We're not doing that right now",
            "Can you hold off on playing with the buttons?",
        ],
        'win': [
            "Yay! You win!",
            "You win! I'm so proud of you",
            "That was the most fabulous win today"
        ]
    },
}