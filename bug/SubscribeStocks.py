from dotenv import load_dotenv
import shioaji as sj
import os
import asyncio
import signal
from shioaji import TickSTKv1, Exchange
load_dotenv()

# 全域變數用於事件循環控制
running = True
api = None

def event_callback(resp_code: int, event_code: int, info: str, event: str):
    print(f'Event code: {event_code} | Event: {event} | Info: {info} | Resp: {resp_code}')

def quote_callback(exchange: Exchange, tick:TickSTKv1):
    print(f"Exchange: {exchange}, Tick: {tick}")

def signal_handler(signum, frame):
    """處理信號的回調函數"""
    global running, api
    print(f'\n收到信號 {signum}，正在優雅退出...')
    running = False
    if api:
        try:
            api.logout()
            print('已登出 Shioaji API')
        except Exception as e:
            print(f'登出時發生錯誤: {e}')

async def shioajiMain(apiKey, secretKey):
    global running, api
    
    # 設置信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 創建新的事件循環
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        api = sj.Shioaji()
        api.login(
            api_key=apiKey, 
            secret_key=secretKey,
            fetch_contract=False,
        )
        api.fetch_contracts(contract_download=True)

        api.quote.set_on_tick_stk_v1_callback(quote_callback)
        api.quote.set_event_callback(event_callback)
        contract = api.Contracts.Stocks["2330"]
        print(contract)
        
        contract.code = "2*"
        api.quote.subscribe(contract, quote_type="tick",version='v1')
        
        print('開始接收報價資料，按 Ctrl+C 退出...')
        
        # 保持程序運行直到收到退出信號
        while running:
            await asyncio.sleep(0.1)
            
    except Exception as e:
        print(f'發生錯誤: {e}')
    finally:
        if api:
            try:
                api.logout()
                print('已清理 Shioaji API 連接')
            except Exception as e:
                print(f'清理時發生錯誤: {e}')

if __name__ == '__main__':
    
    apiKey = os.environ.get('API_KEY')
    secretKey = os.environ.get('SECRET_KEY')
    if apiKey == "" :
        print("No API_KEY")
        exit()
    if secretKey == "" :
        print("No SECRET_KEY")
        exit()

    # 運行 async 主函數
    asyncio.run(shioajiMain(apiKey, secretKey))
    