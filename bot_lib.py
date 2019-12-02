import asyncio
import bot_checks
import os
import itertools
import time
from progress.bar import Bar

import bot_actions
import bot_analyzer

PDSH_GROUP_DIR = "/etc/pdsh/group"

try:
    GROUPS = os.listdir(PDSH_GROUP_DIR)
except:
    GROUPS = []

# checks to run using SSH
CHECKS = [
    (('SCRATCH', bot_checks.check_mount_usage('/global/scratch')), False),
    (('SOFTWARE', bot_checks.check_mount_usage('/global/software')), False),
    (('TMP', bot_checks.check_mount_usage('/tmp')), False),
    (('LOAD', bot_checks.check_load), False),
    (('UPTIME', bot_checks.check_uptime), False),
    (('USER_PROCESSES', bot_checks.check_users), False),
    (('SLURMD_LOG', bot_checks.check_slurmd_log), True)
]

PRE_SSH_CHECKS = [
    (('PING', bot_checks.check_ping), False),
    (('POWER', bot_checks.check_power_status), True),
    (('SSH', bot_checks.check_ssh), False),
    (('LAST_JOB', bot_checks.check_last_job), False)
]

async def show_partition_info():
    result = await bot_checks.run_local_command("sinfo -o '%P %A'")
    _, *partitions = [ entry.split(' ') for entry in result[0].split('\n') ]
    partitions = [ (partition, availability.split('/')) for partition, availability in partitions ]
    partitions = [ (partition, int(idle) / (int(available)  + int(idle))) for partition, (available, idle) in partitions ]
    partitions = [ str(partition) + '\t' + str(percentage * 100) + '%' for partition, percentage in partitions ]
    return '\n'.join(partitions)

async def get_sinfo_nodes():
    result = await bot_checks.run_local_command('sinfo -R -o "%n" | tail -n+2')
    return result[0].split('\n')

async def expand_groups(group):
    if group == 'sinfo':
        return await get_sinfo_nodes()
    if group in GROUPS:
        with open(os.path.join(PDSH_GROUP_DIR, group), 'r') as f:
            *contents, = f
            return [ node.strip() for node in contents ]
    return [group]

async def node_string_to_nodes(node_strings):
    nodes = set()
    for nodelist in node_strings:
        for node in nodelist.split(','):
            nodes.add(node)
    *nodes, = itertools.chain(*await asyncio.gather(*map(expand_groups, nodes)))
    return nodes

async def limit(sem, future):
    async with sem:
        return await future

async def with_progress(bar, futures):
    return [ await result for result in bar.iter(asyncio.as_completed(futures)) ]

async def check_nodes(nodes, use_sudo=True, concurrency=50):
    sinfo_df = await bot_checks.gather_sinfo()
    nodes = await node_string_to_nodes(nodes)
    checks = [ check_node(node, sinfo_df, use_sudo=use_sudo) for node in nodes ]
    sem = asyncio.Semaphore(concurrency)
    checks = [ limit(sem, check) for check in checks ]
    results = await with_progress(Bar('Checking nodes', max=len(checks)), checks)
    return { node: result for node, result in results }

def make_run_checks(checks):
    async def run_checks(node):
      return { name: await check(node) for name, check in checks }
    return run_checks

async def check_node(node, sinfo_df, use_sudo=True):
    pre_ssh_checks = [ check for check, sudo in PRE_SSH_CHECKS if not sudo or use_sudo ]
    checks = [ check for check, sudo in CHECKS if not sudo or use_sudo ]

    sinfo = await bot_checks.get_sinfo(node, sinfo_df)
    sinfo_values = { key: value[0] if len(value) else None for key, value in sinfo.to_dict(orient='list').items() }
    pre_ssh = await make_run_checks(pre_ssh_checks)(node)
    if pre_ssh['SSH']:
        result = { name: await check(node) for name, check in checks }
    else:
        result = { name: None for name, _ in checks }
    result = { **pre_ssh, **sinfo_values, **result }
    result['HOSTNAMES'] = node
    result['OVERALL'] = bot_checks.overall(result)
    result['SUGGESTION'] = bot_actions.suggest(node, bot_analyzer.analyze(result))
    return node, result
