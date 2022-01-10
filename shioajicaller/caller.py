# -*- coding: utf-8 -*-
import sys, logging
from datetime import datetime,date,timedelta
from . import config
import time
import shioaji as sj
from shioaji import TickFOPv1, TickSTKv1, BidAskSTKv1, BidAskFOPv1,Exchange

class Caller(object):
    def __init__(self):
        self._userID = config.userId
        self._userPassowrd = config.userPassowrd
        self._connected = False
        self._api = sj.Shioaji()
        self._caStatus = False
        logging.info("shioaji version:"+sj.__version__)
        print("shioaji version:"+sj.__version__)
        self._api.quote.set_event_callback(self._event_callback)
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

    def SetAccount(self,userId:str="",userPassowrd:str=""):
        if userId != None and userId !="":
            self._userID = userId
        if userPassowrd != None and userPassowrd !="":
            self._userPassowrd = userPassowrd

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

    # only for futoptand and option !? https://sinotrade.github.io/tutor/accounting/account_portfolio/
    # On top has:The features of this page will be removed in the future.
    def GetAccountMargin(self):
        if (self._check_connect()):
            return self._api.get_account_margin()
        return False

    def GetAccountMarginData(self):
        account_margin = self.GetAccountMargin()
        if account_margin:
            return account_margin.data()
        return False

    def GetAccountOpenposition(self):
        if (self._check_connect()):
            return self._api.get_account_openposition()
        return False

    def GetAccountOpenpositionData(self):
        account_openposition = self.GetAccountOpenposition()
        if account_openposition:
            return account_openposition.data()
        return False

    def GetAccountSettleProfitloss(self,start_date:str=""):
        if (self._check_connect()):
            if start_date == "":
                start_date = (date.today() - timedelta(days=30)).strftime('%Y%m%d')
            return self._api.get_account_settle_profitloss(start_date=start_date)
        return False

    def GetAccountSettleProfitlossData(self,start_date:str=""):
        account_settle_profitloss = self.GetAccountSettleProfitloss(start_date)
        if account_settle_profitloss:
            return account_settle_profitloss.data()
        return False

    def Login(self):
        if self._userPassowrd == None or self._userPassowrd == "" or self._userID == None or self._userID == "":
            logging.error("Error!! No UserId or UserPassowrd.")
            sys.exit(70)
        self._accounts = self._api.login(self._userID, self._userPassowrd,contracts_cb = self.ContractsDone())

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

    def OrderStocks(self,code:str="",price:float=0.0,quantity:int=0,action:str="",price_type:str="",order_type:str="",order_cond:str="",order_lot:str="Common",first_sell:str="false"):
        """
        Code: Stocks code.
        price: 10.0
        quantity: 1
        action: {Buy, Sell} (買、賣)
        price_type: {LMT, MKT} (限價、市價)
        order_type: {ROD, IOC, FOK} (當日有效、立即成交否則取消、全部成交否則取消)
        order_cond: {Cash, MarginTrading, ShortSelling} (現股、融資、融券)
        order_lot: {Common, Fixing, Odd, IntradayOdd} (整股、定盤、盤後零股、盤中零股)
        first_sell {str}: {true, false}
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
                first_sell=first_sell,
                account=self._api.stock_account)
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
        octype: {Auto, NewPosition, Cover, DayTrade} (自動、新倉、平倉、當沖)
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

    def __del__(self):
        if self._connected:
            self._api.logout()
        del self._api