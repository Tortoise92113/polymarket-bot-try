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
    """精準搜尋 Ethereum above 系列市場"""
    # SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
    # 直接下精準關鍵字
    params = {
        "q": "Ethereum above", 
        "limit_per_type": 50
    }
    
    print("🔍 正在 Polymarket 搜尋 'Ethereum above' 相關市場...")
    try:
        r = requests.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[DataFetcher] API 搜尋失敗: {e}")
        return None

    candidates = []
    
    for ev in (data.get("events") or []):
        for m in (ev.get("markets") or []):
            slug = m.get("slug", "")
            liq = _to_float(m.get("liquidityNum"))
            
            # 過濾掉已經關閉的市場
            if m.get("closed") or m.get("archived") or not m.get("active"):
                continue
                
            # 只要檔名包含 ethereum 且有流動性，就印出來給你看
            if "ethereum" in slug.lower() and liq > 0:
                print(f"🎯 發現市場: {slug} | 流動性: {liq}")
                candidates.append((liq, slug))

    candidates.sort(reverse=True, key=lambda x: x[0])
    
    if not candidates:
        print("❌ 目前找不到活躍的 Ethereum above 市場。")
        return None
        
    best_slug = candidates[0][1]
    print(f"\n✅ 決定鎖定流動性最高的主力市場: {best_slug}")
    return best_slug
    
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
