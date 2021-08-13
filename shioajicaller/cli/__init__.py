#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, sys
from .. import Caller
from ..codes import __update_codes
from ..codes import __update_codes_redis
from .. import config

def update():
    parser = argparse.ArgumentParser(
        description='Update Code List')
    parser.add_argument('-u', '--user-id', nargs='+', help='Shioaji USER ID')
    parser.add_argument('-p', '--user-password', nargs='+' , help='Shioaji USER PASSWORD')
    parser.add_argument('-t', '--type', default='csv', help='output type csv or redis')
    parser.add_argument('-rh', '--redis-host', default='127.0.0.1', help='redis host')
    parser.add_argument('-rp', '--redis-port',type=int, default=6379, help='redis port')
    parser.add_argument('-rdb', '--redis-db',type=int, default=0, help='reis db')
    args = parser.parse_args(sys.argv[2:])
    print('Start to update codes')
    callers = Caller(userId= args.user_id ,userPassowrd= args.user_password)
    if (args.type == 'csv'):
        __update_codes(callers)
        pass
    elif(args.type == 'redis'):
        if config.redisHost != None:
            host = config.redisHost
        else:
            host = args.redis_host
        
        if config.redisPort != None:
            port = int(config.redisPort)
        else:
            port = int(args.redis_port)
        
        if config.redisDb != None:
            db = config.redisDb
        else:
            db = args.redis_db

        __update_codes_redis(callers,host,port,db)
        # pass
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
