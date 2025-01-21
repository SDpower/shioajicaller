# -*- coding: utf-8 -*-
#
# TSE 上市證券
# OTC 上櫃證券
# Future 期貨
# Option 選擇權
# Indexs 指數

import os,sys,time
import redis
import orjson
import csv
from collections import namedtuple
from shioajicaller.caller import Caller

IndexsROW = namedtuple('Indexs', [
                        'exchange',
                        'code',
                        'symbol',
                        'name'])

StockROW = namedtuple('Stock', [
                        'exchange',
                        'code',
                        'symbol',
                        'name',
                        'category',
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

def FutureRowData(item):
    underlying_code = ""
    try:
        underlying_code = item["underlying_code"]
    except:
        pass

    update_date = ""
    try:
        update_date = item["update_date"]
    except:
        pass
    
    limit_up = ''
    try:
        limit_up = item["limit_up"]
    except:
        pass

    limit_down = ''
    try:
        limit_down = item["limit_down"]
    except:
        pass

    try:
        reference = item["reference"] if "reference" in item else ""
        return FutureRow(
            item["code"],
            item["symbol"],
            item["name"],
            item["category"],
            item["delivery_month"],
            item["underlying_kind"],
            underlying_code,
            item["unit"],
            limit_up,
            limit_down,
            reference,
            update_date)
    except Exception as ex:
        print(f'AppendtoFutureRowData error:{ex}')

def toFutureRowData(result,data):
    if (data != None):
        for item in data:
            retData = FutureRowData(item)
            if retData != None:
                result.append(retData)

def OptionRowData(item):
    return OptionRow(
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
        item["update_date"])
    
def toOptionRowData(result,data):
    if (data != None):
        for item in data:
            result.append(OptionRowData(item))

def StockRowData(item):
    try:
        return StockROW(
            item["exchange"],
            item["code"],
            item["symbol"],
            item["name"],
            item["category"],
            item["unit"],
            item["limit_up"],
            item["limit_down"],
            item["reference"],
            item["update_date"],
            item["day_trade"])
    except:
        return StockROW(
            item["exchange"],
            item["code"],
            item["symbol"],
            item["name"],
            item["category"],
            item["unit"],
            item["limit_up"],
            item["limit_down"],
            item["reference"],
            item["update_date"],
            'No')

def toStockRowData(result,data):
    if (data != None):
        for item in data:
            result.append(StockRowData(item))

def IndexRowData(item):
    return IndexsROW(
        item["exchange"],
        item["code"],
        item["symbol"],
        item["name"],
    )

def toIndexRowData(result,data):
    if (data != None):
        for Contract in data:
            result.append(IndexRowData(Contract))

def clear_redis(redisHost: str,redisPort: int,redisDb: str,prefix: str='Stocks'):
    rServer= redis.StrictRedis(redisHost,redisPort,redisDb)
    for key in rServer.scan_iter(f"{prefix}:*"):
        rServer.delete(key)

def to_redis(results,redisHost: str,redisPort: int,redisDb: str,prefix: str='Stocks'):
    if (results == None):
        return
    rServer= redis.StrictRedis(redisHost,redisPort,redisDb)    
    for item in results:
        try:
            key=""
            if prefix[-6:] == "Indexs":
                key = f'{prefix}:{item.exchange}:{item.code}'
            elif prefix[-6:] != "Stocks":
                key = f'{prefix}:{item.category}:{item.code}'
            else:
                key = f'{prefix}:{item.exchange}:{item.code}'

            jstr = orjson.dumps(item._asdict(), default=lambda obj: obj.__dict__, option=orjson.OPT_NAIVE_UTC)
            setObj = orjson.loads(jstr)
            rServer.hset(key,mapping=setObj)
            if prefix[-6:] == "Stocks" and item.category !="00" and item.category !="":
                key = f'{prefix}:{item.category}:{item.exchange}:{item.code}'
                rServer.hset(key,mapping=setObj)
        except Exception as ex:
            print(f'error to_redis {ex}')

def __update_codes_redis(callers: Caller,redisHost: str,redisPort: int,redisDb: str,prefix: str=""):
    callers.Login()

    resultIndexs= []
    IndexsDataTSE = callers.Contracts(type="Indexs",code="TSE")
    IndexsDataOTC = callers.Contracts(type="Indexs",code="OTC")
    toIndexRowData(resultIndexs,IndexsDataTSE)
    toIndexRowData(resultIndexs,IndexsDataOTC)
    if len(resultIndexs) > 0:
        clear_redis(redisHost,redisPort,redisDb,prefix=f"{prefix}Indexs")
        to_redis(resultIndexs, redisHost,redisPort,redisDb,prefix=f"{prefix}Indexs")

    resultStock=[]
    TSEdata = callers.getContractsStocks("TSE")
    OTCdata = callers.getContractsStocks("OTC")
    toStockRowData(resultStock,TSEdata)
    toStockRowData(resultStock,OTCdata)
    if len(resultStock) > 0:
        clear_redis(redisHost,redisPort,redisDb,prefix=f"{prefix}Stocks")
        to_redis(resultStock, redisHost,redisPort,redisDb,prefix=f"{prefix}Stocks")
    
    resultFutures=[]
    Futures = callers.getContractsFutures()
    if Futures != None :
        clear_redis(redisHost,redisPort,redisDb,prefix=f"{prefix}Futures")
        for Fitems in Futures:
            toFutureRowData(resultFutures,Fitems)
        to_redis(resultFutures, redisHost,redisPort,redisDb,prefix=f"{prefix}Futures")
    
    resultOptions=[]
    Options = callers.getContractsOptions()
    if Options != None :
        clear_redis(redisHost,redisPort,redisDb,prefix=f"{prefix}Options")
        for Oitems in Options:
            toOptionRowData(resultOptions,Oitems)
        to_redis(resultOptions, redisHost,redisPort,redisDb,prefix=f"{prefix}Options")
    print("Update done.")


def __update_codes(callers: Caller):
    callers.Login()
    resultIndexs=[]
    IndexsDataTSE = callers.Contracts(type="Indexs",code="TSE")
    IndexsDataOTC = callers.Contracts(type="Indexs",code="OTC")
    toIndexRowData(resultIndexs,IndexsDataTSE)
    toIndexRowData(resultIndexs,IndexsDataOTC)
    to_csv(resultIndexs, 'IndexsTWSE.csv')
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
    print("Update done.")


if __name__ == '__main__':
    callers=Caller()
    __update_codes(callers)