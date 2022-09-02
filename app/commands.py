from fastapi import Depends
from slackers.server import commands
from logging import getLogger
import shlex
import argparse
import app.slack
import app.coda
import app.config
import app.error

log = getLogger(__name__)

class InvalidCommand(Exception):

    def __init__(self, message):
        self.message = message

# This parser subclass supports our bespoke reporting needs.  Specifically,
# it adds some members and overrides some methods so we can capture
# all the text normally written to stdout or stderr (accumulateing it for
# later reporting to the user), and stops any calls to sys.exit

class Parser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):

        # Add the following members to support our bespoke reporting
        self.success = True
        self.slack_text = None
        if 'slack_text' in kwargs.keys():
            self.slack_text = kwargs.pop('slack_text')

        super(Parser,self).__init__(*args, **kwargs)

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

    # Define argument parser for this command
    parser = Parser(description='Perform timesheet operations.')
    parser.prog = payload['command']
    subparsers = parser.add_subparsers(help='sub-command help', dest='selected_subcommand')
    subparser_aliases = {}
   
    # Define argument parser for the "add" subcommand 
    subparser_aliases['add'] = ["a"]
    parser_add = subparsers.add_parser("add",aliases=subparser_aliases["add"],help="Add a timesheet entry.")
    parser_add.add_argument('duration', type=float, help='Time in days')
    parser_add.add_argument('comment', type=str, help='Entry description (use quotes)')
    
    # Define argument parser for the "report" subcommand 
    subparser_aliases['report'] = ["r"]
    parser_report = subparsers.add_parser("report",aliases=subparser_aliases['report'],help="Timesheet report.")

    # Add the text accumulator to the parsers
    slack_text = SlackText()
    for parser_i in [parser,parser_add,parser_report]:
        parser_i.slack_text = slack_text

    # Report the command that was submitted back to the user
    slack_text.append(f"\nYou ran: {payload['command']} {payload['text']}\n\n")

    # Remove inverted quotes which Slack inserts; makes string splitting tricky otherwise
    command_text = payload['text'].replace('“','"').replace('”','"')

    # Parse the command
    try:
        args = parser.parse_args(shlex.split(command_text))
    except InvalidCommand as e:
        slack_text.append(e.message)

    # Run the command if parsing was successful
    if parser.success:

        slack_channel_id = payload['channel_id']
        slack_user_id = payload['user_id']

        if args.selected_subcommand == 'add' or args.selected_subcommand in subparser_aliases['add']:        

            # ======= 'add' LOGIC STARTS HERE ======= 
            try:
                # Take the Slack Channel and User IDs from the payload and convert them
                #    into a Coda project and user
                coda_project = coda.get_rows('projects',f'"Slack Channel ID":"{slack_channel_id}"')[0]
                coda_user = coda.get_rows('people',f'"Slack ID":"{slack_user_id}"')[0]

                # Formulate the data for the row to add
                data = {}
                data['Developer'] = coda_user['Name']
                data['Project ID'] = coda_project['Project ID']
                data['Duration'] = args.duration
                data['Comment'] = args.comment

                # Add row to timesheet
                coda.put_rows('timesheet',[data])

            except Exception as e:
                slack_text.append(f"ERROR: {e}")

            else:
                slack_text.append(f"{args.duration} days added to database.")
            # ======= 'add' LOGIC STOPS HERE ======= 

        elif args.selected_subcommand == 'report' or args.selected_subcommand in subparser_aliases['report']:        

            # ======= 'report' LOGIC STARTS HERE ======= 
            try:
                # Take the Slack Channel and User IDs from the payload and convert them
                #    into a Coda project and user
                coda_project = coda.get_rows('projects',f'"Slack Channel ID":"{slack_channel_id}"')[0]
            except Exception as e:
                slack_text.append(f"ERROR: {e}")
            else:
                weeks_remaining=coda_project['Weeks Remaining']
                total_weeks=coda_project['Total Weeks']
                slack_text.append(f"{weeks_remaining} (of {total_weeks}) weeks remaining in this project.")
            # ======= 'report' LOGIC STOPS HERE ======= 

        else:
            slack_text.append(f"ERROR: subcommand '{args.selected_subcommand}' not implemented.\n")

    # Report back to user
    if not slack_text.untouched :
        slack.message(payload, slack_text.text, code=True)

    return


