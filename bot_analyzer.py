"""
P(ssh = down | state = ok) = 0
P(ssh = up | state = ok) = 1
"""

""" Determine the state based on the indicators """
def analyze(status):
    if not status['SSH'] and status['REASON'] == 'Not responding' and status['POWER'] == 'on':
        return 'NODE_KILLED_IPMI_ON'
    if not status['SSH'] and status['REASON'] == 'Not responding' and status['POWER'] == 'off':
        return 'NODE_KILLED_IPMI_OFF'

    if not status['SSH']:
        return 'UNKNOWN'

    # All of these are when SSH is working
    if status['REASON'] == 'Not responding':
        if len(status['USERS']):
            return 'SLURM_FAILED_USER_PROCESSES_ALIVE'
        else:
            return 'SLURM_FAILED_NO_USER_PROCESSES'
    if status['REASON'] == 'Node unexpectedly rebooted':
        return 'NODE_WORKING'
    if status['REASON'] == 'batch job complete failure' and status['OVERALL']:
        return 'NODE_WORKING'
    return 'UNKNOWN'