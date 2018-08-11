import xmlrpc.client
import argparse
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import (loading_status, success_status,
                                         FailureException, admin_only,
                                         UsageSyntaxException)


def handle_supervisor_command(parsed_args, channel_id) -> None:
    '''
    Processes and executes the supervisor command.
    '''
    server = xmlrpc.client.Server('http://localhost:9001/RPC2')
    command_name = parsed_args.command_name
    process_name = parsed_args.process_name
    if command_name == 'start':
        server.supervisor.startProcess(process_name)
    elif command_name == 'stop':
        server.supervisor.stopProcess(process_name)
    elif command_name == 'restart':
        server.supervisor.stopProcess(process_name)
        server.supervisor.startProcess(process_name)
    elif command_name == 'info':
        process_info = server.supervisor.getProcessInfo(process_name)
        bot.post_message(channel_id, '>>>' + process_info)
    elif command_name == 'tail':
        # The first argument is the resulting log snippet.
        log_snippet = server.supervisor.tailProcessStderrLog(process_name, 0,
                                                             parsed_args.n)[0]
        # Upload log to channel as a snippet.
        bot.api.files.upload(channels=channel_id, content=log_snippet,
                             filetype='text', title=f'{process_name} log')


@bot.on_command('supervisor')
@admin_only
@loading_status
@success_status
def handle_supervisor(command: Command):
    '''
    `!supervisor (<start> | <stop> | <restart> | <info> |
    (<tail> <-n> <NUM_BYTES>)) <PROCESS_NAME>` - Command to control supervisord
    processes. Allows a user to start, stop and restart processes as well as get
    their info and log file tails.
    '''
    channel_id = command.channel_id
    command_args = command.arg.split() if command.has_arg() else []

    arg_parser = argparse.ArgumentParser()
    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()
    arg_parser.error = usage_error  # type: ignore
    sub_parsers = arg_parser.add_subparsers(dest='command_name')
    sub_parsers.add_parser('start')
    sub_parsers.add_parser('stop')
    sub_parsers.add_parser('restart')
    sub_parsers.add_parser('info')
    tail_parser = sub_parsers.add_parser('tail')
    tail_parser.add_argument('-n', default=1000, type=int)
    arg_parser.add_argument('process_name')

    parsed_args = arg_parser.parse_args(command_args)
    try:
        handle_supervisor_command(parsed_args, channel_id)
    except xmlrpc.client.Fault as e:
        error_message = f'There was an issue performing `' \
                         + f'{parsed_args.command_name}` on `' \
                         + f'{parsed_args.process_name}`. ' \
                         + f'{e.faultCode}: {e.faultString}.'
        bot.logger.error(error_message)
        bot.post_message(channel_id, error_message)
        raise FailureException
