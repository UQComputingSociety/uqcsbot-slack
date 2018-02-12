import os
import sys
import importlib
import logging
from uqcsbot.base import UQCSBot, bot, Command

SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_VERIFICATION_TOKEN", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")


def main():
    # Import scripts
    dir_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(dir_path, 'scripts')
    for sub_file in os.listdir(scripts_dir):
        if not sub_file.endswith('.py') or sub_file == '__init__.py':
            continue
        module = f'uqcsbot.scripts.{sub_file[:-3]}'
        importlib.import_module(module)

    # Run bot
    # TODO: Make logging command-line configurable
    if '--dev' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
        bot.run_debug()
    else:
        logging.basicConfig(level=logging.INFO)
        bot.run(SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN)

if __name__ == "__main__":
    main()
