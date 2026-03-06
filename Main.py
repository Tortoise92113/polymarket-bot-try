import time
import requests
import pandas as pd
from datetime import datetime, timezone
import json
import os

# --- 設定網址 ---
LIST_URL = "https://gamma-api.polymarket.com/markets"
SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
DETAIL_URL = "https://gamma-api.polymarket.com/markets/slug/{}"

# --- 新增：黃金比例計算邏輯 (測試盤點用) ---
def calculate_strategy(last_price):
    """
    Jonerdthan，這部分之後填入你的黃金比例公式。
    目前先以 0.5 秒延遲與 5% 獲利門檻做示範。
    """
    # 假設你的黃金比例線算出來是 0.618
    golden_line = 0.618 
    
    print(f"\n[策略盤點] 當前 LAST 價格: {last_price}")
    print(f"[策略盤點] 目標黃金線: {golden_line}")

    if last_price < (golden_line * 0.98): # 價差大於 2% 才買
        print("🚨 觸發買入信號！價格低於黃金線門檻。")
    elif last_price >= (golden_line * 1.05):
        print("💰 觸發賣出信號！已達 5% 獲利。")
    else:
        print("⏳ 未達門檻，繼續觀望。")

def fetch_and_print_markets():
    slug = pick_eth_updown_slug()
    if not slug:
        print("找不到 Ethereum Up or Down 的可交易市場")
        return

    try:
        d = requests.get(DETAIL_URL.format(slug), timeout=15)
        d.raise_for_status()
        dm = d.json()
    except Exception as e:
        print(f"抓取詳細資料失敗: {e}")
        return

    # outcomes 與 tokenIds
    outcomes = dm.get("outcomes")
    if isinstance(outcomes, str): outcomes = json.loads(outcomes)
    token_ids = dm.get("clobTokenIds")
    if isinstance(token_ids, str): token_ids = json.loads(token_ids)

    buy = float(dm["bestAsk"]) if dm.get("bestAsk") not in [None, "0", 0] else None
    sell = float(dm["bestBid"]) if dm.get("bestBid") not in [None, "0", 0] else None
    last = float(dm["lastTradePrice"]) if dm.get("lastTradePrice") not in [None, "0", 0] else 0.0

    print(f"\n=== {dm.get('slug')} 報價分析 ===")
    print(f"BUY(Ask): {buy} | SELL(Bid): {sell} | LAST: {last}")
    
    # --- 執行策略盤點 ---
    if last > 0:
        calculate_strategy(last)

def _to_float(x, default=0.0):
    try: return float(x)
    except: return default

def _parse_dt(s):
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except: return None

def pick_eth_updown_slug():
    params = {"q": "Ethereum Up or Down", "limit_per_type": 50, "keep_closed_markets": 0, "optimized": True}
    try:
        r = requests.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except: return None

    now = datetime.now(timezone.utc)
    candidates = []
    for ev in (data.get("events") or []):
        for m in (ev.get("markets") or []):
            slug = m.get("slug")
            if not slug or m.get("closed") or m.get("archived"): continue
            end_dt = _parse_dt(m.get("endDate") or "")
            if end_dt and end_dt <= now: continue
            candidates.append((_to_float(m.get("volume24hr")), _to_float(m.get("liquidityNum")), slug))

    candidates.sort(reverse=True, key=lambda x: (x[0], x[1]))
    return candidates[0][2] if candidates else None

def main():
    print(f"✅ 機器人啟動時間: {datetime.now()}")
    # 執行一次即結束，由 GitHub Actions 的 cron 定時觸發
    fetch_and_print_markets()
    print(f"✅ 執行完畢，結束程式。")

if __name__ == "__main__":
    main()
