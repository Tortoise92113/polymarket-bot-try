import data_fetcher
import strategy
from datetime import datetime

def main():
    print(f"✅ 機器人啟動時間: {datetime.now()}")
    
    # 1. 拿 Slug (只接一個變數！)
    slug = data_fetcher.get_best_market_slug()
    if not slug:
        print("目前沒有符合的 Ethereum 市場，結束程式。")
        return
        
    # 2. 拿報價與 Token ID
    market_data = data_fetcher.get_market_data(slug)
    if not market_data or not market_data.get("token_id"):
        print("無法獲取市場資料或 Token ID，結束程式。")
        return
        
    # 3. 拿歷史 K 線
    history = data_fetcher.get_price_history(market_data["token_id"])
    
    # 4. 跑策略大腦
    strategy.analyze_and_trade(market_data, history)
    
    print("\n✅ 執行完畢，等待下次排程。")

if __name__ == "__main__":
    main()
