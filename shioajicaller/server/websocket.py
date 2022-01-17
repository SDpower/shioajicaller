# -*- coding: utf-8 -*-
import asyncio
import aioredis
import sys, base64
import logging
import ujson
import time
import websockets
from gmqtt import Client as MQTTClient
import uvloop
from ..caller import Caller
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

STOP = asyncio.Event()
ClientS = set()
loop = asyncio.get_event_loop()
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
class WebsocketsHandler():
    def SetCallers(self,callers:Caller):
        self._callers = callers
        self._cmdQueue = asyncio.Queue()
        self._eventQueue = asyncio.Queue()
        self._oderQueue = asyncio.Queue()
        self._tradeQueue = asyncio.Queue()
        self._subscribeStocksTickQueue = asyncio.Queue()
        self._subscribeFuturesTickQueue = asyncio.Queue()
        self._subscribeStocksBidaskQueue = asyncio.Queue()
        self._subscribeFuturesBidaskQueue = asyncio.Queue()
        self._subscribeClientS = set()

        self._callers.SetEnevtCallBack(self.EnevtCallBack)
        self._callers.SetSubscribeStocksTickCallBack(self.SubscribeStocksTickCallBack)
        self._callers.SetSubscribeFuturesTickCallBack(self.SubscribeFuturesTickCallBack)
        self._callers.SetSubscribeStocksBidaskCallBack(self.SubscribeStocksBidaskCallBack)
        self._callers.SetSubscribeFuturesBidaskCallBack(self.SubscribeFuturesBidaskCallBack)
        self._callers.SetTradeCallBack(self.TradeCallBack)
        self._callers.SetOrderCallBack(self.OrderCallBack)

    def _on_connect(self, client, flags, rc, properties):
        logging.info('Mqtt Connected')

    def _on_message(self, client, topic, payload, qos, properties):
        logging.debug('RECV MSG:', payload)

    def _on_disconnect(self, client, packet, exc=None):
        logging.warning('Mqtt Disconnected')

    def _on_subscribe(self, client, mid, qos, properties):
        logging.info('Mqtt subscribed')

    async def SetMqttConnection(self,mqttHost: str,mqttUser: str,mqttPassword: str):
        _timestamp =round(time.time() * 1000)
        self._mqttClient = MQTTClient(f"shioajiCaller-{_timestamp}", receive_maximum=24000, session_expiry_interval=60)
        self._mqttClient.on_connect = self._on_connect
        self._mqttClient.on_message = self._on_message
        self._mqttClient.on_disconnect = self._on_disconnect
        self._mqttClient.on_subscribe = self._on_subscribe

        logging.info(f"SetMqttConnection! {mqttHost} {mqttUser} {mqttPassword}")

        self._mqttClient.set_auth_credentials(mqttUser, mqttPassword)
        await self._mqttClient.connect(mqttHost, keepalive=30)
        await STOP.wait()
        await self._mqttClient.disconnect()

    def SetRedisConnection(self,redisHost: str,redisPort: int,redisDb: str):
        self._redis = aioredis.Redis(
            host=redisHost,
            port=redisPort,
            db=redisDb,
            encoding="utf-8",
            decode_responses=True,
            socket_keepalive=True,
        )
        logging.info(f"SetRedisConnections! {redisHost}:{redisPort}:{redisDb}")

    def OrderCallBack(self,*args):
        loop.call_soon_threadsafe(self._oderQueue.put_nowait, args)

    def TradeCallBack(self,**keyword_params):
        loop.call_soon_threadsafe(self._tradeQueue.put_nowait, keyword_params)

    def EnevtCallBack(self,item):
        loop.call_soon_threadsafe(self._eventQueue.put_nowait, item)

    def SubscribeStocksTickCallBack(self,item):
        loop.call_soon_threadsafe(self._subscribeStocksTickQueue.put_nowait, item)

    def SubscribeFuturesTickCallBack(self,item):
        loop.call_soon_threadsafe(self._subscribeFuturesTickQueue.put_nowait, item)

    def SubscribeStocksBidaskCallBack(self,item):
        loop.call_soon_threadsafe(self._subscribeStocksBidaskQueue.put_nowait, item)

    def SubscribeFuturesBidaskCallBack(self,item):
        loop.call_soon_threadsafe(self._subscribeFuturesBidaskQueue.put_nowait, item)

    async def CmdWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._cmdQueue.get()
            logging.debug(f'CmdWorker<< {Item["cmd"]}')
            ret = {"type": "response"}
            websocket = Item["wsclient"]
            CmdDefault = ujson.dumps({"type": "respose", "result": f'Not supported'})
            try:
                if 'params' in Item.keys():
                    ret["result"] = getattr(self._callers, f'{Item["cmd"]}', lambda: CmdDefault)(**Item["params"])
                else:
                    ret["result"] = getattr(self._callers, f'{Item["cmd"]}', lambda: CmdDefault)()
            except AttributeError:
                pass

            await websocket.send(ujson.dumps(ret, default=str, ensure_ascii=False))
            counter += 1
            self._cmdQueue.task_done()

    async def OrderWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._oderQueue.get()
            ret = {"type":"OderEvent","ret":Item}
            strMsg = ujson.dumps(ret, default=str)
            logging.debug(f'OderEvent<< {strMsg}')
            websockets.broadcast(ClientS, strMsg)
            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish("shioaji.order", PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/order'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            counter += 1
            self._oderQueue.task_done()

    async def TradeWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._tradeQueue.get()
            ret = {"type":"TradeEvent","ret":Item}
            strMsg = ujson.dumps(ret, default=str)
            logging.debug(f'TradeEvent<< {strMsg}')
            websockets.broadcast(ClientS, strMsg)
            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish("shioaji.trade", PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/trade'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            counter += 1
            self._tradeQueue.task_done()

    async def EnevtWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._eventQueue.get()
            ret = {"type":"SystemEvent","ret":Item}
            strMsg = ujson.dumps(ret, default=str)
            logging.debug(f'EnevtWorker<< {strMsg}')
            websockets.broadcast(ClientS, strMsg)
            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish("shioaji.system", PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/system'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            counter += 1
            self._eventQueue.task_done()

    async def SubscribeStocksBidaskWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._subscribeStocksBidaskQueue.get()
            if len(self._subscribeClientS)>0:
                ret = {"type":"StocksBidaskEvent","ret":Item}
                strMsg = ujson.dumps(ret, default=str)
                websockets.broadcast(self._subscribeClientS, strMsg)

            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish(f'shioaji.stocks.bidask.{Item["code"]}', PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/stocks/bidask/{Item["code"]}'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            logging.debug(f'SubscribeStocksBidaskWorker<< {Item}')
            counter += 1
            self._subscribeStocksBidaskQueue.task_done()

    async def SubscribeFuturesBidaskWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._subscribeFuturesBidaskQueue.get()
            if len(self._subscribeClientS)>0:
                ret = {"type":"FuturesBidaskEvent","ret":Item}
                strMsg = ujson.dumps(ret, default=str)
                websockets.broadcast(self._subscribeClientS, strMsg)
            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish(f'shioaji.futures.bidask.{Item["code"]}', PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/futures/bidask/{Item["code"]}'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            logging.debug(f'SubscribeFuturesBidaskWorker<< {Item}')
            counter += 1
            self._subscribeFuturesBidaskQueue.task_done()

    async def SubscribeStocksTickWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._subscribeStocksTickQueue.get()
            if len(self._subscribeClientS)>0:
                ret = {"type":"StocksTickEvent","ret":Item}
                strMsg = ujson.dumps(ret, default=str)
                websockets.broadcast(self._subscribeClientS, strMsg)

            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish(f'shioaji.stocks.tick.{Item["code"]}', PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/stocks/tick/{Item["code"]}'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            logging.debug(f'SubscribeStocksTickWorker<< {Item}')
            counter += 1
            self._subscribeStocksTickQueue.task_done()

    async def SubscribeFuturesTickWorker(self,name):
        counter = 0
        logging.info(f'{name} start!')
        while True:
            Item = await self._subscribeFuturesTickQueue.get()
            if len(self._subscribeClientS)>0:
                ret = {"type":"FuturesTickEvent","ret":Item}
                strMsg = ujson.dumps(ret, default=str)
                websockets.broadcast(self._subscribeClientS, strMsg)
            if hasattr(self,"_redis") or hasattr(self,"_mqttClient"):
                PstrMsg = ujson.dumps(Item, default=str)
                if hasattr(self,"_redis"):
                    logging.debug(f'Redis publish >> {PstrMsg}')
                    await self._redis.publish(f'shioaji.futures.tick.{Item["code"]}', PstrMsg)
                if hasattr(self,"_mqttClient"):
                    logging.debug(f'Mqtt publish >> {PstrMsg}')
                    mqtttopic = f'Shioaji/v1/futures/tick/{Item["code"]}'
                    self._mqttClient.publish(mqtttopic, PstrMsg, qos=1)
            logging.debug(f'SubscribeFuturesTickWorker<< {Item}')
            counter += 1
            self._subscribeFuturesTickQueue.task_done()

    async def run(self,websocket,message):
        self._message = message
        self._websocket = websocket
        if (self.checkEmptyMessage()):
            return
        self._data = self.checkFormateMessage(self._message)
        if (self._data == None):
            await websocket.send(ujson.dumps({"error": "wrong formate message."}))
            return
        logging.info("<< "+ self._message)
        CmdDefault = ujson.dumps({"type": "respose", "result": f'command not found.'})
        if 'params' not in self._data:
            logging.info(f'cmd{self._data["cmd"]}')
            result = await getattr(self, f'cmd{self._data["cmd"]}', lambda: CmdDefault)(wsclient= websocket)
        else:
            logging.info(f'cmd{self._data["cmd"]}::{self._data["params"]}')
            result = await getattr(self, f'cmd{self._data["cmd"]}', lambda: CmdDefault)(wsclient= websocket,**self._data["params"])
        if type(result) == str:
            await websocket.send(result)

    async def cmdID(self,wsclient):
        # {"cmd":"ID"}
        ret = {"type": "response","ret":True}
        ret["id"] = f'{self._websocket.id}'
        self._subscribeClientS.add(wsclient)
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdGetsubscribEvents(self,wsclient):
        # {"cmd":"GetsubscribEvents"}
        ret = {"type": "response","ret":True}
        self._subscribeClientS.discard(wsclient)
        self._subscribeClientS.add(wsclient)
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdRemovesubscribEvents(self,wsclient):
        # {"cmd":"RemovesubscribEvents"}
        ret = {"type": "response","ret":True}
        self._subscribeClientS.discard(wsclient)
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdGetAccount(self,wsclient):
        # {"cmd":"GetAccount"}
        cmd =  {"cmd":"GetAccount","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetStockAccount(self,wsclient):
        # {"cmd":"GetStockAccount"}
        cmd =  {"cmd":"GetStockAccount","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetFutoptAccount(self,wsclient):
        # {"cmd":"GetFutoptAccount"}
        cmd =  {"cmd":"GetFutoptAccount","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetAccountList(self,wsclient):
        # {"cmd":"GetAccountList"}
        cmd =  {"cmd":"GetAccountList","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetAccountMarginData(self,wsclient):
        # {"cmd":"GetAccountMarginData"}
        cmd =  {"cmd":"GetAccountMarginData","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetAccountOpenpositionData(self,wsclient):
        # {"cmd":"GetAccountOpenpositionData"}
        cmd =  {"cmd":"GetAccountOpenpositionData","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetAccountSettleProfitlossData(self,wsclient,**keyword_params):
        # {"cmd":"GetAccountSettleProfitlossData"}
        # {"cmd":"GetAccountSettleProfitlossData","params":{"start_date":"20210801"}}
        cmd =  {"cmd":"GetAccountSettleProfitlossData","wsclient":wsclient,"params":{**keyword_params}}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdLogout(self,wsclient):
        # {"cmd":"Logout"}
        ret = {"type": "response", "ret": self._callers.LogOut()}
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdGetOrderList(self,wsclient):
        # {"cmd":"GetOrderList"}
        cmd =  {"cmd":"GetOrderList","wsclient":wsclient}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdUpdateOrderById(self,wsclient,**keyword_params):
        # {"cmd":"UpdateOrderById","params":{"id":"d12b7777","price":17880.0}}
        if "id" not in keyword_params:
            ret = {"type": "response", "ret": False}
            await wsclient.send(ujson.dumps(ret, default=str))
        else:
            keyword_params["order_id"] = keyword_params["id"]
            del keyword_params["id"]
            cmd =  {"cmd":"UpdateOrderById","wsclient":wsclient,"params":{**keyword_params}}
            loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdCancelOrderById(self,wsclient,**keyword_params):
        # {"cmd":"CancelOrderById","params":{"id":"d12b7777"}}
        if "id" not in keyword_params:
            ret = {"type": "response", "ret": False}
            await wsclient.send(ujson.dumps(ret, default=str))
        else:
            cmd =  {"cmd":"CancelOrderById","wsclient":wsclient,"params":{"order_id":keyword_params["id"]}}
            loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetOrderById(self,wsclient,**keyword_params):
        # {"cmd":"GetOrderById","params":{"id":"d12b7777"}}
        if "id" not in keyword_params:
            ret = {"type": "response", "ret": False}
            await wsclient.send(ujson.dumps(ret, default=str))
        else:
            cmd =  {"cmd":"GetOrderById","wsclient":wsclient,"params":{"order_id":keyword_params["id"]}}
            loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdOrderStocks(self,wsclient,**keyword_params):
        # {"cmd":"OrderStocks","params":{"code":"2610","price":25.0,"quantity":1,"action":"Buy","price_type":"LMT","order_cond":"Cash","order_type":"ROD","order_lot":"Common"}}
        cmd =  {"cmd":"OrderStocks","wsclient":wsclient,"params":{**keyword_params}}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdOrderFutures(self,wsclient,**keyword_params):
        # {"cmd":"OrderFutures","params":{"code":"MXFL1","price":17767.0,"quantity":1,"action":"Buy","price_type":"LMT","order_type":"ROD","octype":"Auto"}}
        cmd =  {"cmd":"OrderFutures","wsclient":wsclient,"params":{**keyword_params}}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdActivateCa(self,wsclient,**keyword_params):
        # {"cmd":"ActivateCa","params":{"ActivateCa":"BASE64srtring" ,"CaPasswd":"password","PersonId":"PersonId" }}
        if "ActivateCa" in keyword_params and "CaPasswd" in keyword_params:
            try:
                file_content=keyword_params["ActivateCa"].encode("utf-8")
                with open("SinopacWS.pfx","wb") as file_to_save:
                    decoded_image_data = base64.decodebytes(file_content)
                    file_to_save.write(decoded_image_data)
                    file_to_save.close()
                    if "PersonId" in keyword_params:
                        ret = {"type": "response", "ret": self._callers.ActivateCa(Cafiles="SinopacWS.pfx",CaPasswd=keyword_params["CaPasswd"],PersonId=keyword_params["PersonId"])}
                    else:
                        ret = {"type": "response", "ret": self._callers.ActivateCa(Cafiles="SinopacWS.pfx",CaPasswd=keyword_params["CaPasswd"])}
            except Exception as e:
                ret = {"type": "response", "ret": False,"message":str(e)}
        else:
            ret = {"type": "response", "ret": False,"message":"Miss CA string or CaPasswd."}
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdSubscribeFutures(self,wsclient,**keyword_params):
        # {"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"tick"}}
        # {"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"bidask"}}
        ret = {"type": "response", "status": self._callers.SubscribeFutures(**keyword_params)}
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdSubscribeStocks(self,wsclient,**keyword_params):
        # {"cmd":"SubscribeStocks","params":{"code":"2330","quote_type":"tick"}}
        # {"cmd":"SubscribeStocks","params":{"code":"2330","quote_type":"bidask"}}
        ret = {"type": "response", "status": self._callers.SubscribeStocks(**keyword_params)}
        await wsclient.send(ujson.dumps(ret, default=str))

    async def cmdGetTicks(self,wsclient,**keyword_params):
        # {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08"}}
        # {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08","query_type":"RangeTime","time_start":"09:00:00","time_end":"09:20:01"}}
        # {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08","query_type":"LastCount","last_cnt":10}}
        cmd =  {"cmd":"GetTicks","wsclient":wsclient,"params":{**keyword_params}}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    async def cmdGetKBars(self,wsclient,**keyword_params):
        # {"cmd":"GetKBars","params":{"StockCode":"2330","start":"2021-10-18","end":"2021-10-19"}}
        # {"cmd":"GetKBars","params":{"FutureCode":"TXFJ1","start":"2021-10-18","end":"2021-10-19"}}
        cmd =  {"cmd":"GetBars","wsclient":wsclient,"params":{**keyword_params}}
        loop.call_soon_threadsafe(self._cmdQueue.put_nowait, cmd)

    def checkEmptyMessage(self):
        return (len(self._message) <= 0)

    def checkFormateMessage(self,message):
        try:
            return ujson.loads(message)
        except:
            pass
        finally:
            pass

    def ClientS_event(self):
        return ujson.dumps({"type": "total connects", "count": len(ClientS)})

WebsocketsHandler = WebsocketsHandler()

async def root(websocket, path):
    try:
        # Register user
        ClientS.add(websocket)
        websockets.broadcast(ClientS, WebsocketsHandler.ClientS_event())
        # Manage state changes
        async for message in websocket:
            await WebsocketsHandler.run(websocket,message)
    except Exception as e:
        logging.info(f'ws client error: %s', e)
    finally:
        # Unregister user
        ClientS.remove(websocket)
        websockets.broadcast(ClientS, WebsocketsHandler.ClientS_event())

async def start_server(port=6789):
    try:
        async with websockets.serve(root, "", port):
            await asyncio.Future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        print('Cancelled task')
        STOP.set()
        sys.exit(0)
    except Exception as ex:
        print('Exception:', ex)
    return None

def __start_wss_server(port:int=6789,callers:Caller=Caller(),pool_size:int=50,debug:int=logging.WARNING,
    with_redis:bool=False,redisHost:str=None,redisPort:int=6379,redisDb:str="0",
    with_mqtt:bool=False,mqttHost:str=None,mqttUser:str="",mqttPassword:str=""):
    WebsocketsHandler.SetCallers(callers)
    if with_redis:
        WebsocketsHandler.SetRedisConnection(redisHost,redisPort,redisDb)
    logger = logging.getLogger()
    logger.setLevel(debug)
    if debug == logging.DEBUG:
        loop.set_debug(True)
    task = None
    try:
        if with_mqtt:
            loop.create_task(WebsocketsHandler.SetMqttConnection(mqttHost,mqttUser,mqttPassword))
        loop.create_task(WebsocketsHandler.EnevtWorker('EnevtWorker-1'))
        loop.create_task(WebsocketsHandler.OrderWorker('OrderWorker-1'))
        loop.create_task(WebsocketsHandler.TradeWorker('TradeWorker-1'))
        loop.create_task(WebsocketsHandler.CmdWorker('CmdWorker-1'))

        for i in range(pool_size):
            loop.create_task(WebsocketsHandler.SubscribeStocksTickWorker(f'SubscribeStocksTickWorker-{i}'))
            loop.create_task(WebsocketsHandler.SubscribeFuturesTickWorker(f'SubscribeFuturesTickWorker-{i}'))
            loop.create_task(WebsocketsHandler.SubscribeStocksBidaskWorker(f'SubscribeStocksBidaskWorker-{i}'))
            loop.create_task(WebsocketsHandler.SubscribeFuturesBidaskWorker(f'SubscribeFuturesBidaskWorker-{i}'))

        task = asyncio.ensure_future(start_server(port))
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print('Interrupted, cancelling tasks')
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.close()

if __name__ == "__main__":
    __start_wss_server()