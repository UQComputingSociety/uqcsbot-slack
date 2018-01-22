import os
import sys
import importlib
from uqcsbot.base import slack_events_adapter, bot, command_handler
from uqcsbot.stub import ClientStub

def main():
    dir_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(dir_path, 'scripts')
    for sub_file in os.listdir(scripts_dir):
        if not sub_file.endswith('.py') or sub_file == '__init__.py':
            continue
        module = f'uqcsbot.scripts.{sub_file[:-3]}'
        importlib.import_module(module)

    if '--dev' in sys.argv:
        stub = ClientStub(command_handler)
        bot.client = stub
        stub.adapter.prompt()
    else:
        slack_events_adapter.start(port=5000)

if __name__ == "__main__":
    main()
