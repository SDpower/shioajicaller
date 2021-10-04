Shioaji Warp Caller P.O.C project.
----------------------------
# 簡介
因為Shioaji API只能有五個連線，且有訂閱上限制。 如果你有多個分開程式需要處理，就會佔用重複資源。
透過Websocket服務將API擴充為誇平台，你要寫網頁下單機也沒問題。

透過取得Shioaji所擴充的功能：
* 所有Contracts
    * 輸出檔案
        * 股票 輸出檔案(`StockTWSE.csv`)
          * 上市股票
          * 櫃股股票
        * 期貨 輸出檔案(`Futures.csv`)
        * 選擇權 輸出檔案(`Options.csv`)
    * 存入Redis
    * 每日更新即可不用每次都要去查詢API，最好方式開盤前先執行跑一次。
    * 輸出為csv 檔案 很方便，使用編碼為UTF8請注意。
* Websocket服務
    * 訂閱Subscribe或取消
        * 股票
            * 指令範例：{"cmd":"SubscribeStocks","params":{"code":"2330","quote_type":"tick"}}
        * 期貨 
            * 指令範例：{"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"tick"}}
    * Clinet 
        * 取的client的連線ID
            * 指令範例：{"cmd":"ID"}
        * 取的Shioaji 連線帳戶資訊
            * 指令範例：{"cmd":"GetAccount"}
        * 接收Subscribe資料
            * 指令範例：{"cmd":"GetsubscribEvents"}
        * 取消接收接收Subscribe資料
            * 指令範例：{"cmd":"RemovesubscribEvents"}
    * 額外功能
        * 推播 Subscribe資料
            * redis
            * mqtt
    * 回傳類型type
        * 命令回傳
            * {"type": "response".....
        * 訂閱資料回傳
            * {"type": "StocksEvent"........
            * {"type": "FuturesEvent"........
        * Shioaji系統回傳
            * {"type":"SystemEvent"..........

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
USER_ID=YOUID
USER_PASSWORD=YOU_PASSWORD
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
shioaji version:0.3.3.dev3
usage: <command> [<args>]
The most commonly used git commands are:
   update         update Code List
   websockets     start a websocket server
shioajicaller: error: the following arguments are required: command
```

啟動服務:
```
# shioajicaller websockets
shioaji version:0.3.3.dev3
Start Websockets Server Port:6789
```

### Client 範例

下方可以看到個指令接收狀況與系統回傳
```
# python -m websockets ws://127.0.0.1:6789/
Connected to ws://127.0.0.1:6789/.
< {"type": "total connects", "count": 1}
> {"cmd":"GetAccount"}
< {"type": "response", "account": ["person_id='XXXXXX' broker_id='XXXXXX' account_id='XXXXXXX' signed=True username='XXXXXXXXX'", "person_i
< {"type": "SystemEvent", "ret": {"ResponseCode": 0, "Code": 0, "Message": "host '203.66.91.161:80', IP 203.66.91.161:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1)", "Description": "Session up"}}'"]}
>
> {"cmd":"SubscribeFutures","params":{"code":"TXFJ1","quote_type":"tick"}}
< {"type": "response", "status": true}
< {"type": "SystemEvent", "ret": {"ResponseCode": 200, "Code": 16, "Message": "TIC/v1/FOP/*/TFE/TXFJ1", "Description": "Subscribe or Unsubscribe ok"}}
> {"cmd":"GetsubscribEvents"}
< {"type": "response", "ret": true}
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
< {"type": "response", "ret": true}
```

### 安全事項免責聲明

1. 目前系統設計皆未使用加密連線，請自行做好安全控管。
2. 任何使用本程式不擔保任何損失且皆與本系統無關請自己負責。
3. 不擔保其正確性、即時性或完整性。 
