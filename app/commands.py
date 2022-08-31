from fastapi import Depends
from slackers.server import commands
from logging import getLogger
import argparse
import app.slack
import app.coda
import app.config

log = getLogger(__name__)

class InvalidCommand(Exception):

    def __init__(self, message):
        self.message = message

class MyParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):

        self.slack = kwargs.pop('slack')
        self.payload = kwargs.pop('payload')
        super(MyParser,self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):

        pass

    def error(self, message):

        raise InvalidCommand(f'{message}')

    def _print_message(self, message, file=None):

        self.slack.message(self.payload, message)


@commands.on("time")  # responds to "/time"  
async def handle_command(payload, slack = app.slack.get_client(app.config.get_settings()), coda = app.coda.get_client(app.config.get_settings())):

    parser = MyParser(prog=payload['command'],description='Perform timesheet operations.', slack=slack, payload=payload)
    parser.add_argument('--foo')

    # First, keep ArgParser from exiting on invalid input
    #parser.exit = parser_exit

    try:
        args = parser.parse_args(payload['text'].split())
    except InvalidCommand as e:
        slack.message(payload, e.message)

    return

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
