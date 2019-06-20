import asyncio
import bot_checks
import shlex

from termcolor import colored

POWER_CYCLE_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} power cycle"
POWER_ON_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} power on"
POWER_OFF_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} power off"
SLURM_RESUME_COMMAND = "sudo scontrol update node={node} state=resume"
SYSTEMCTL_DAEMON_RELOAD_COMMAND = "sudo systemctl daemon-reload && sudo systemctl start slurmd"

def ssh(node):
    def ssh_command(command):
        return 'ssh {node} {command}'.format(node=shlex.quote(node),command=shlex.quote(command))
    return ssh_command

def power_cycle(node, state):
    return [
        POWER_CYCLE_COMMAND.format(node=node)
    ]

def power_on(node, state):
    return [
        POWER_ON_COMMAND.format(node=node)
    ]

def restart_slurm(node, state):
    return [
        ssh(node)(SYSTEMCTL_DAEMON_RELOAD_COMMAND)
    ]

def slurm_resume(node, state):
    return [
        SLURM_RESUME_COMMAND.format(node=node)
    ]

def nothing(node, state):
    return []

SUGGESTION = {
    'NODE_KILLED_IPMI_ON': power_cycle,
    'NODE_KILLED_IPMI_OFF': power_on,
    'SLURM_FAILED_USER_PROCESSES_ALIVE': power_cycle,
    'SLURM_FAILED_NO_USER_PROCESS': restart_slurm,
    'NODE_WORKING': slurm_resume,
    'UNKNOWN': nothing
}

def suggest(node, state):
    return SUGGESTION[state](node, state)

def display_status(status):
    return str(status)

def display_suggestion(suggestion):
    return colored('\n'.join([ '\t' + command for command in suggestion ]), attrs=['bold'])

async def interactive_suggest(suggestions, status):
    accepted_nodes = []
    suggestions = { node: suggestion for node, suggestion in suggestions.items() if suggestion }
    print('{}/{} nodes have suggestions'.format(len(suggestions.keys()), len(status.keys())))
    for node, suggestion in suggestions.items():
        print(colored(node, 'green' if status[node]['SSH'] else 'red', attrs=['bold']), '-', display_status(status[node]))
        print(display_suggestion(suggestion))
        response = input(colored('Run suggestion? (y/[n]) ', 'grey', attrs=['bold']))
        if response == 'y':
            for command in suggestion:
                await asyncio.sleep(1) # bot_checks.run_local_command(suggestion)
            accepted_nodes.append(node)
            print('Accepted suggestion\n')
        else:
            print('Rejected suggestion\n')