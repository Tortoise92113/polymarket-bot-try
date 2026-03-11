import requests
from datetime import datetime, timezone

SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
DETAIL_URL = "https://gamma-api.polymarket.com/markets/slug/{}"

def _to_float(x, default=0.0):
    try: return float(x)
    except: return default

def _parse_dt(s):
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except: return None

def get_best_market_slug():
    """嚴格鎖定 Ethereum 相關的活躍市場"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "active": True,
        "closed": False,
        "limit": 100
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[DataFetcher] API 抓取失敗: {e}")
        return None

    candidates = []
    for m in data:
        slug = m.get("slug", "")
        
        # 🚨 核心防護：只允許 Ethereum 相關市場
        if "ethereum" not in slug.lower():
            continue
            
        liq = _to_float(m.get("liquidityNum"))
        # 流動性必須大於 0
        if liq <= 0: 
            continue
            
        candidates.append((liq, slug))

    # 依流動性從大到小排序，挑最有肉的那個
    candidates.sort(reverse=True, key=lambda x: x[0])
    
    if not candidates:
        print("[DataFetcher] 目前無活躍的 Ethereum 市場。")
        return None
        
    return candidates[0][1]
    
def get_market_data(slug):
    """抓取指定市場的詳細報價，並回傳乾淨的字典"""
    try:
        d = requests.get(DETAIL_URL.format(slug), timeout=15)
        d.raise_for_status()
        dm = d.json()
        
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
