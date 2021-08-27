import os
import subprocess


def say(words, verbose=True):
    command, options = getattr(say, 'command', (None, None))

    # First time running, figure out which command to speak on this system
    if not command:
        result = os.system('say hello')
        if result == 0:
            command = 'say'
            options = ['-r', '300']
        else:
            result = os.system('espeak hello')
            if result == 0:
                command = 'espeak'
                options = ''
        setattr(say, 'command', (command, options))

    if verbose:
        print(f'Saying: "{words}"')

    full_command = []
    full_command.append(command)
    full_command.extend(options)
    full_command.append(words)
    subprocess.run(full_command)

