Shioaji Warp Caller P.O.C project.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/shioajicaller)](https://pypi.org/project/shioajicaller)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/shioajicaller)](https://pypi.org/project/shioajicaller)
[![PyPI - License](https://img.shields.io/pypi/l/shioajicaller)](https://pypi.org/project/shioajicaller)
[![Docker Pulls](https://img.shields.io/docker/pulls/sdpower/shioaji_caller)]()

----------------------------
# 簡介
因為Shioaji API只能有五個連線，且有訂閱上限制。 如果你有多個分開程式需要處理，就會佔用重複資源。
透過Websocket服務將API擴充為誇平台，你要寫網頁下單機也沒問題。

透過取得Shioaji所擴充的功能：
* 所有Contracts
    * 輸出檔案
        * 指數 輸出檔案(`IndexsTWSE.csv`)
        * 股票 輸出檔案(`StockTWSE.csv`)
          * 上市股票
          * 櫃股股票
        * 期貨 輸出檔案(`Futures.csv`)
        * 選擇權 輸出檔案(`Options.csv`)
    * 存入Redis
    * 每日更新即可不用每次都要去查詢API，最好方式開盤前先執行跑一次。
    * 輸出為csv 檔案 很方便，使用編碼為UTF8請注意。
* Websocket服務
    * 取的Contract資料
        * 股票 Stocks
            * 指令範例：{"cmd":"GetContracts","params":{"type":"Stocks","code":"2330"}}
        * 期貨 Futures
            * 指令範例：{"cmd":"GetContracts","params":{"type":"Futures","code":"TXFB2"}}
        * 選擇權 Options
            * 指令範例：{"cmd":"GetContracts","params":{"type":"Options","code":"TXO17500C2"}}
        * 指數 Indexs
            * 指令範例：{"cmd":"GetContracts","params":{"type":"Indexs","code":"001"}}
    * 訂閱Subscribe或取消
        * 指數
            * 指令範例：{"cmd":"SubscribeIndexs","params":{"code":"001"}}
        * 股票
            * 指令範例：{"cmd":"SubscribeStocks","params":{"code":"2330","quote_type":"tick"}}
            * 指令範例：{"cmd":"SubscribeStocks","params":{"code":"2330","quote_type":"bidask"}}
        * 期貨
            * 指令範例：{"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"tick"}}
            * 指令範例：{"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"bidask"}}
    * Clinet
        * 取得client的連線ID
            * 指令範例：{"cmd":"ID"}
        * 取得Shioaji 連線帳戶資訊
            * 指令範例：{"cmd":"GetAccount"}
        * 登出 Shioaji 連線
            * {"cmd":"Logout"}
        * 接收Subscribe資料
            * 指令範例：{"cmd":"GetsubscribEvents"}
        * 取消接收接收Subscribe資料
            * 指令範例：{"cmd":"RemovesubscribEvents"}
        * 取得ticks歷史資料
            * 股票指令範例： {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08"}}
            * 期貨指令範例： {"cmd":"GetTicks","params":{"FutureCode":"TXFJ1","date":"2021-10-08"}}
            * 股票區間指令範例： {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08","query_type":"RangeTime","time_start":"09:00:00","time_end":"09:20:01"}}
            * 股票最後指令範例： {"cmd":"GetTicks","params":{"StockCode":"2330","date":"2021-10-08","query_type":"LastCount","last_cnt":10}}
            * 期貨區間指令範例： {"cmd":"GetTicks","params":{"FutureCode":"TXFJ1","date":"2021-10-08","query_type":"RangeTime","time_start":"09:00:00","time_end":"09:20:01"}}
            * 期貨最後指令範例： {"cmd":"GetTicks","params":{"FutureCode":"TXFJ1","date":"2021-10-08","query_type":"LastCount","last_cnt":10}}
        * 取得KBar歷史資料
            * 股票指令範例： {"cmd":"GetKBars","params":{"StockCode":"2330","start":"2021-10-18","end":"2021-10-19"}}
            * 期貨指令範例： {"cmd":"GetKBars","params":{"FutureCode":"TXFJ1","start":"2021-10-18","end":"2021-10-19"}}
        * 取得Scanners資料
            * 指令範例： {"cmd":"GetScanners","params":{"scanner_type":"ChangePercentRank"}}
            * 指令範例： {"cmd":"GetScanners","params":{"scanner_type":"ChangePriceRank"}}
            * 指令範例： {"cmd":"GetScanners","params":{"scanner_type":"DayRangeRank"}}
            * 指令範例： {"cmd":"GetScanners","params":{"scanner_type":"VolumeRank"}}
            * 指令範例： {"cmd":"GetScanners","params":{"scanner_type":"AmountRank"}}
        * 取得Account & Portfolio
            * 取得Account
                * 全部帳戶指令範例： {"cmd":"GetAccountList"}
                * 股票帳戶指令範例： {"cmd":"GetStockAccount"}
                * 期貨帳戶指令範例： {"cmd":"GetFutoptAccount"}
            * 取得期貨帳戶Margin資料
                * 指令範例： {"cmd":"GetMargin"}
            * 取得帳戶Position資料
                * 股票
                    * 指令範例： {"cmd":"GetListPositions"}
                * 期貨
                    * 指令範例： {"cmd":"GetListFuturePositions"}
            * 取得帳戶ProfitLoss資料
                * 股票
                    * 指令範例： {"cmd":"GetListProfitLoss"}
                * 期貨
                    * 指令範例： {"cmd":"GetListFutureProfitLoss"}
            * 取得帳戶ProfitLoss資料
                * 股票
                    * 指令範例： {"cmd":"GetListProfitLossDetail","params":{"detail_id":2}}
                * 期貨
                    * 指令範例： {"cmd":"GetListFutureProfitLossDetail","params":{"detail_id":2}}
            * 取得帳戶ProfitLossSum資料
                * 股票
                    * 指令範例： {"cmd":"GetListProfitLossSum"}
                    * 指令範例： {"cmd":"GetListProfitLossSum","params":{"begin_date":"2022-10-05","end_date":"2022-10-07"}}
                * 期貨
                    * 指令範例： {"cmd":"GetListFutureProfitLossSum"}
                    * 指令範例： {"cmd":"GetListFutureProfitLossSum","params":{"begin_date":"2022-10-05","end_date":"2022-10-07"}}
            * 取得股票帳戶交割Settlements資料
                * 指令範例： {"cmd":"GetSettlements"}
        * 下單Order
            * 套用憑證Apply & Activate CA
                * 請用base64 讀取你的憑證。
                * PersonId 可以不給預設為登入帳戶的ID
                * 指令範例： {"cmd":"ActivateCa","params":{"ActivateCa":"BASE64srtring" ,"CaPasswd":"password"}}
                * 指令範例： {"cmd":"ActivateCa","params":{"ActivateCa":"BASE64srtring" ,"CaPasswd":"password","PersonId":"PersonId" }}
            * 股票下單 Stock
                * price 請給小數點
                * 買指令範例： {"cmd":"OrderStocks","params":{"code":"2610","price":25.0,"quantity":1,"action":"Buy","price_type":"LMT","order_cond":"Cash","order_type":"ROD","order_lot":"Common"}}
                * first_sell指令範例： {"cmd":"OrderStocks","params":{"code":"2610","price":25.0,"quantity":1,"action":"Sell","price_type":"LMT","order_cond":"Cash","order_type":"ROD","order_lot":"Common","first_sell":"true"}}
            * 期貨下單 Future
                * price 請給小數點
                * 指令範例： {"cmd":"OrderFutures","params":{"code":"MXFL1","price":17767.0,"quantity":1,"action":"Buy","price_type":"LMT","order_type":"ROD","octype":"Auto"}}
                * DayTrade 指令範例： {"cmd":"OrderFutures","params":{"code":"MXFL1","price":17767.0,"quantity":1,"action":"Buy","price_type":"LMT","order_type":"ROD","octype":"DayTrade"}}
            * 取的交易清單list_trades
                * 指令範例：{"cmd":"GetOrderList"}
            * 取的單筆交易GetOrderById
                * 參數id為oder的id
                * 指令範例：{"cmd":"GetOrderById","params":{"id":"d12b7777"}}
            * 取消單筆交易CancelOrderById
                * 參數id為oder的id
                * 指令範例：{"cmd":"CancelOrderById","params":{"id":"d12b7777"}}
            * 更新單筆交易UpdateOrderById
                * 參數id為oder的id
                * price 請給小數點
                * 指令範例：{"cmd":"UpdateOrderById","params":{"id":"d12b7777","price":17880.0,"qty":1}}
                * 指令範例：{"cmd":"UpdateOrderById","params":{"id":"d12b7777","price":17880.0}}
                * 指令範例：{"cmd":"UpdateOrderById","params":{"id":"d12b7777","qty":1}}
    * 額外功能
        * 推播 Subscribe資料
            * redis
            * mqtt
    * 回傳類型type
        * 命令回傳
            * {"type": "response".....
        * 訂閱資料回傳
            * {"type":"IndexsTickEvent"...........
            * {"type": "StocksTickEvent"........
            * {"type": "FuturesTickEvent"........
            * {"type": "StocksBidaskEvent"........
            * {"type": "FuturesBidaskEvent"........
        * Shioaji系統回傳
            * {"type":"SystemEvent"..........
            * {"type":"OrderEvent"..........
            * {"type":"TradeEvent"..........

## 安裝使用
### 使用pip安裝
** 請確認 python 版本 3.8 之上 **
### linux windows
```
$ pip install shioajicaller
$ shioajicaller -h
```

### mac osx
```
$ pip install shioajicaller uvloop==0.17.0
$ shioajicaller -h
```


### 使用Docker
Docker [https://hub.docker.com/r/sdpower/shioaji_caller](https://hub.docker.com/r/sdpower/shioaji_caller)
範例：
```
docker run -d \
  --name shioaji-caller \
  --restart unless-stopped \
  --env-file=".env" \
  -p 6789:6789 \
  sdpower/shioaji_caller websockets -wm -ps 250
```

## 範例Example
這裡說明範例，參數避免暴露請自行建立.env檔案就可以不用給帳號密碼參數。

```
USER_ID=YOUID
USER_PASSWORD=YOU_PASSWORD
```
### 執行範例
```
$ python main.py update --help
$ python main.py update -u YOUID -p YOU_PASSWORD
```
### 直接執行cli
```
$ shioajicaller update
$ shioajicaller -u YOUID -p YOU_PASSWORD
```
### 新增 redis
```
$ shioajicaller update -rh 127.0.0.1 -rp 6379 -rdb 0 -t redis
$ shioajicaller -t redis -u YOUID -p YOU_PASSWORD
```
### ENV範例

可使用環境變數與.env擋案

```
API_KEY=YOU_API_KEY
SECRET_KEY=YOU_SECRET_KEY
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
MQTT_HOST=127.0.0.1
MQTT_USER=user
MQTT_PASSWORD=password
```
## Websocket服務

命令範例:
```
# shioajicaller
shioaji version:0.3.6.dev3
usage: <command> [<args>]
The most commonly used git commands are:
   update         update Code List
   websockets     start a websocket server
shioajicaller: error: the following arguments are required: command

# shioajicaller websockets --h
usage: main.py [-h] [-api API_KEY [API_KEY ...]] [-secret SECRET_KEY [SECRET_KEY ...]] [-wp WEBSOCKETS_PORT] [-ps POOL_SIZE] [-wr] [-rh REDIS_HOST] [-rp REDIS_PORT]
               [-rdb REDIS_DB] [-wm] [-mh MQTT_HOST] [-mu MQTT_USER] [-mp MQTT_PASSWORD] [-v]

Websockets Server

options:
  -h, --help            show this help message and exit
  -api API_KEY [API_KEY ...], --api-key API_KEY [API_KEY ...]
                        Shioaji API_KEY
  -secret SECRET_KEY [SECRET_KEY ...], --secret-key SECRET_KEY [SECRET_KEY ...]
                        Shioaji SECRET_KEY
  -wp WEBSOCKETS_PORT, --websockets-port WEBSOCKETS_PORT
                        Websockets port
  -ps POOL_SIZE, --pool-size POOL_SIZE
                        pool size
  -wr, --with-redis     with redis publish.
  -rh REDIS_HOST, --redis-host REDIS_HOST
                        redis host
  -rp REDIS_PORT, --redis-port REDIS_PORT
                        redis port
  -rdb REDIS_DB, --redis-db REDIS_DB
                        reis db
  -wm, --with-mqtt      with mqtt publish.
  -mh MQTT_HOST, --mqtt-host MQTT_HOST
                        mqtt host
  -mu MQTT_USER, --mqtt-user MQTT_USER
                        mqtt user
  -mp MQTT_PASSWORD, --mqtt-password MQTT_PASSWORD
                        mqtt password
  -v, --verbosity       increase output verbosity
```

啟動服務:
```
# shioajicaller websockets
shioaji version:0.3.6.dev3
Start Websockets Server Port:6789
```

### Client 範例

下方可以看到個指令接收狀況與系統回傳
#### 資料訂閱 範例
```
# python -m websockets ws://127.0.0.1:6789/
Connected to ws://127.0.0.1:6789/.
< {"type": "total connects", "count": 1}
> {"cmd":"GetAccount"}
< {"type": "response", "cmd":"GetAccount", "result":["person_id='F124673627' broker_id='F00000' account_id='80000000' signed=True username='XXX'","person_id='F11111111' broker_id='XAXAX' account_id='12345678' signed=True username='xxxxx'"]}
< {"type": "SystemEvent", "ret": {"ResponseCode": 0, "Code": 0, "Message": "host '203.66.91.161:80', IP 203.66.91.161:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1)", "Description": "Session up"}}'"]}
>
> {"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"tick"}}
< {{"type":"response","cmd":"SubscribeFutures","ret":true}
< {"type": "SystemEvent", "ret": {"ResponseCode": 200, "Code": 16, "Message": "TIC/v1/FOP/*/TFE/TXFJ1", "Description": "Subscribe or Unsubscribe ok"}}
> {"cmd":"GetsubscribEvents"}
< {"type":"response","cmd":"GetsubscribEvents","ret":true}
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:54.513000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:54.701000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:54.963000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:55.014000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:56.178000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:56.374000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:15:56.374000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:00.754000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:01.670000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:04.625000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:04.719000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:11.930000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:17.009000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:19.447000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:19.566000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:19.567000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:19.567000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:19.568000", "open": "16345", "underlying_price": "16408.35", "bid_side_
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:20.898000", "open": "16345", "underlying_price": "16408.35", "bid_side_total_vol": 22498, "ask_side_total_vol": 22817, "avg_price": "16392.996253", "close": "16366", "high": "16457", "low": "16288", "amount": "16366", "total
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:27.667000", "open": "16345", "underlying_price": "16408.35", "bid_side_total_vol": 22501, "ask_side_total_vol": 22818, "avg_price": "16392.993864", "close": "16366", "high": "16457", "low": "16288", "amount": "49098", "total_amount": "555706099", "volume": 3, "total_volume": 33899, "tick_type": 1, "chg_type": 2, "price_chg": "5", "pct_chg": "0.03056", "simtrade": 0, "UNTime"
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:27.668000", "open": "16345", "underlying_price": "16408.35", "bid_side_total_vol": 22504, "ask_side_total_vol": 22821, "avg_price": "16392.989883", "close": "16366", "high": "16457", "low": "16288", "amount": "81830", "total_amount": "555787929", "volume": 5, "total_volume": 33904, "tick_type": 1, "chg_type": 2, "price_chg": "5", "pct_chg": "0.03056", "simtrade": 0, "UNTime": "2021-10-04 22:16:27.515556", "exchange": "TAIFEX"}}
< {"type": "FuturesEvent", "ret": {"code": "TXFJ1", "datetime": "2021-10-04T22:16:31.564000", "open": "16345", "underlying_price": "16408.35", "bid_side_total_vol": 22500, "ask_side_total_vol": 22824, "avg_price": "16392.988173", "close": "16364", "high": "16457", "low": "16288", "amount": "32728", "total_amount": "555820657", "volume": 2, "total_volume": 33906, "tick_type": 2, "chg_type": 2, "price_chg": "3", "pct_chg": "0.018336", "simtrade": 0, "UNTime": "2021-10-04 22:16:31.515169", "exchange": "TAIFEX"}}
  {"cmd":"RemovesubscribEvents"}
< {"type":"response","cmd":"RemovesubscribEvents","ret":true}
```

#### 下單範例
```
# python -m websockets ws://127.0.0.1:6789/
Connected to ws://127.0.0.1:6789/.
< {"type": "total connects", "count": 1}
> {"cmd":"GetAccount"}
< {"type": "response", "cmd":"GetAccount", "result":["person_id='F124673627' broker_id='F00000' account_id='80000000' signed=True username='XXX'","person_id='F11111111' broker_id='XAXAX' account_id='12345678' signed=True username='xxxxx'"]}
< {"type": "SystemEvent", "ret": {"ResponseCode": 0, "Code": 0, "Message": "host '203.66.91.161:80', IP 203.66.91.161:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1)", "Description": "Session up"}}'"]}
> {"cmd":"ActivateCa","params":{"PersonId":"XXXXXXX","CaPasswd":"XXXXXXX","ActivateCa":"......."}}
< {"type":"response","cmd":"ActivateCa","ret":true}
> {"cmd":"OrderFutures","params":{"code":"MXFL1","price":17880.0,"quantity":1,"action":"Sell","price_type":"LMT","order_type":"IOC","octype":"DayTrade"}}
< {"type":"response","cmd":"OrderFutures","ret":true}
< {"type":"TradeEvent","ret":{"contract":{"code":"MXFL1","symbol":"MXF202112","name":"AAAAAAAA","category":"MXF","delivery_month":"202112","delivery_date":"2021\/12\/15","underlying_kind":"I","unit":1,"limit_up":19637.0,"limit_down":16067.0,"reference":17852.0,"update_date":"2021\/11\/22"},"status":{"id":"5e1943de","status":"PendingSubmit","status_code":"    ","order_datetime":"2021-11-22 11:04:19","deals":[]},"order":{"action":"Sell","price":17880.0,"quantity":1,"id":"5e1943de","seqno":"762613","account":{"account_type":"F","person_id":"XXXXXXX","broker_id":"XXXXXXX","account_id":"XXXXXXX","signed":true},"ca":"........","price_type":"LMT","order_type":"IOC","octype":"DayTrade"}}}
< {"type":"OderEvent","ret":["FORDER",{"operation":{"op_type":"New","op_code":"00","op_msg":""},"order":{"id":"5e1943de","seqno":"762613","ordno":"t00Gw","account":{"account_type":"F","person_id":"","broker_id":"XXXXXXX","account_id":"3918061","signed":true},"action":"Sell","price":17880.0,"quantity":1,"order_type":"IOC","market_type":"Day","oc_type":"DayTrade","subaccount":""},"status":{"id":"5e1943de","exchange_ts":1637550559,"modified_price":0.0,"cancel_quantity":0,"order_quantity":1},"contract":{"security_type":"FUT","code":"MXF","exchange":"TIM","delivery_month":"XXXXXXX","delivery_date":"","strike_price":0.0,"option_right":"Future"}}]}
< {"type":"OderEvent","ret":["FORDER",{"operation":{"op_type":"Cancel","op_code":"00","op_msg":""},"order":{"id":"5e1943de","seqno":"762613","ordno":"t00Gw","account":{"account_type":"F","person_id":"","broker_id":"XXXXXXX","account_id":"3918061","signed":true},"action":"Sell","price":17880.0,"quantity":1,"order_type":"IOC","market_type":"Day","oc_type":"DayTrade","subaccount":""},"status":{"id":"5e1943de","exchange_ts":1637550559,"modified_price":0.0,"cancel_quantity":1,"order_quantity":1},"contract":{"security_type":"FUT","code":"MXF","exchange":"TIM","delivery_month":"XXXXXXX","delivery_date":"","strike_price":0.0,"option_right":"Future"}}]}
```
### 安全事項免責聲明

1. 目前系統設計皆未使用加密連線，請自行做好安全控管。
2. 任何使用本程式不擔保任何損失且皆與本系統無關請自己負責。
3. 不擔保其正確性、即時性或完整性。
