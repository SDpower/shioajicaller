#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, sys, os
from shioajicaller import Caller
from shioajicaller.codes import __update_codes

def update():
    parser = argparse.ArgumentParser(
        description='Update Code List')
    parser.add_argument('-u', '--user-id', nargs='+', help='Shioaji USER ID')
    parser.add_argument('-p', '--user-password', nargs='+' , help='Shioaji USER PASSWORD')
    parser.add_argument('-t', '--type', action='store_true', help='output type only csv now')
    args = parser.parse_args(sys.argv[2:])
    print('Start to update codes')
    callers = Caller(userId= args.user_id ,userPassowrd= args.user_password)
    __update_codes(callers)
    print('Done!')

def run():
    parser = argparse.ArgumentParser(
        description='Shioaji Warp Caller P.O.C project.',
        usage='''<command> [<args>]
The most commonly used git commands are:
   update     update Code List
''')
    parser.add_argument('command', help='Subcommand to run')
    args = parser.parse_args(sys.argv[1:2])
    if not hasattr(locals(), args.command):
        print ('Unrecognized command')
        parser.print_help()
        sys.exit(70)
    globals()[args.command]()
