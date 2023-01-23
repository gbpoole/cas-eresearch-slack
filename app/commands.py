from fastapi import Depends
from slackers.server import commands
from logging import getLogger
import textwrap
import numpy as np
import datetime as dt
import pytz
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
        self.slack_text = None
        if 'slack_text' in kwargs.keys():
            self.slack_text = kwargs.pop('slack_text')

        super(Parser,self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):

        raise InvalidCommand(f'{message}')

    def error(self, message):

        raise InvalidCommand(f'{message}')

    def _print_message(self, message, file=None):

        self.slack_text.append(message)

class SlackText(object):

    text: str = ""
    untouched = True

    def append(self,text: str):
        if text:
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
    parser_report.add_argument('-a', '--all', action='store_true', help='Generate a report across all projects.')

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
    except (argparse.ArgumentError, InvalidCommand) as e:
        if e.message != 'None':
            slack_text.append(e.message)
    except Exception as e:
        slack_text.append(f"ERROR: {e}")

    # Run the command if parsing was successful
    else:

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
                slack_text.append(f"{args.duration} days added to project {coda_project['Project ID']}.")
            # ======= 'add' LOGIC STOPS HERE ======= 

        elif args.selected_subcommand == 'report' or args.selected_subcommand in subparser_aliases['report']:        

            # ======= 'report' LOGIC STARTS HERE ======= 
            try:
                # Take the Slack Channel and User IDs from the payload and convert them into a Coda project and user
                coda_project = coda.get_rows('projects',f'"Slack Channel ID":"{slack_channel_id}"')[0]
                project_id = coda_project['Project ID']
                coda_user = coda.get_rows('people',f'"Slack ID":"{slack_user_id}"')[0]
                dev_name = coda_user['Name']

                # Fetch timesheet entries for this project
                if args.all:
                    coda_timesheet_project = coda.get_rows('timesheet')
                else:
                    coda_timesheet_project = coda.get_rows('timesheet',f'"Project ID":"{project_id}"')

                # Set the current time and timezone
                timezone = pytz.timezone('Australia/Melbourne')
                current_time = dt.datetime.now(tz=timezone)

                # Select list items for this user
                user_entries = [entry for entry in coda_timesheet_project if entry['Developer']==dev_name]

                # Add datetime objects for sorting
                for entry in user_entries:
                    entry['datetime'] = dt.datetime.fromisoformat(entry['Entry Date']).astimezone(tz=timezone)

            except Exception as e:
                slack_text.append(f"ERROR: {e}")
            else:

                if user_entries:

                    # Print the user's timesheet entries (sort by Project first - needed if args.all - and then time)
                    comment_length = 80
                    last_entry = None
                    for i_entry,entry in enumerate(sorted(user_entries,key=lambda d: (d['Project ID'], d['datetime']))):

                        if i_entry != 0:
                            if entry['Project ID']!=last_entry['Project ID']:
                                # Print anything you want to be shown AFTER a project's entries here
                                # Report the number of business days since the last entry
                                last_entry_date = last_entry['datetime']
                                last_entry_date_fmt = last_entry_date.strftime("%d/%m/%y")
                                num_business_days = np.busday_count( last_entry_date.date(), current_time.date())
                                slack_text.append(f"\n  Last entry:      ~{num_business_days} business days ago.\n")

                                # Report resource statistics
                                weeks_allocated = coda_project['Total Weeks']
                                weeks_spent = coda_project['Days Spent']/5
                                weeks_remaining = weeks_allocated - weeks_spent
                                slack_text.append(f"  Weeks remaining: {weeks_remaining:.1f} (of {weeks_allocated:.1f})\n")
                                slack_text.append(f"\n")

                        if i_entry == 0 or entry['Project ID']!=last_entry['Project ID']:
                            # Print anything you want to be shown BEFORE a project's entries here
                            slack_text.append(f"Your timesheet report for {entry['Project ID']}:\n\n")

                        entry_date_fmt = entry['datetime'].strftime("%d/%m/%y")
                        slack_text.append(f"  {entry_date_fmt}: {textwrap.shorten(entry['Comment'], width=comment_length, placeholder='...')} [{entry['Duration']}]\n")

                        # Hold onto this entry for comparisons to the next one
                        last_entry = entry

                    # Report the number of business days since the last entry
                    last_entry_date = last_entry['datetime']
                    last_entry_date_fmt = last_entry_date.strftime("%d/%m/%y")
                    num_business_days = np.busday_count( last_entry_date.date(), current_time.date())
                    slack_text.append(f"\n  Last entry:      ~{num_business_days} business days ago.\n")

                    # Report resource statistics
                    weeks_allocated = coda_project['Total Weeks']
                    weeks_spent = coda_project['Days Spent']/5
                    weeks_remaining = weeks_allocated - weeks_spent
                    slack_text.append(f"  Weeks remaining: {weeks_remaining:.1f} (of {weeks_allocated:.1f})\n")

                else:
                    if args.all:
                        slack_text.append(f"You do not yet have any timesheet entries against this (or any other) project.")
                    else:
                        slack_text.append(f"You do not yet have any timesheet entries against this project.")

            # ======= 'report' LOGIC STOPS HERE ======= 

        else:
            slack_text.append(f"ERROR: subcommand '{args.selected_subcommand}' not implemented.\n")

    # Report back to user
    if not slack_text.untouched :
        slack.message(payload, slack_text.text, code=True)

    return

# Respond to the "/project" command
@commands.on("project")
async def handle_command(payload, slack = app.slack.get_client(app.config.get_settings()), coda = app.coda.get_client(app.config.get_settings())):

    # Define argument parser for this command
    parser = Parser(description='Perform project operations.')
    parser.prog = payload['command']
    subparsers = parser.add_subparsers(help='sub-command help', dest='selected_subcommand')
    subparser_aliases = {}
   
    # Define argument parser for the "report" subcommand 
    subparser_aliases['report'] = ["r"]
    parser_report = subparsers.add_parser("report",aliases=subparser_aliases['report'],help="Project report.")

    # Add the text accumulator to the parsers
    slack_text = SlackText()
    for parser_i in [parser,parser_report]:
        parser_i.slack_text = slack_text

    # Report the command that was submitted back to the user
    slack_text.append(f"\nYou ran: {payload['command']} {payload['text']}\n\n")

    # Remove inverted quotes which Slack inserts; makes string splitting tricky otherwise
    command_text = payload['text'].replace('“','"').replace('”','"')

    # Parse the command
    try:
        args = parser.parse_args(shlex.split(command_text))
    except (argparse.ArgumentError, InvalidCommand) as e:
        if e.message != 'None':
            slack_text.append(e.message)
    except Exception as e:
        slack_text.append(f"ERROR: {e}")

    # Run the command if parsing was successful
    else:

        slack_channel_id = payload['channel_id']
        slack_user_id = payload['user_id']

        if args.selected_subcommand == 'report' or args.selected_subcommand in subparser_aliases['report']:        

            # ======= 'report' LOGIC STARTS HERE ======= 
            try:
                # Take the Slack Channel and User IDs from the payload and convert them
                #    into a Coda project and user
                coda_user = coda.get_rows('people',f'"Slack ID":"{slack_user_id}"')[0]
                coda_project = coda.get_rows('projects',f'"Slack Channel ID":"{slack_channel_id}"')[0]
            except Exception as e:
                slack_text.append(f"ERROR: {e}")
            else:
                slack_text.append(f"Project ID:    {coda_project['Project ID']}\n\n")
                slack_text.append(f"Project Title: {coda_project['Project Title']}\n\n")

                if len(coda_project['Sci Team Lead'])>0:
                    slack_text.append(f"Sci Team Lead:     {coda_project['Sci Team Lead']}\n")
                else:
                    slack_text.append(f"Sci Team Lead:     None\n")
                #if len(coda_project['Sci Team Member'])>0:
                #    slack_text.append(f"Sci Team Members: {coda_project['Sci Team Member']}\n")
                #else:
                #    slack_text.append(f"Sci Team Members: None\n")

                slack_text.append(f"\n")
                if len(coda_project['Dev Team Lead'])>0:
                    slack_text.append(f"Dev Team Lead:     {coda_project['Dev Team Lead']}\n")
                else:
                    slack_text.append(f"Dev Team Lead:     None\n")
                if len(coda_project['Dev Team Members'])>0:
                    slack_text.append(f"Dev Team Members:  {coda_project['Dev Team Members']}\n")
                else:
                    slack_text.append(f"Dev Team Members:  None\n")

                weeks_allocated = coda_project['Total Weeks']
                weeks_spent = coda_project['Days Spent']/5
                weeks_remaining = weeks_allocated - weeks_spent

                slack_text.append(f"\n")
                slack_text.append(f"Weeks allocated:  {weeks_allocated:.1f}\n")
                slack_text.append(f"Weeks spent:      {weeks_spent:.1f}\n")
                slack_text.append(f"Weeks remaining:  {weeks_remaining:.1f}\n")

                #slack_text.append(f"\n")
                #if len(coda_project['Actions'].split(','))>0:
                #    slack_text.append(f"Actions:\n")
                #    for i_action,action in enumerate(coda_project['Actions'].split(',')):
                #        slack_text.append(f"  {i_action}) {action}\n")

                if coda_project['Milestones'] and len(coda_project['Milestones'].split(','))>0:
                    slack_text.append(f"\n")
                    slack_text.append(f"Milestones:\n")
                    for i_milestone,milestone in enumerate(coda_project['Milestones'].split(',')):
                        slack_text.append(f"  {i_milestone}) {milestone}\n")
            # ======= 'report' LOGIC STOPS HERE ======= 

        else:
            slack_text.append(f"ERROR: subcommand '{args.selected_subcommand}' not implemented.\n")

    # Report back to user
    if not slack_text.untouched :
        slack.message(payload, slack_text.text, code=True)

    return

# Respond to the "/user" command
@commands.on("user")
async def handle_command(payload, slack = app.slack.get_client(app.config.get_settings()), coda = app.coda.get_client(app.config.get_settings())):

    # Define argument parser for this command
    parser = Parser(description='Perform project operations.')
    parser.prog = payload['command']
    subparsers = parser.add_subparsers(help='sub-command help', dest='selected_subcommand')
    subparser_aliases = {}
   
    # Define argument parser for the "info" subcommand 
    subparser_aliases['info'] = ["i"]
    parser_info = subparsers.add_parser("info",aliases=subparser_aliases['info'],help="Info about user.")

    # Add the text accumulator to the parsers
    slack_text = SlackText()
    for parser_i in [parser,parser_info]:
        parser_i.slack_text = slack_text

    # Report the command that was submitted back to the user
    slack_text.append(f"\nYou ran: {payload['command']} {payload['text']}\n\n")

    # Remove inverted quotes which Slack inserts; makes string splitting tricky otherwise
    command_text = payload['text'].replace('“','"').replace('”','"')

    # Parse the command
    try:
        args = parser.parse_args(shlex.split(command_text))
    except (argparse.ArgumentError, InvalidCommand) as e:
        if e.message != 'None':
            slack_text.append(e.message)
    except Exception as e:
        slack_text.append(f"ERROR: {e}")

    # Run the command if parsing was successful
    else:

        slack_channel_id = payload['channel_id']
        slack_user_id = payload['user_id']

        if args.selected_subcommand == 'info' or args.selected_subcommand in subparser_aliases['info']:        

            # ======= 'info' LOGIC STARTS HERE ======= 
            try:
                # Take the Slack Channel and User IDs from the payload and convert them
                #    into a Coda project and user
                coda_user = coda.get_rows('people',f'"Slack ID":"{slack_user_id}"')[0]
            except Exception as e:
                slack_text.append(f"ERROR: {e}")
            else:
                slack_text.append(f"User Name: {coda_user['Name']}\n\n")
                if len(coda_user['Dev Team Lead'])>0:
                    slack_text.append(f"Dev Team Lead of:   {coda_user['Dev Team Lead']}\n")
                if len(coda_user['Dev Team Member'])>0:
                    slack_text.append(f"Dev Team Member of: {coda_user['Dev Team Member']}\n")
                if len(coda_user['Sci Team Lead'])>0:
                    slack_text.append(f"Sci Team Lead of:   {coda_user['Sci Team Lead']}\n")
                if len(coda_user['Sci Team Member'])>0:
                    slack_text.append(f"Sci Team Member of: {coda_user['Sci Team Member']}\n")

                slack_text.append(f"\n")
                if len(coda_user['Actions'].split(','))>0:
                    slack_text.append(f"Actions:\n")
                    for i_action,action in enumerate(coda_user['Actions'].split(',')):
                        slack_text.append(f"  {i_action}) {action}\n")
            # ======= 'info' LOGIC STOPS HERE ======= 

        else:
            slack_text.append(f"ERROR: subcommand '{args.selected_subcommand}' not implemented.\n")

    # Report back to user
    if not slack_text.untouched :
        slack.message(payload, slack_text.text, code=True)

    return

