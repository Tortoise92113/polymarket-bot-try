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
    """尋找流動性與成交量最高的 ETH Up/Down 市場"""
    params = {"q": "Ethereum Up or Down", "limit_per_type": 50, "keep_closed_markets": 0, "optimized": True}
    try:
        r = requests.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[DataFetcher] API 搜尋失敗: {e}")
        return None

    now = datetime.now(timezone.utc)
    candidates = []
    
    for ev in (data.get("events") or []):
        for m in (ev.get("markets") or []):
            slug = m.get("slug")
            if not slug or m.get("closed") or m.get("archived"): continue
            end_dt = _parse_dt(m.get("endDate") or "")
            if end_dt and end_dt <= now: continue
            
            # 🚨 新增防呆：流動性低於 100 的垃圾市場直接跳過
            liq = _to_float(m.get("liquidityNum"))
            if liq < 100: continue
            
            candidates.append((_to_float(m.get("volume24hr")), liq, slug))

    candidates.sort(reverse=True, key=lambda x: (x[0], x[1]))
    return candidates[0][2] if candidates else None

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
