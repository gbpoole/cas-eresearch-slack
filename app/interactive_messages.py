import logging
from slackers.hooks import actions

log = logging.getLogger(__name__)

# # Listening for the action type.
# @actions.on("interactive_message")
# def handle_action(payload):
#     log.info("Action started.")
#     log.debug(payload)
# 
# # Listen for an action by it's name
# @actions.on("interactive_message:action_name")
# def handle_action_by_id(payload):
#     log.info("Action started.")
#     log.debug(payload)
# 
# # Listen for an action by it's type
# @actions.on("interactive_message:action_type")
# def handle_action_by_callback_id(payload):
#     log.info(f"Action started.")
#     log.debug(payload)
# 
# # Listen for an action by it's name and type
# @actions.on("interactive_message:action_name:action_type")
# def handle_action_by_callback_id(payload):
#     log.info(f"Action started.")
#     log.debug(payload)
