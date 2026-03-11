import data_fetcher
import strategy
from datetime import datetime

def main():
    print(f"✅ 機器人啟動時間: {datetime.now()}")
    
    # 1. 抓取最好的市場與對應的 Token ID
    liq, slug, token_id = data_fetcher.get_best_market_slug()
    if not slug or not token_id:
        print("目前沒有符合條件的市場或找不到 Token ID，結束程式。")
        return
        
    # 2. 獲取當下報價
    market_data = data_fetcher.get_market_data(slug)
    if not market_data:
        return
        
    # 3. 獲取歷史 K 線 (用來算黃金線)
    history_prices = data_fetcher.get_price_history(token_id)
    
    # 4. 交給大腦判斷
    strategy.analyze_and_trade(market_data, history_prices)
    
    print("\n✅ 執行完畢，等待下次排程。")

if __name__ == "__main__":
    main()
