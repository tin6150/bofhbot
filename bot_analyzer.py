from bot_lib import check_nodes

STATES = {
    'NODE_KILLED_IPMI_ON': 1,
    'NODE_KILLED_IPMI_OFF': 2,
    'SLURM_FAILED': 3,
    'NODE_WORKING': 4,
    'UNKNOWN': 5,
}

"""
P(ssh = down | state = ok) = 0
P(ssh = up | state = ok) = 1
"""

""" Determine the state based on the indicators """
def analyze(status):
    if not status['SSH'] and status['REASON'] == 'Not responding' and status['POWER'] == 'on':
        return STATES['NODE_KILLED_IPMI_ON']
    if not status['SSH'] and status['REASON'] == 'Not responding' and status['POWER'] == 'off':
        return STATES['NODE_KILLED_IPMI_OFF']

    if not status['SSH']:
        return STATES['UNKNOWN']

    # All of these are when SSH is working
    if status['REASON'] == 'Not responding':
        return STATES['SLURM_FAILED']
    if status['REASON'] == 'Node unexpectedly rebooted':
        return STATES['NODE_WORKING']
    if status['REASON'] == 'batch job complete failure' and status['OVERALL']:
        return STATES['NODE_WORKING']
    return STATES['UNKNOWN']