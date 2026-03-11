import requests
import json

def get_best_market_slug():
    url = "https://gamma-api.polymarket.com/markets"
    params = {"active": True, "closed": False, "limit": 100}
    try:
        r = requests.get(url, params=params, timeout=15)
        candidates = []
        for m in r.json():
            slug = m.get("slug", "")
            liq = float(m.get("liquidityNum", 0) or 0)
            if "ethereum" in slug.lower() and liq > 0:
                candidates.append((liq, slug))
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1] if candidates else None
    except Exception as e:
        print(f"[錯誤] 搜尋市場失敗: {e}")
        return None

def get_market_data(slug):
    try:
        r = requests.get(f"https://gamma-api.polymarket.com/markets/slug/{slug}", timeout=15)
        dm = r.json()
        
        # 安全抓取 Token ID (從 clobTokenIds 拿第一個)
        token_ids = dm.get("clobTokenIds")
        if isinstance(token_ids, str): token_ids = json.loads(token_ids)
        token_id = token_ids[0] if token_ids else None

        return {
            "slug": slug,
            "buy_ask": float(dm.get("bestAsk", 0) or 0),
            "sell_bid": float(dm.get("bestBid", 0) or 0),
            "last_price": float(dm.get("lastTradePrice", 0) or 0),
            "liquidity": float(dm.get("liquidityNum", 0) or 0),
            "token_id": token_id
        }
    except Exception as e:
        print(f"[錯誤] 獲取報價失敗: {e}")
        return None

def get_price_history(token_id):
    if not token_id: return []
    try:
        r = requests.get("https://clob.polymarket.com/prices-history", params={"market": token_id, "interval": "1d"}, timeout=15)
        # 提取歷史價格陣列
        return [float(item.get("p", 0)) for item in r.json().get("history", [])]
    except Exception as e:
        print(f"[錯誤] 獲取歷史價格失敗: {e}")
        return []
