#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, sys, logging
from .. import Caller
from ..codes import __update_codes
from ..codes import __update_codes_redis
from .. import config
from ..server import __start_wss_server

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)

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
    callers = Caller()
    callers.SetAccount(args.user_id ,args.user_password)
    if (args.type == 'csv'):
        print('Start to update codes to csv')
        __update_codes(callers)
    elif(args.type == 'redis'):
        print('Start to update codes to redis')
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
    print('Done!')

def websockets():
    parser = argparse.ArgumentParser(
        description='Websockets Server')
    parser.add_argument('-u', '--user-id', nargs='+', help='Shioaji USER ID')
    parser.add_argument('-p', '--user-password', nargs='+' , help='Shioaji USER PASSWORD')
    parser.add_argument('-wp', '--websockets-port',type=int, default=6789, help='Websockets port')
    parser.add_argument('-ps', '--pool-size', type=int, default=50, help='pool size')
    parser.add_argument('-wr', '--with-redis', action="store_true", help='with redis publish.')
    parser.add_argument('-rh', '--redis-host', default='127.0.0.1', help='redis host')
    parser.add_argument('-rp', '--redis-port',type=int, default=6379, help='redis port')
    parser.add_argument('-rdb', '--redis-db',type=int, default=0, help='reis db')
    parser.add_argument("-v", "--verbosity", action="count",
                    help="increase output verbosity")
    args = parser.parse_args(sys.argv[2:])
    if config.WebsocketsPort != None:
        wsport = int(config.WebsocketsPort)
    else:
        wsport = int(args.websockets_port)

    args_redis = dict()
    if (args.with_redis):
        args_redis["with_redis"]=True
        if config.redisHost != None:
            args_redis["redisHost"] = config.redisHost
        else:
            args_redis["redisHost"] = args.redis_host

        if config.redisPort != None:
            args_redis["redisPort"] = int(config.redisPort)
        else:
            args_redis["redisPort"] = int(args.redis_port)

        if config.redisDb != None:
            args_redis["redisDb"] = config.redisDb
        else:
            args_redis["redisDb"] = args.redis_db

    if args.verbosity == 1:
        debug = logging.INFO
    elif args.verbosity == 2:
        debug = logging.DEBUG
    else:
        debug = logging.WARNING

    print(f'Start Websockets Server Port:{wsport}')
    if args.user_id != None and args.user_password != None:
        callers = Caller()
        callers.SetAccount(userId= args.user_id ,userPassowrd= args.user_password)
        __start_wss_server(port=wsport, callers=callers, pool_size=args.pool_size, debug=debug, **args_redis)
    else:
        __start_wss_server(port=wsport, pool_size=args.pool_size, debug=debug, **args_redis)


def run():
    parser = argparse.ArgumentParser(
        description='Shioaji Warp Caller P.O.C project.',
        usage='''<command> [<args>]
The most commonly used git commands are:
   update         update Code List
   websockets     start a websocket server
''')
    parser.add_argument('command', help='Subcommand to run')
    try:
        args = parser.parse_args(sys.argv[1:2])
        if (args.command != None) and args.command not in globals():
            print ('Unrecognized command')
            parser.print_help()
        else:
            globals()[args.command]()
    except:
        pass
