import asyncio
import re
import shlex
import getpass
from functools import lru_cache

import pandas as pd

POWER_STATUS_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.sh {node} chassis power status"

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

async def run_command_stdout(node, command, timeout=3.0):
    return (await run_command(node, command, timeout=timeout))[0]

def string_to_float(str):
    try:
        return float(str)
    except:
        return None

async def check_ping(node):
    command = 'ping -c1 {} | sed -n 2p | awk \'{{ print $NF }}\''.format(shlex.quote(node))
    result, _ = await run_local_command(command)
    return result == 'ms'

def check_mount_usage(mount):
    async def check_node(node):
        command = "df {mount} --output=target,size | grep {mount} | awk '{{ print $2 }}'".format(mount=mount)
        usage = await run_command_stdout(node, command)
        try:
            return int(usage) * (2 ** 10) if usage else None
        except:
            return None
    return check_node

# JobId=4497298 UserId=jianlicheng(43988) GroupId=ucb(501) Name=knl_launcher JobState=COMPLETED Partition=savio2_knl TimeLimit=2880 StartTime=2019-06-19T09:31:56 EndTime=2019-06-19T09:32:03 NodeList=n0281.savio2 NodeCnt=1 ProcCnt=64 WorkDir=/clusterfs/cloudcuckoo/jianli/block_2019-06-17-16-19-29-023806/launcher_2019-06-19-16-31-49-043372 ReservationName= Gres= Account=co_lsdi QOS=lsdi_knl2_normal WcKey= Cluster=brc SubmitTime=2019-06-19T09:31:49 EligibleTime=2019-06-19T09:31:49 DerivedExitCode=0:0 ExitCode=0:0
async def check_last_job(node):
    command = 'tac /var/log/slurm/jobcomp.log | grep {} | head -n1'.format(shlex.quote(node))
    result, _ = await run_local_command(command)
    if result:
        result_dict = { data_pair.split('=')[0]: data_pair.split('=')[1] for data_pair in result.split(' ') }
        keys = ['JobId', 'UserId', 'Account', 'JobState']
        return { key: result_dict[key] for key in result_dict.keys() if key in keys }

async def check_slurmd_log(node):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]') # https://stackoverflow.com/a/14693789/8706910
    command = 'sudo cat /var/log/slurm/slurmd.log | grep -i \'error\\|signal\' | tail -n10 && sudo cat /var/log/slurm/slurmd.log | tail -n1'
    result = await run_command_stdout(node, command)
    return ansi_escape.sub('', result) if result else None

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
    return (results['LOAD'] != None and results['LOAD'] < 1) and (results['USER_PROCESSES'] != None and len(results['USER_PROCESSES']) == 0) and (results['SCRATCH'] != None and results['SCRATCH'] > 1 * DATA['PiB']) and (results['SOFTWARE'] != None and results['SOFTWARE'] > 700 * DATA['GiB']) and (results['TMP'] != None and results['TMP'] > 2 * DATA['GiB'])

def hello_world(node):
    return run_command_stdout(node, 'echo hi from $(hostname)')
