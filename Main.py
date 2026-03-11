import data_fetcher
from datetime import datetime

def main():
    print(f"✅ 機器人啟動時間: {datetime.now()}")
    
    # 1. 呼叫情報員：給我最好的市場
    slug = data_fetcher.get_best_market_slug()
    if not slug:
        print("目前沒有符合流動性條件的市場，結束程式。")
        return
        
    # 2. 呼叫情報員：給我該市場的報價
    market_data = data_fetcher.get_market_data(slug)
    if not market_data:
        print("無法獲取報價，結束程式。")
        return
        
    print(f"\n=== 報價分析 ({market_data['slug']}) ===")
    print(f"BUY(Ask): {market_data['buy_ask']} | SELL(Bid): {market_data['sell_bid']} | LAST: {market_data['last_price']}")
    print(f"市場流動性: {market_data['liquidity']}")
    
    # 3. 交給軍師 (即將建立的 strategy.py)
    # strategy.analyze(market_data)
    
    print("\n✅ 執行完畢，等待 GitHub 下次排程。")

if __name__ == "__main__":
    main()
