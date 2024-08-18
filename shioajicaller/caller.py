# -*- coding: utf-8 -*-
import sys, logging
from datetime import datetime,date,timedelta
from . import config
import time
import shioaji as sj
from shioaji import TickFOPv1, TickSTKv1, BidAskSTKv1, BidAskFOPv1,Exchange

class Caller(object):
    def __init__(self):
        self._apiKey = config.apiKey
        self._secretKey = config.secretKey
        self._connected = False
        self._api = sj.Shioaji()
        self._caStatus = False
        logging.info("shioaji version:"+sj.__version__)
        self._api.quote.set_event_callback(self._event_callback)
        self._api.quote.set_quote_callback(self.Quote_callback_v0_tick)
        self._api.quote.set_on_tick_stk_v1_callback(self.Quote_callback_stk_v1_tick)
        self._api.quote.set_on_bidask_stk_v1_callback(self.Quote_callback_stk_v1_bidask)
        self._api.quote.set_on_tick_fop_v1_callback(self.Quote_callback_fop_v1_tick)
        self._api.quote.set_on_bidask_fop_v1_callback(self.Quote_callback_fop_v1_bidask)
        self._api.set_order_callback(self.Order_CallBack)

    def Order_CallBack(self,stat, msg):
        if hasattr(self, 'OrderCB'):
            self.OrderCB(stat, msg)

    def Trade_CallBack(self,keyword_params):
        if hasattr(self, 'TradeCB'):
            self.TradeCB(**keyword_params)

    def SetOrderCallBack(self,callback):
        if callable(callback):
            self.OrderCB=callback

    def SetTradeCallBack(self,callback):
        if callable(callback):
            self.TradeCB=callback

    def SetEnevtCallBack(self,callback):
        if callable(callback):
            self.EventCallback=callback

    def SetSubscribeTickv0CallBack(self,callback):
        if callable(callback):
            self.SubscribeTickv0CallBack= callback

    def SetSubscribeStocksTickCallBack(self,callback):
        if callable(callback):
            self.SubscribeStocksTickCallBack= callback

    def SetSubscribeFuturesTickCallBack(self,callback):
        if callable(callback):
            self.SubscribeFuturesTickCallBack= callback

    def SetSubscribeStocksBidaskCallBack(self,callback):
        if callable(callback):
            self.SubscribeStocksBidaskCallBack= callback

    def SetSubscribeFuturesBidaskCallBack(self,callback):
        if callable(callback):
            self.SubscribeFuturesBidaskCallBack= callback

    def SetAccount(self,apiKey:str="",secretKey:str=""):
        if apiKey != None and apiKey !="":
            self._apiKey = apiKey
        if secretKey != None and secretKey !="":
            self._secretKey = secretKey

    def GetStockAccount(self):
        if (self._check_connect()):
            return self._api.stock_account
        return False
    def GetFutoptAccount(self):
        if (self._check_connect()):
            return self._api.futopt_account
        return False

    def GetAccountList(self):
        if (self._check_connect()):
            return self._api.list_accounts()
        return False

    def GetAccount(self):
        if (self._check_connect()):
            return self._accounts
        return False

    # future account
    def GetMargin(self,timeout: int = 5000):
        if (self._check_connect()):
            future_account = self._api.futopt_account
            if future_account != None:
                return self._api.margin(account=future_account, timeout=timeout)
            return False
        return False

    def GetListFuturePositions(self,timeout: int = 5000):
        if (self._check_connect()):
            future_account = self._api.futopt_account
            if future_account == None:
                return False
            return self.GetListPositions(account = future_account ,timeout = timeout)
        return False

    # Default: stock account
    def GetListPositions(self,account: sj.account = None ,timeout: int = 5000):
        if (self._check_connect()):
            return self._api.list_positions(account=account, timeout=timeout)
        return False

    def GetListFutureProfitLoss(self,timeout: int = 5000):
        if (self._check_connect()):            
            future_account = self._api.futopt_account
            if future_account == None:
                return False
            return self.GetListProfitLoss(account=future_account ,timeout = timeout)
        return False
        
    # Default date range is today.
    # Default: stock account
    def GetListProfitLoss(self,account: sj.account = None,begin_date: str = '',end_date: str = '',timeout: int = 5000):        
        if (self._check_connect()):
            return self._api.list_profit_loss(account=account ,begin_date=begin_date ,end_date=end_date ,timeout=timeout)
        return False

    def GetListFutureProfitLossDetail(self,detail_id: int = 0,timeout: int = 5000):
        if (self._check_connect()):            
            if detail_id == 0:
                return False
            future_account = self._api.futopt_account
            if future_account == None:
                return False
            return self.GetListProfitLossDetail(account=future_account ,detail_id=detail_id ,timeout = timeout)
        return False

    # Default date range is today.
    # Default: stock account
    def GetListProfitLossDetail(self,account: sj.account = None,detail_id: int = 0,timeout: int = 5000):
        if (self._check_connect()):
            if detail_id == 0:
                return False
            return self._api.list_profit_loss_detail(account=account ,detail_id=detail_id ,timeout=timeout)
        return False

    def GetListFutureProfitLossSum(self,begin_date: str = '',end_date: str = '',timeout: int = 5000):
        if (self._check_connect()):            
            future_account = self._api.futopt_account
            if future_account == None:
                return False
            return self.GetListProfitLossSum(account=future_account ,begin_date=begin_date ,end_date=end_date ,timeout = timeout)
        return False

    # Default date range is today.
    # Default: stock account
    def GetListProfitLossSum(self,account: sj.account = None,begin_date: str = '',end_date: str = '',timeout: int = 5000):
        if (self._check_connect()):
            return self._api.list_profit_loss_sum(account=account ,begin_date=begin_date ,end_date=end_date ,timeout=timeout)
        return False

    def GetSettlements(self,timeout: int = 5000):
        if (self._check_connect()):
            return self._api.settlements(timeout=timeout)
        return False

    def Login(self):
        if self._apiKey == None or self._apiKey == "" or self._secretKey == None or self._secretKey == "":
            logging.error("Error!! No apiKey or secretKey.")
            sys.exit(70)
        self._accounts = self._api.login(self._apiKey, self._secretKey,contracts_cb = self.ContractsDone())

    def LogOut(self):
        self._connected = False
        self._connected_ts = None
        ret = self._api.logout()
        self._api.Contracts = None
        logging.info(f"LogOut.")
        return ret

    def ActivateCa(self,Cafiles:str="Sinopac.pfx",PersonId:str="",CaPasswd:str=""):
        if PersonId =="":
            PersonId = self._userID
        if (self._check_connect()):
            result = self._api.activate_ca(
                ca_path=Cafiles,
                ca_passwd=CaPasswd,
                person_id=PersonId,
            )
            self._caStatus = result
            return result
        else:
            return False

    def ContractsDone(self):
        logging.info(f"Loading Contracts is Done.")

    def Contracts(self,type:str="",code:str=""):
        if (type == None or type ==""):
            return False
        if (self._check_connect()):            
            if (code == None or code ==""):
                contract = self._api.Contracts[type]
                if contract != None:
                    return contract
                else:
                    return False
            else:
                contract = self._api.Contracts[type][code]
                if contract != None:
                    return contract
                else:
                    return False    
        else:
            return False

    def SubscribeIndexs(self,code:str="",intraday_odd:bool=False):
        quote_type = "tick"
        version = "v0"
        if (code == None or code ==""):
            return False
        logging.info(f"SubscribeIndexs {code} {quote_type} {version}")
        if (self._check_connect()):
            contract = self._api.Contracts.Indexs[code]
            if contract != None:
                self._api.quote.subscribe(contract ,quote_type=quote_type, intraday_odd=intraday_odd ,version=version)
                return True
            else:
                return False
        else:
            return False

    def SubscribeStocks(self,code:str="",quote_type:str="tick",intraday_odd:bool=False,version:str="v1"):
        if (code == None or code ==""):
            return False
        logging.info(f"SubscribeStocks {code} {quote_type} {version}")
        if (self._check_connect()):
            contract = self._api.Contracts.Stocks[code]
            if contract != None:
                self._api.quote.subscribe(contract ,quote_type=quote_type, intraday_odd=intraday_odd ,version=version)
                return True
            else:
                return False
        else:
            return False
    def SubscribeFutures(self,code:str="",quote_type:str="tick",intraday_odd:bool=False,version:str="v1"):
        if (code == None or code ==""):
            return False
        logging.info(f"SubscribeFutures {code} {quote_type} {version}")
        if (self._check_connect()):
            contract = self._api.Contracts.Futures[code]
            if contract != None:
                self._api.quote.subscribe(contract ,quote_type=quote_type, intraday_odd=intraday_odd ,version=version)
                return True
            else:
                return False
        else:
            return False

    def UpdateOrderById(self,order_id:str="",price:float=0.0,qty:int=0):
        if self._check_connect():
            self._api.update_status()
            tradeList = self._api.list_trades()
            if len(tradeList) == 0:
                return False
            else:
                for trade in tradeList:
                    if trade.order.id == order_id:
                        if price > 0.0 and qty > 0:
                            return dict(**self._api.update_order(trade=trade, price=price, qty=qty))
                        elif price > 0.0:
                            return dict(**self._api.update_order(trade=trade, price=price))
                        elif qty > 0:
                            return dict(**self._api.update_order(trade=trade, qty=qty))
                        else:
                            return False
                return False
        else:
            return False

    def CancelOrderById(self,order_id:str=""):
        if self._check_connect():
            self._api.update_status()
            tradeList = self._api.list_trades()
            if len(tradeList) == 0:
                return False
            else:
                for trade in tradeList:
                    if trade.order.id == order_id:
                        return dict(**self._api.cancel_order(trade))
                return False
        else:
            return False

    def GetOrderById(self,order_id:str=""):
        if self._check_connect():
            self._api.update_status()
            tradeList = self._api.list_trades()
            if len(tradeList) == 0:
                return False
            else:
                for trade in tradeList:
                    if trade.order.id == order_id:
                        return dict(**trade)
                return False
        else:
            return False

    def GetOrderList(self):
        if self._check_connect():
            self._api.update_status()
            tradeList = self._api.list_trades()
            if len(tradeList) == 0:
                return tradeList
            else:
                ret=[]
                for trade in tradeList:
                    ret.append(dict(**trade))
                return ret
        else:
            return False

    def OrderStocks(self,code:str="",price:float=0.0,quantity:int=0,action:str="",price_type:str="",order_type:str="",order_cond:str="",order_lot:str="Common",daytrade_short:str="false",custom_field:str=""):
        """
        Code: Stocks code.
        price: 10.0
        quantity: 1
        action: {Buy, Sell} (買、賣)
        price_type: {LMT, MKT} (限價、市價)
        order_type: {ROD, IOC, FOK} (當日有效、立即成交否則取消、全部成交否則取消)
        order_cond: {Cash, Netting, MarginTrading, ShortSelling, Emerging} (現股、餘額交割、融資、融券、興櫃)
        order_lot: {Common, ,BlockTrade ,Fixing, Odd, IntradayOdd} (整股、鉅額、定盤、盤後零股、盤中零股)
        daytrade_short {str}: {true, false}
        custom_field {str}:"" 自定義內容
        """
        if self._check_connect():
            if not self._caStatus:
                return False
            if (code == None or code ==""):
                return False
            if (price_type == "LMT" and price <= 0 ):
                return False

            contract = self._api.Contracts.Stocks[code]
            order = self._api.Order(
                action=action,
                price=price,
                quantity=quantity,
                price_type=price_type,
                order_type=order_type,
                order_cond=order_cond,
                order_lot=order_lot,
                daytrade_short=daytrade_short,
                account=self._api.stock_account,
                custom_field = custom_field)                
            return dict(**self._api.place_order(contract, order, timeout=0,cb=self.Trade_CallBack))
        else:
            return False

    def OrderFutures(self,code:str="",price:float=0.0,quantity:int=0,action:str="",price_type:str="",order_type:str="",octype:str=""):
        """
        Code: Futures code.
        price: 100.0
        quantity: 1
        action: {Buy, Sell} (買、賣)
        price_type: {LMT, MKT, MKP} (限價、市價、範圍市價)
        order_type: {ROD, IOC, FOK} (當日有效、立即成交否則取消、全部成交否則取消)
        octype: {Auto, New, Cover, DayTrade} (自動、新倉、平倉、當沖)
        """
        if self._check_connect():
            if not self._caStatus:
                return False
            if (code == None or code ==""):
                return False
            if (price_type == "LMT" and price <= 0 ):
                return False

            contract = self._api.Contracts.Futures[code]
            order = self._api.Order(
                action=action,
                price=price,
                quantity=quantity,
                price_type=price_type,
                order_type=order_type,
                octype=octype,
                account=self._api.futopt_account)
            return dict(**self._api.place_order(contract, order, timeout=0,cb=self.Trade_CallBack))
        else:
            return False

    def Quote_callback_v0_tick(self,topic: str, quote: dict):
        quote['UNTime']= datetime.now()
        tmp = topic.split("/")
        quote['code'] = tmp[2]
        quote['exchange']= tmp[1]
        if hasattr(self, 'SubscribeTickv0CallBack'):
            self.SubscribeTickv0CallBack(quote)

    def Quote_callback_stk_v1_tick(self,exchange: Exchange, tick:TickSTKv1):
        tickdata = tick.to_dict(raw=True)
        tickdata['UNTime']= datetime.now()
        tickdata['exchange']= f'{exchange}'
        if hasattr(self, 'SubscribeStocksTickCallBack'):
            self.SubscribeStocksTickCallBack(tickdata)

    def Quote_callback_stk_v1_bidask(self,exchange: Exchange, bidask:BidAskSTKv1):
        bidaskdata = bidask.to_dict(raw=True)
        bidaskdata['UNTime']= datetime.now()
        bidaskdata['exchange']= f'{exchange}'
        if hasattr(self, 'SubscribeStocksBidaskCallBack'):
            self.SubscribeStocksBidaskCallBack(bidaskdata)

    def Quote_callback_fop_v1_tick(self,exchange: Exchange, tick:TickFOPv1):
        tickdata = tick.to_dict(raw=True)
        tickdata['UNTime']= datetime.now()
        tickdata['exchange']= f'{exchange}'
        if hasattr(self, 'SubscribeFuturesTickCallBack'):
            self.SubscribeFuturesTickCallBack(tickdata)

    def Quote_callback_fop_v1_bidask(self,exchange: Exchange, bidask:BidAskFOPv1):
        bidaskdata = bidask.to_dict(raw=True)
        bidaskdata['UNTime']= datetime.now()
        bidaskdata['exchange']= f'{exchange}'
        if hasattr(self, 'SubscribeFuturesBidaskCallBack'):
            self.SubscribeFuturesBidaskCallBack(bidaskdata)

    def Quote_callback(self,topic: str, quote: dict):
        print(f"Tpoic:{topic} Quote: {quote}")

    def _event_callback(self,ResponseCode:int,Code:int, Message:str,Description:str):
        logging.info(f'EventCallback {ResponseCode} {Code} {Message} Event: {Description}')
        if ResponseCode == 0 and Code == 0:
            self._connected = True
            self._connected_ts=time.time()
        if hasattr(self, 'EventCallback'):
            item = {
                "ResponseCode":ResponseCode,
                "Code": Code,
                "Message": Message,
                "Description": Description,
                }
            self.EventCallback(item)

    def _check_connect(self, timeout=30, period=0.25):
        if self._connected and (time.time() - self._connected_ts) < 86400-30:
            return self._accounts
        # token timeout 24hr before 30sec will relogin
        if self._connected and (time.time() - self._connected_ts) >= 86400-30:
            self.LogOut
        self.Login()
        mustend = time.time() + timeout
        while time.time() < mustend:
            if self._connected == True: return True
            time.sleep(period)
        return False

    def GetTicks(self,StockCode:str="",FutureCode:str="",**kwargs):
        if (self._check_connect()):
            if StockCode != None and StockCode !="":
                contract = self.getContractsStockByCode(StockCode)
            if FutureCode != None and FutureCode !="":
                contract = self.getContractsFutures(FutureCode)

            if contract != None:
                return self._api.ticks(contract=contract, **kwargs)
        return False

    def GetBars(self,StockCode:str="",FutureCode:str="",**kwargs):
        if (self._check_connect()):
            if StockCode != None and StockCode !="":
                contract = self.getContractsStockByCode(StockCode)
            if FutureCode != None and FutureCode !="":
                contract = self.getContractsFutures(FutureCode)

            if contract != None:
                return self._api.kbars(contract=contract, **kwargs)
        return False


    ## OTC, TSE
    def getContractsIndexs(self,Exchange:str):
        if (self._check_connect()):
            return self._api.Contracts.Indexs[Exchange]

    ## OES, OTC, TSE
    def getContractsStocks(self,Exchange:str):
        if (self._check_connect()):
            return self._api.Contracts.Stocks[Exchange]

    def getContractsStockByCode(self,Code:str):
        if (self._check_connect()):
            return self._api.Contracts.Stocks[Code]

    def getContractsFutures(self,Code:str=""):
        if (self._check_connect()):
            if Code == "":
                return self._api.Contracts.Futures
            else:
                return self._api.Contracts.Futures[Code]

    def getContractsOptions(self,Code:str=""):
        if (self._check_connect()):
            if Code == "":
                return self._api.Contracts.Options
            else:
                return self._api.Contracts.Options[Code]

    def GetScanners(self,**kwargs):        
        if (self._check_connect()):
            return self._api.scanners(**kwargs)

    def __del__(self):
        if self._connected:
            self._api.logout()
        del self._api