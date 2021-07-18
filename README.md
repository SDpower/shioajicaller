Shioaji Warp Caller P.O.C project.
----------------------------
# 簡介
透過取得Shioaji所有：
* 股票 輸出檔案(`StockTWSE.csv`)
  * 上市股票
  * 櫃股股票
* 期貨 輸出檔案(`Futures.csv`)

每日更新即可不用每次都要去查詢API，最好方式開盤前先執行跑一次。
輸出為csv 檔案 很方便使用。編碼為UTF8請注意
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
