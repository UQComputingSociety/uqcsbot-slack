import os
import importlib
from .base import slack_events_adapter, api, command_handler


def main():
	dir_path = os.path.dirname(__file__)
	scripts_dir = os.path.join(dir_path, 'scripts')
	for subfile in os.path.listdir(scripts_dir):
		if not subfile.endswith('.py') or subfile == '__init__.py':
			continue
		module = f'uqcsbot.scripts.{subfile[:-3]}'
		importlib.import_module(module)


	slack_events_adapter.start(port=5000)

if __name__ == "__main__":
	main()