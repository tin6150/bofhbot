import asyncio
import bot_checks
import os
import itertools
import time
from progress.bar import Bar

PDSH_GROUP_DIR = "/etc/pdsh/group"

GROUPS = os.listdir(PDSH_GROUP_DIR)

# checks to run using SSH
CHECKS = [
    ('SCRATCH', bot_checks.check_mount_usage('/global/scratch')),
    ('SOFTWARE', bot_checks.check_mount_usage('/global/software')),
    ('TMP', bot_checks.check_mount_usage('/tmp')),
    ('LOAD', bot_checks.check_load),
    ('UPTIME', bot_checks.check_uptime),
    ('USERS', bot_checks.check_users)
]

async def get_sinfo_nodes():
    result = await bot_checks.run_local_command('sinfo -R -o "%n" | tail -n+2')
    return result[0].split('\n')

async def expand_groups(group):
    if group == 'sinfo':
        return await get_sinfo_nodes()
    if group in GROUPS:
        *contents, = open(os.path.join(PDSH_GROUP_DIR, group), 'r')
        return [ node.strip() for node in contents ]
    return [group]

async def with_progress(bar, futures):
    return [ await result for result in bar.iter(asyncio.as_completed(futures)) ]

async def check_nodes(nodes):
    sinfo_df = await bot_checks.gather_sinfo()
    *nodes, = itertools.chain(*await asyncio.gather(*map(expand_groups, nodes)))
    checks = [ check_node(node, sinfo_df) for node in nodes ]
    results = await with_progress(Bar('Checking nodes', max=len(checks)), checks)
    return { node: result for node, result in results }

async def check_node(node, sinfo_df):
    sinfo = await bot_checks.get_sinfo(node, sinfo_df)
    power_status = await bot_checks.check_power_status(node)
    ssh_up = await bot_checks.check_ssh(node)
    if ssh_up:
        result = { name: await check(node) for name, check in CHECKS }
    else:
        result = { name: None for name, _ in CHECKS }
    sinfo_values = { key: value[0] if len(value) else None for key, value in sinfo.to_dict(orient='list').items() }
    result = { 'SSH': ssh_up, 'POWER': power_status, **sinfo_values, **result }
    result['OVERALL'] = bot_checks.overall(result)
    return node, result