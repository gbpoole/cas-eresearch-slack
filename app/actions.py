from logging import getLogger
from slackers.hooks import actions

log = getLogger(__name__)

# # Listening for the action type.
# @actions.on("block_actions")
# def handle_action(payload):
#     log.info("Action started.")
#     log.debug(payload)
# 
# # Listen for an action by it's action_id
# @actions.on("block_actions:your_action_id")
# def handle_action_by_id(payload):
#     log.info("Action started.")
#     log.debug(payload)
# 
# # Listen for an action by it's callback_id
# @actions.on("block_actions:your_callback_id")
# def handle_action_by_callback_id(payload):
#     log.info(f"Action started.")
#     log.debug(payload)
