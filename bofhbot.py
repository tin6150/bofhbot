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
from os import path
from pathlib import Path

from bot_lib import check_nodes, show_partition_info
from bot_analyzer import analyze
from bot_actions import suggest, interactive_suggest
from convert_json import show_table
from db_connector import db_storage

from pygments import highlight
from pygments.lexers import JsonLexer 
from pygments.formatters import TerminalFormatter

def process_cli() :
    # https://docs.python.org/3/howto/argparse.html#id1
    parser = argparse.ArgumentParser(prog='bofhbot')
    subparsers = parser.add_subparsers(dest='subparser_name')

    check_parser = subparsers.add_parser('check')
    check_parser.add_argument('nodes', nargs='*', default=['sinfo'])
    check_parser.add_argument('--no-sudo', dest='use_sudo', action='store_false')
    check_parser.add_argument('--concurrency', type=int)
    check_parser.set_defaults(use_sudo=True, concurrency=50)

    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.add_argument('nodes', nargs='*', default=['sinfo'])

    show_parser = subparsers.add_parser('show')

    suggest_parser = subparsers.add_parser('suggest')

    fix_parser = subparsers.add_parser('fix')
    fix_parser.add_argument('nodes', nargs='*', default=['sinfo'])

    report_parser = subparsers.add_parser('report')

    return parser.parse_args()
# process_cli()-end 

def read_stdin():
    return json.loads(''.join(sys.stdin.readlines()))

def get_analysis(node_info):
    return { node: analyze(status) for node, status in node_info.items() }

def get_suggestions(node_info):
    status = get_analysis(node_info)
    return { node: suggest(node, state) for node, state in status.items() }

async def main(): 
    args = process_cli()
    print(args, file=sys.stderr)
    if args.subparser_name == 'check':
        results = await check_nodes(args.nodes, use_sudo=args.use_sudo, concurrency=args.concurrency)
        # db_storage(results, path.join(Path.home(), 'bofhbot.db'))
        results_json = json.dumps(results, sort_keys=True, indent=2)
        if sys.stdout.isatty():
            return print(highlight(results_json, JsonLexer(), TerminalFormatter()))
        return print(results_json)
    if args.subparser_name == 'analyze':
        print(get_analysis(read_stdin()))
    if args.subparser_name == 'show':
        show_table(read_stdin())
    if args.subparser_name == 'suggest':
        print(get_suggestions(read_stdin()))
    if args.subparser_name == 'fix':
        status = await check_nodes(args.nodes)
        suggestions = get_suggestions(status)
        await interactive_suggest(suggestions, status)
    if args.subparser_name == 'list':
        return show_status(args.nodes)
    if args.subparser_name == 'report':
        return print(await show_partition_info())
# main()-end

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
