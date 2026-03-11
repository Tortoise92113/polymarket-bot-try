import requests
from datetime import datetime, timezone

SEARCH_URL = "https://gamma-api.polymarket.com/markets"
HISTORY_URL = "https://clob.polymarket.com/prices-history"

def _to_float(x, default=0.0):
    try: return float(x)
    except: return default

def get_best_market_slug():
    params = {"active": True, "closed": False, "limit": 100}
    try:
        r = requests.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[DataFetcher] API 抓取失敗: {e}")
        return None

    candidates = []
    for m in data:
        slug = m.get("slug", "")
        if "ethereum" not in slug.lower(): continue
            
        liq = _to_float(m.get("liquidityNum"))
        if liq <= 0: continue
            
        # 抓取 Token ID (這裡預設抓 index 0，通常是 'Yes' 或 'Up' 的代幣)
        tokens = m.get("tokens", [])
        token_id = tokens[0].get("token_id") if tokens else None
        
        if token_id:
            candidates.append((liq, slug, token_id))

    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0] if candidates else (None, None, None)

def get_market_data(slug):
    try:
        r = requests.get(f"https://gamma-api.polymarket.com/markets/slug/{slug}", timeout=15)
        r.raise_for_status()
        dm = r.json()
        return {
            "slug": slug,
            "buy_ask": _to_float(dm.get("bestAsk")),
            "sell_bid": _to_float(dm.get("bestBid")),
            "last_price": _to_float(dm.get("lastTradePrice")),
            "liquidity": _to_float(dm.get("liquidityNum"))
        }
    except Exception as e:
        print(f"[DataFetcher] 抓取報價失敗: {e}")
        return None

def get_price_history(token_id):
    """抓取該代幣過去 24 小時的歷史價格 (interval=1d)"""
    params = {"market": token_id, "interval": "1d"}
    try:
        r = requests.get(HISTORY_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        # Polymarket 回傳格式: {"history": [{"t": 時間戳, "p": 價格}, ...]}
        history = data.get("history", [])
        prices = [_to_float(item.get("p")) for item in history]
        return prices
    except Exception as e:
        print(f"[DataFetcher] 抓取歷史價格失敗: {e}")
        return []
