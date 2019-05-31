#!/usr/bin/env python3

#### module load python/3.6
#### need python3 cuz exception handling for ssh call

# bofhbot - An enhanced sinfo -R for lazy sys admins--aka bofh :)
# see README.rst for detailed description (and license).
# tin (at) berkeley.edu 

# future exercise can likely write this using functional approach
# for now, regular scripting style. 
# OOP can have a structure with problem node as list of objects
# and parallel ssh/ping/etc check on them 
# to speed up output

# most functions moved to bofhbot_lib so that it can be used by the botd api server -Sn 2019.0302

import asyncio
import argparse
import json
import sys

from bot_lib import check_nodes

def process_cli() :
    # https://docs.python.org/3/howto/argparse.html#id1
    parser = argparse.ArgumentParser(prog='bofhbot')
    subparsers = parser.add_subparsers(dest='subparser_name')
    check_parser = subparsers.add_parser('check')
    check_parser.add_argument('nodes', nargs='*', default=['sinfo'])
    return parser.parse_args()
# process_cli()-end 

async def main(): 
    args = process_cli()
    print(args, file=sys.stderr)
    if args.subparser_name == 'check':
        results = await check_nodes(args.nodes)
        results_json = json.dumps(results)
        return print(results_json)
    if args.subparser_name == 'list':
        return show_status(args.nodes)
# main()-end

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()