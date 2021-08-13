# -*- coding: utf-8 -*-
import sys, os
from . import config
import time
import shioaji as sj

class Caller(object):
    def __init__(self,userId:str,userPassowrd:str):
        if userId == None or userId =="":
            self._userID = config.userId
        else:
            self._userID = userId
        
        if userPassowrd == None or userPassowrd =="":
            self._userPassowrd = config.userPassowrd
        else:
            self._userPassowrd = userPassowrd
        
        if self._userPassowrd == None or self._userPassowrd == "" or self._userID == None or self._userID == "":
            print("Error!! No UserId or UserPassowrd.")
            sys.exit(70)
        self._connected = False
        self._api = sj.Shioaji()
        self._api.quote.set_quote_callback(self._quote_callback) 
        self._api.quote.set_event_callback(self._event_callback)
        self._accounts = self._api.login(self._userID, self._userPassowrd)
    
    def _quote_callback(self,topic: str, quote: dict):
        print(f"Tpoic:{topic} Quote: {quote}")

    def _event_callback(self,ResponseCode:int,Code:int, Message:str,Description:str):
        print(f'{ResponseCode} {Code} {Message} Event: {Description}')
        if ResponseCode == 0 and Code == 0:
            self._connected = True
    
    def _check_connect(self, timeout=10, period=0.25):
        mustend = time.time() + timeout
        while time.time() < mustend:
            if self._connected == True: return True
            time.sleep(period)
        return False

    def getContractsStocks(self,Name:str):
        if (self._check_connect()):
            return self._api.Contracts.Stocks[Name]

    def getContractsFutures(self,Name=""):
        if (self._check_connect()):
            if Name == "":
                return self._api.Contracts.Futures
            else:
                return self._api.Contracts.Futures[Name]

    def __del__(self):
        del self._api