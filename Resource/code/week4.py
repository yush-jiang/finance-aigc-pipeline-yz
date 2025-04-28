import time
import json
import re
import requests
import pandas as pd
from typing import Any, Dict, List, Set, Tuple
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError

# 常量配置
DEEPSEEK_KEY   = "sk-a013cb27adc2449cb42cef63630d3d38"
FINANCE_KEY    = "0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM"

ENDPOINT       = "https://api.deepseek.com/chat/completions"
HEADERS_DS     = {
    "Authorization": f"Bearer {DEEPSEEK_KEY}",
    "Content-Type": "application/json"
}
BASE_URL_QUOTES = "https://assets.msn.com/service/Finance/Quotes"
BASE_URL_FEEDS  = "https://assets.msn.com/service/MSN/Feed/me"


def fetch_quotes(stock_ids: List[str]):
    params = {
        "apikey": FINANCE_KEY,
        "ocid": "finance-utils-peregrine",
        "cm": "en-us",
        "ids": ",".join(stock_ids),
        "wrapodata": "false",
    }
    return requests.get(BASE_URL_QUOTES, params=params, timeout=8).json()

def fetch_feeds(stock_id: str, top: int = 30):
    params = {
        "$top": top,
        "DisableTypeSerialization": "true",
        "apikey": FINANCE_KEY,
        "cm": "en-us",
        "contentType": "article,video,slideshow,webcontent",
        "entityids": stock_id,
        "ocid": "finance-data-feeds",
        "query": "finance_stock",
        "responseSchema": "cardview",
        "scn": "ANON",
        "timeOut": "3000",
        "wrapodata": "false",
    }
    return requests.get(BASE_URL_FEEDS, params=params, timeout=8).json()

# 递归提取新闻
def extract_feed_items(raw: Any, limit: int = 5) -> List[Dict[str, str]]:
    collected: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str]] = set()

    def dfs(node: Any):
        if len(collected) >= limit:
            return
        if isinstance(node, dict):
            title = node.get("title") or node.get("Title")
            url   = node.get("url")   or node.get("Url")
            if title and url:
                key = (title, url)
                if key not in seen:
                    seen.add(key)
                    collected.append({
                        "title": title.strip(),
                        "abstract": node.get("abstract") or node.get("Abstract") or "",
                        "url": url.strip(),
                    })
            for v in node.values():
                dfs(v)
        elif isinstance(node, list):
            for item in node:
                dfs(item)

    dfs(raw)
    return collected[:limit]

#Prompt 构造
def build_bullbear_prompt(quote: Dict[str, Any],
                          feeds: List[Dict[str, str]]) -> str:
    stock_name = quote.get("displayName") or quote.get("shortName") or "该股"
    last_price = quote.get("price", "N/A")
    pct_change = quote.get("priceChangePercent", "N/A")
    low_52w    = quote.get("price52wLow", "N/A")
    high_52w   = quote.get("price52wHigh", "N/A")
    market_cap = round(quote.get("marketCap", 0) / 1e9, 2) if quote.get("marketCap") else "N/A"
    pe_ratio   = quote.get("peRatio", "N/A")

    news_titles = [n["title"] for n in feeds[:3]] or ["暂无相关新闻"]

    prompt = (
        f"System Instruction:\n"
        f"Create a balanced bull-bear table for {stock_name}. Use concise bullet points.\n\n"
        f"<Title>{stock_name} 多空论点对比</Title>\n"
        "<Snapshot>\n"
        f"  • 最新价：{last_price} USD（{pct_change}%）\n"
        f"  • 52 周区间：{low_52w} – {high_52w}\n"
        f"  • 市值：{market_cap} B\n"
        "</Snapshot>\n"
        "<Content>\n"
        "   Bull Case\n"
        "  - {bull_point_1}\n"
        "  - {bull_point_2}\n"
        "   Bear Case\n"
        "  - {bear_point_1}\n"
        "  - {bear_point_2}\n"
        "</Content>\n"
        "<News>\n" + "\n".join(f"  - {t}" for t in news_titles) + "\n</News>\n"
        "<Valuation>\n"
        f"  • TTM PE：{pe_ratio}\n"
        f"  • Forward PE：{{forward_pe}}\n"
        f"  • PEG：{{peg_ratio}}\n"
        "</Valuation>\n"
        "<Poll>\n"
        "  <Question>你当前立场？</Question>\n"
        "  <Answer>看涨</Answer>\n"
        "  <Answer>中性</Answer>\n"
        "  <Answer>看跌</Answer>\n"
        "</Poll>\n\n"
        "【Quote】:\n" + json.dumps(quote, ensure_ascii=False, indent=2) + "\n\n"
        "【Feeds】:\n" + json.dumps(feeds, ensure_ascii=False, indent=2)
    )
    return prompt

# DeepSeek 调用
def validate_bullbear_output(txt: str) -> bool:
    tags = ("Title", "Snapshot", "Content", "News", "Valuation", "Poll")
    if not all(re.search(fr"<{t}>.+?</{t}>", txt, re.S) for t in tags):
        return False
    return len(re.findall(r"<Answer>.+?</Answer>", txt, re.S)) >= 3




def call_deepseek(prompt: str,
                  max_retries=3,
                  base_sleep=2.0,
                  timeout_sec=60) -> str:
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位金融数据专家。"},
            {"role": "user",   "content": prompt}
        ]
    }
    for attempt in range(max_retries):
        try:
            r = requests.post(ENDPOINT, headers=HEADERS_DS,
                              json=payload, timeout=timeout_sec)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except (ReadTimeout, ConnectionError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"DeepSeek 连接超时: {e}") from e
            time.sleep(base_sleep * 2 ** attempt)
        except HTTPError as e:
            raise RuntimeError(f"DeepSeek HTTP 错误: {e}") from e

#  单支股票处理
def process_stock(stock_id: str) -> Dict[str, str]:
    try:
        raw_quotes = fetch_quotes([stock_id])

        quote = {}
        if raw_quotes:
            first = raw_quotes[0]
            if isinstance(first, list):
                quote = first[0] if first else {}
            elif isinstance(first, dict):
                quote = first

        feeds = extract_feed_items(fetch_feeds(stock_id), 5)
        prompt = build_bullbear_prompt(quote, feeds)

        for _ in range(3):
            xml = call_deepseek(prompt)
            if validate_bullbear_output(xml):
                break
        else:
            raise RuntimeError("生成结果多次不合规")

        return {"stock_id": stock_id, "bullbear_xml": xml, "error": ""}

    except Exception as e:
        return {
            "stock_id": stock_id,
            "bullbear_xml": "",
            "error": str(e).replace('\n', ' ')
        }

def main():
    STOCK_IDS = [
        "a1u3rw",  # Alphabet A (GOOGL)
        "a1xzim",  # Microsoft
        "a1mou2",  # Apple
        "a24kar",  # Tesla
        "a1nhlh",  # Amazon
        "a1yv52",  # NVIDIA
        "a1ndww",  # AMD
        "a1vmf2",  # Intel
        "a1slm7",  # Meta Platforms
    ]

    results = []
    for sid in STOCK_IDS:
        print(f" 正在处理 {sid} ")
        results.append(process_stock(sid))
        time.sleep(1)

    pd.DataFrame(results).to_csv("BullBearBatch.csv", index=False, encoding="utf-8-sig")
    print("已写入 BullBearBatch.csv")

if __name__ == "__main__":
    main()
