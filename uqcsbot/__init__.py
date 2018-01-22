import os
import sys
import importlib
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
    if '--dev' in sys.argv:
        bot.run_debug()
    else:
        bot.run(SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
