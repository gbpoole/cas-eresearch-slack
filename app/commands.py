from fastapi import Depends
from slackers.server import commands
from logging import getLogger
import shlex
import argparse
import app.slack
import app.coda
import app.config

log = getLogger(__name__)

class InvalidCommand(Exception):

    def __init__(self, message):
        self.message = message

# This parser subclass supports our bespoke reporting needs.  Specifically,
# it adds some members and overrides some methods so we can capture
# all the text normally written to stdout or stderr (accumulateing it for
# later reporting to the user), and stops any calls to sys.exit

class MyParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):

        # Add the following members to support our bespoke reporting
        self.success = True
        self.slack_text = None
        if 'slack_text' in kwargs.keys():
            self.slack_text = kwargs.pop('slack_text')

        super(MyParser,self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):

        self.success = False

    def error(self, message):

        self.success = False
        raise InvalidCommand(f'{message}')

    def _print_message(self, message, file=None):

        self.slack_text.append(message)

class SlackText(object):

    text: str = ""
    untouched = True

    def append(self,text: str):
        self.text+=text
        self.untouched=False

# Respond to the "/time" command
@commands.on("time")
async def handle_command(payload, slack = app.slack.get_client(app.config.get_settings()), coda = app.coda.get_client(app.config.get_settings())):

    # Define argument parser for the "/time" command
    parser_time = MyParser(description='Perform timesheet operations.')
    parser_time.prog = payload['command']
    subparsers_time = parser_time.add_subparsers(help='sub-command help', dest='selected_subcommand')
    subparser_aliases = {}
   
    # Define argument parser for the "add" subcommand 
    subparser_aliases['add'] = ["a"]
    parser_time_add = subparsers_time.add_parser("add",aliases=subparser_aliases["add"],help="Add a timesheet entry.")
    parser_time_add.add_argument('time', type=float, help='Time in weeks')
    parser_time_add.add_argument('comment', type=str, help='Entry description (use quotes)')
    
    # Define argument parser for the "report" subcommand 
    subparser_aliases['report'] = ["r"]
    parser_time_report = subparsers_time.add_parser("report",aliases=subparser_aliases['report'],help="Timesheet report.")

    # Add the text accumulator to the parsers
    slack_text = SlackText()
    for parser in [parser_time,parser_time_add,parser_time_report]:
        parser.slack_text = slack_text

    # Report the command that was submitted back to the user
    slack_text.append(f"\nYou ran: {payload['command']} {payload['text']}\n\n")

    # Remove inverted quotes which Slack inserts; makes string splitting tricky otherwise
    command_text = payload['text'].replace('“','"').replace('”','"')

    # Parse the command
    try:
        args = parser_time.parse_args(shlex.split(command_text))
    except InvalidCommand as e:
        slack_text.append(e.message)

    # Run the command if parsing was successful
    if parser_time.success:

        # ======= COMMAND LOGIC STARTS HERE ======= 
        if args.selected_subcommand == 'add' or args.selected_subcommand in subparser_aliases['add']:        
            slack_text.append(f"ADDING ENTRY WITH: {args}")
        elif args.selected_subcommand == 'report' or args.selected_subcommand in subparser_aliases['report']:        
            slack_text.append(f"REPORTING WITH: {args}")
        else:
            slack_text.append(f"ERROR: subcommand '{args.selected_subcommand}' not implemented.\n")

        # ======= COMMAND LOGIC STOPS HERE ======= 

    # Report back to user
    if not slack_text.untouched :
        slack.message(payload, slack_text.text, code=True)

    return

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
