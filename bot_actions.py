import asyncio
import bot_checks
import shlex
import yaml

from termcolor import colored
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter

from db_connector import action

POWER_CYCLE_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} chassis power cycle"
POWER_ON_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} chassis power on"
POWER_OFF_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} chassis power off"
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
    'SLURM_FAILED_NO_USER_PROCESSES': restart_slurm,
    'NODE_WORKING': slurm_resume,
    'UNKNOWN': nothing
}

def suggest(node, state):
    return SUGGESTION[state](node, state)

def display_status(status):
    return highlight(yaml.dump(status, sort_keys=True, indent=2), YamlLexer(), TerminalFormatter())

def display_suggestion(index, suggestion):
    return str(index) + ') ' + colored(';'.join([ command for command in suggestion ]), attrs=['bold'])

async def interactive_suggest(suggestions, status):
    accepted_nodes = []
    suggestions = { node: suggestion for node, suggestion in suggestions.items() if suggestion }
    print('{}/{} nodes have suggestions'.format(len(suggestions.keys()), len(status.keys())))
    for node, suggestion in suggestions.items():
        print(colored(node, 'green' if status[node]['SSH'] else 'red', attrs=['bold']))
        print(display_status(status[node]))
        choices = [ power_cycle(node, None), suggestion ]
        for index, choice in enumerate(choices):
            print(display_suggestion(index, choice)) 
        response = input(colored('Run suggestion? (#/[n]) ', 'grey', attrs=['bold']))
        try:
            index = int(response)
            if choices[index]:
                for command in choices[index]:
                    print('Running: ' + command)
                    # await bot_checks.run_local_command(command)
        except:
            print('Rejected suggestion\n')
