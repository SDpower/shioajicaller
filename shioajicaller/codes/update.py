# -*- coding: utf-8 -*-
#
# TSE 上市證券
# OTC 上櫃證券
# Future 期貨

import os
import redis
import csv,json
from json import JSONEncoder
from collections import namedtuple
from shioajicaller.caller import Caller

StockROW = namedtuple('Stock', [
                        'exchange',
                        'code',
                        'symbol',
                        'name',
                        'category',
                        'currency',
                        'unit',
                        'limit_up',
                        'limit_down',
                        'reference',
                        'update_date',
                        'day_trade'])

FutureRow = namedtuple('Future', [
                        'code',
                        'symbol',
                        'name',
                        'category',
                        'delivery_month',
                        'underlying_kind',
                        'underlying_code',
                        'unit',
                        'limit_up',
                        'limit_down',
                        'reference',
                        'update_date'])

OptionRow = namedtuple('Option', [
                'code',
                'symbol',
                'name',
                'category',
                'delivery_month',
                'strike_price',
                'option_right',
                'underlying_kind',
                'limit_up',
                'limit_down',
                'update_date'])

def to_csv(result,path):
    if (len(result) > 0):
        with open(path, 'w', newline='', encoding='utf_8') as csvfile:
            writer = csv.writer(csvfile,
                                delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(result[0]._fields)
            for r in result:
                writer.writerow([_ for _ in r])

def toFutureRowData(result,data):
    if (data != None):
        for item in data:
            if item["underlying_code"]:
                underlying_code = item["underlying_code"]
            else:
                underlying_code = ""
            result.append(FutureRow(
                item["code"],
                item["symbol"],
                item["name"],
                item["category"],
                item["delivery_month"],
                item["underlying_kind"],
                underlying_code,
                item["unit"],
                item["limit_up"],
                item["limit_down"],
                item["reference"],
                item["update_date"]))

def toOptionRowData(result,data):
    if (data != None):
        for item in data:
            result.append(OptionRow(
                item["code"],
                item["symbol"],
                item["name"],
                item["category"],
                item["delivery_month"],
                item["strike_price"],
                item["option_right"],
                item["underlying_kind"],
                item["limit_up"],
                item["limit_down"],
                item["update_date"]))

def toStockRowData(result,data):
    if (data != None):
        for item in data:
            result.append(StockROW(
                item["exchange"],
                item["code"],
                item["symbol"],
                item["name"],
                item["category"],
                item["currency"],
                item["unit"],
                item["limit_up"],
                item["limit_down"],
                item["reference"],
                item["update_date"],
                item["day_trade"]))

class EmployeeEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def clear_redis(redisHost: str,redisPort: int,redisDb: str,prefix = 'stock'):
    rServer= redis.StrictRedis(redisHost,redisPort,redisDb)
    for key in rServer.scan_iter(f"{prefix}:*"):
        rServer.delete(key)

def to_redis(results,redisHost: str,redisPort: int,redisDb: str,prefix = 'stock'):
    if (results == None):
        return
    rServer= redis.StrictRedis(redisHost,redisPort,redisDb)
    for item in results:
        if prefix != "stock":
            key = f'{prefix}:{item.category}:{item.code}'
        else:
            key = f'{prefix}:{item.exchange}:{item.code}'
        jstr = json.dumps(item,cls=EmployeeEncoder)
        setObj = json.loads(jstr)
        rServer.hset(key,mapping=setObj)
        if prefix == "stock" and item.category !="00" and item.category !="":
            key = f'{prefix}:{item.category}:{item.exchange}:{item.code}'
            rServer.hset(key,mapping=setObj)

def __update_codes_redis(callers: Caller,redisHost: str,redisPort: int,redisDb: str):
    callers.Login()
    TSEdata = callers.getContractsStocks("TSE")
    OTCdata = callers.getContractsStocks("OTC")
    if TSEdata != None and OTCdata != None :
        clear_redis(redisHost,redisPort,redisDb)
        to_redis(TSEdata, redisHost,redisPort,redisDb)
        to_redis(OTCdata, redisHost,redisPort,redisDb)
    Futures = callers.getContractsFutures()
    if Futures != None :
        clear_redis(redisHost,redisPort,redisDb,prefix='futures')
        for Fitems in Futures:
            to_redis(Fitems, redisHost,redisPort,redisDb,prefix='futures')
    Options = callers.getContractsOptions()
    if Options != None :
        clear_redis(redisHost,redisPort,redisDb,prefix='options')
        for Oitems in Options:
            to_redis(Oitems, redisHost,redisPort,redisDb,prefix='options')


def __update_codes(callers: Caller):
    callers.Login()
    resultStock=[]
    TSEdata = callers.getContractsStocks("TSE")
    OTCdata = callers.getContractsStocks("OTC")
    toStockRowData(resultStock,TSEdata)
    toStockRowData(resultStock,OTCdata)
    to_csv(resultStock, 'StockTWSE.csv')

    resultFutures=[]
    Futures = callers.getContractsFutures()
    if Futures != None :
        for Fitems in Futures:
            toFutureRowData(resultFutures,Fitems)
        to_csv(resultFutures, 'Futures.csv')
    resultOptions=[]
    Options = callers.getContractsOptions()
    if Options != None :
        for Oitems in Options:
            toOptionRowData(resultOptions,Oitems)
        to_csv(resultOptions, 'Options.csv')


if __name__ == '__main__':
    callers=Caller()
    __update_codes(callers)