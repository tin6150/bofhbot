import asyncio
import shlex
import getpass

import pandas as pd

POWER_STATUS_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh status {node}"
POWER_CYCLE_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh cycle {node}"
POWER_ON_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh on {node}"
POWER_OFF_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh down {node}"
SLURM_RESUME_COMMAND = "sudo scontrol update node={node} state=resume"

def run_command(node, command, timeout=3.0):
    ssh_command = 'ssh {} {}'.format(shlex.quote(node), shlex.quote(command))
    return run_local_command(ssh_command, timeout=timeout)

async def run_local_command(command, timeout=3.0):
    # Reference: https://docs.python.org/3/library/asyncio-subprocess.html
    proc = await asyncio.create_subprocess_shell(
        command, 
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return stdout.decode().strip(), stderr.decode().strip()
    except asyncio.TimeoutError:
        return None, 'Timed out'

async def run_command_stdout(node, command):
    return (await run_command(node, command))[0]

def string_to_float(str):
    try:
        return float(str)
    except:
        return None

def check_mount_usage(mount):
    async def check_node(node):
        command = "df {mount} --output=target,size | grep {mount} | awk '{{ print $2 }}'".format(mount=mount)
        usage = await run_command_stdout(node, command)
        try:
            return int(usage) * (2 ** 10) if usage else None
        except:
            return None
    return check_node

async def check_power_status(node):
    command = POWER_STATUS_COMMAND.format(node=shlex.quote(node))
    output, _ = await run_local_command(command)
    return output.split('\n')[0].split(' ')[-1] if output else 'error'

async def check_users(node):
    command = 'ps -eo uname | egrep -v "^root$|^29$|^USER$|^telegraf$|^munge$|^rpc$|^chrony$|^dbus$|^{username}$" | sort | uniq'.format(username=getpass.getuser())
    result = await run_command_stdout(node, command)
    return [ val for val in result.split('\n') if val ] if result else []

async def check_load(node):
    command = "cat /proc/loadavg | awk -F' ' '{ print $3 }'"
    return string_to_float(await run_command_stdout(node, command))

async def check_uptime(node):
    command = 'cat /proc/uptime | cut -d" " -f1'
    return string_to_float(await run_command_stdout(node, command))

async def check_ssh(node):
    command = 'echo success'
    result = await run_command_stdout(node, command)
    return result == 'success'

async def gather_sinfo():
    splitColumns = lambda line: [ elem.strip() for elem in line.split('\t') ]
    command = 'sinfo -R --format="$(echo -e \'%n\t%t\t%H\t%u\t%E\')"'
    columns, *data = map(splitColumns, (await run_local_command(command))[0].split('\n'))
    return pd.DataFrame(data, columns = columns)

async def get_sinfo(node, sinfo_df):
    return sinfo_df[sinfo_df['HOSTNAMES'] == node]

DATA = {
    'KiB': (2 ** 10),
    'MiB': (2 ** 20),
    'GiB': (2 ** 30),
    'TiB': (2 ** 40),
    'PiB': (2 ** 50),
}

def overall(results):
    for k, v in results.items():
        if v == None:
            return False
    return (results['LOAD'] < 1) and (len(results['USERS']) == 0) and (results['SCRATCH'] > 1 * DATA['PiB']) and (results['SOFTWARE'] > 700 * DATA['GiB']) and (results['TMP'] > 2 * DATA['GiB'])

def hello_world(node):
    return run_command_stdout(node, 'echo hi from $(hostname)')