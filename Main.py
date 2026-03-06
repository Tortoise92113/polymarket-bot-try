import time
import requests
import pandas
from datetime import datetime, timezone
import json


LIST_URL = "https://gamma-api.polymarket.com/markets"
SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
DETAIL_URL = "https://gamma-api.polymarket.com/markets/slug/{}"

def fetch_and_print_markets():
    slug = pick_eth_updown_slug()
    if not slug:
        print("找不到 Ethereum Up or Down 的可交易市場（可能暫時沒開或搜尋結果都過期）")
        return

    d = requests.get(DETAIL_URL.format(slug), timeout=15)
    d.raise_for_status()
    detail = d.json()

    # detail 可能直接就是 market dict（你之前已驗證過）
    dm = detail if isinstance(detail, dict) and "slug" in detail else None
    if not dm:
        print("detail 回傳格式不符合預期")
        return

    # ===== outcomes 與 tokenIds 對應（非常重要）=====
    outcomes = dm.get("outcomes")
    if isinstance(outcomes, str):
        outcomes = json.loads(outcomes)

    token_ids = dm.get("clobTokenIds")
    if isinstance(token_ids, str):
        token_ids = json.loads(token_ids)

    print("=== OUTCOMES / TOKEN IDS 對應 ===")
    for i, name in enumerate(outcomes or []):
        tid = token_ids[i] if token_ids and i < len(token_ids) else None
        print(f"{i}: outcome = {name}, tokenId = {tid}")
    print("================================")
    # ================================================


    buy = float(dm["bestAsk"]) if dm.get("bestAsk") not in [None, "0", 0] else None
    sell = float(dm["bestBid"]) if dm.get("bestBid") not in [None, "0", 0] else None
    last = float(dm["lastTradePrice"]) if dm.get("lastTradePrice") not in [None, "0", 0] else None

    print("=== ETH Up/Down 報價 ===")
    print("slug:", dm.get("slug"))
    print("endDate:", dm.get("endDate"))
    print("BUY(bestAsk):", buy)
    print("SELL(bestBid):", sell)
    print("LAST:", last)
    print("active:", dm.get("active"), "closed:", dm.get("closed"), "archived:", dm.get("archived"))
    print("=======================")



def _to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _parse_dt(s):
    # 例: "2025-12-31T12:00:00Z"
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def pick_eth_updown_slug():
    params = {
        "q": "Ethereum Up or Down",
        "limit_per_type": 50,
        "keep_closed_markets": 0,   # 盡量不要把過期市場混進來
        "optimized": True
    }
    r = requests.get(SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    now = datetime.now(timezone.utc)

    candidates = []
    for ev in (data.get("events") or []):
        for m in (ev.get("markets") or []):
            slug = m.get("slug")
            if not slug:
                continue

            # 基本過濾：不要 closed/archived、不要已過期
            if m.get("closed") is True or m.get("archived") is True:
                continue

            end_dt = _parse_dt(m.get("endDate") or "")
            if end_dt and end_dt <= now:
                continue

            v24 = _to_float(m.get("volume24hr"), 0.0)
            liq = _to_float(m.get("liquidityNum"), 0.0)

            candidates.append((v24, liq, slug, m.get("endDate")))

    # 依 24h 成交量優先，再看流動性
    candidates.sort(reverse=True, key=lambda x: (x[0], x[1]))

    if not candidates:
        return None

    best = candidates[0]
    print("✅ picked:", {"slug": best[2], "endDate": best[3], "volume24hr": best[0], "liquidityNum": best[1]})
    return best[2]



def main():
    while True:
        fetch_and_print_markets()
        time.sleep(5)

if __name__ == "__main__":
    main()
