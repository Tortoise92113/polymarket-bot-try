def analyze_and_trade(market_data, history_prices):
    current_price = market_data['last_price']
    
    print(f"\n=== 🧠 策略大腦啟動 ({market_data['slug']}) ===")
    print(f"當下 LAST 價格: {current_price:.3f}")
    
    # 濾網 1: 剔除極端價格 (勝負已定)
    if current_price < 0.25 or current_price > 0.75:
        print(f"⚠️ 價格 {current_price} 進入極端區，缺乏波動空間，保持觀望。")
        return

    # 濾網 2: 檢查歷史數據是否足夠
    if not history_prices or len(history_prices) < 5:
        print("⚠️ 歷史價格數據不足，無法計算黃金線。")
        return

    high = max(history_prices)
    low = min(history_prices)

    if high == low:
        print("⚠️ 過去一段時間價格無波動，不宜進場。")
        return

    # 核心邏輯: 0.382 回撤位 (做多買點)
    golden_buy_price = low + (high - low) * 0.382

    print(f"📈 近期區間: High {high:.3f} | Low {low:.3f}")
    print(f"🎯 黃金支撐買價: {golden_buy_price:.3f}")

    # 判斷進場 (給予 2% 的容錯空間)
    if current_price <= golden_buy_price * 1.02:
        print("🚨 觸發買入信號！價格已回落至黃金區間，準備掛單。")
    else:
        print("⏳ 尚未跌至黃金買點，繼續等待回調。")
