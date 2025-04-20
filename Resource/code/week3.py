import requests
import json
import re
from typing import Any, Dict, List, Set, Tuple
import time
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


# API 调用


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


# 递归解析 Feeds


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


# Prompt 生成 & 校验


def build_prompt(quotes, feeds):
    """构造发送给 DeepSeek 的用户 Prompt"""
    return (
        "系统角色说明: 你是一位金融数据专家，根据行情和相关新闻生成投资简报。请严格输出以下格式:\n\n"
        "<Title>标题</Title>\n"
        "<Content>内容</Content>\n"
        "<Reason>\n  - 原因1 (新闻标题)\n  - 原因2 ...\n</Reason>\n"
        "<Poll>\n  <Question>调查问题</Question>\n  <Answer>选项1</Answer>\n  <Answer>选项2</Answer>\n  <Answer>选项3</Answer>\n</Poll>\n\n"
        "【Quotes】:\n" + json.dumps(quotes, ensure_ascii=False, indent=2) + "\n\n" +
        "【Feeds】:\n"  + json.dumps(feeds,  ensure_ascii=False, indent=2)
    )


def validate_output(text: str) -> bool:
    """检查是否含 Title/Content/Reason/Poll 格式"""
    patterns = [
        r"<Title>.+?</Title>",
        r"<Content>.+?</Content>",
        r"<Reason>.+?</Reason>",
        r"<Poll>[\s\S]*?<Question>.+?</Question>[\s\S]*?<Answer>.+?</Answer>[\s\S]*?<Answer>.+?</Answer>[\s\S]*?<Answer>.+?</Answer>[\s\S]*?</Poll>",
    ]
    return all(re.search(p, text, re.DOTALL) for p in patterns)


def call_deepseek(prompt: str,
                  max_retries: int = 3,
                  base_sleep: float = 2.0,
                  timeout_sec: int = 60) -> str:
    """
    调用 DeepSeek；读超时 / 连接错误时自动重试：
        sleep = base_sleep * 2**retry_i
    """
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位金融数据专家。"},
            {"role": "user",   "content": prompt}
        ]
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                ENDPOINT,
                headers=HEADERS_DS,
                json=payload,
                timeout=timeout_sec,
            )
            resp.raise_for_status()                           # HTTP 4xx/5xx
            return resp.json()["choices"][0]["message"]["content"]

        except (ReadTimeout, ConnectionError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"DeepSeek 连接/超时失败: {e}") from e
            time.sleep(base_sleep * (2 ** attempt))           # 指数退避后重试

        except HTTPError as e:                                # 非 2xx
            raise RuntimeError(f"DeepSeek HTTP 错误: {e}") from e

# Risk‑Radar Prompt 生成

def build_risk_prompt(quotes: List[Dict[str, Any]],
                      feeds: List[Dict[str, str]]) -> str:

    stock_name  = quotes[0].get("displayName", "该股") if quotes else "该股"
    news_titles = [f["title"] for f in feeds[:3]] or ["暂无相关新闻"]

    # few‑shot 示例
    example = (
        "<Title>某某公司 风险雷达</Title>\n"
        "<Content>\n"
        "  • 波动率：IV30 = 42% ，位于过去一年 85% 分位。\n"
        "  • 宏观风险：美国 CPI 超预期\n"
        "  • 公司特定：供应链中断\n"
        "</Content>\n"
        "<Reason>\n"
        "  - 美国 CPI 超预期\n"
        "  - 供应链中断\n"
        "</Reason>\n"
        "<Poll>\n"
        "  <Question>你的风险偏好？</Question>\n"
        "  <Answer>高</Answer>\n"
        "  <Answer>中</Answer>\n"
        "  <Answer>低</Answer>\n"
        "</Poll>\n\n"
    )

    reason_block = "\n".join(f"  - {t}" for t in news_titles)

    prompt = (
        "系统角色说明: 你是首席风险官，请基于行情和新闻生成风险雷达，严格遵守下列 XML 格式。\n"
        "以下是示例：\n" + example +
        "请按照相同结构，为下列公司生成风险雷达：\n\n"
        f"<Title>{stock_name} 风险雷达</Title>\n"
        "<Content>\n"
        "  • 波动率：IV30 = {iv30}% ，位于过去一年 {iv_percentile}% 分位。\n"
        "  • 宏观风险：{macro_headline}\n"
        f"  • 公司特定：{news_titles[0]}\n"
        "</Content>\n"
        "<Reason>\n" + reason_block + "\n</Reason>\n"
        "<Poll>\n"
        "  <Question>你的风险偏好？</Question>\n"
        "  <Answer>高</Answer>\n"
        "  <Answer>中</Answer>\n"
        "  <Answer>低</Answer>\n"
        "</Poll>\n\n"
        "【Quotes】:\n" + json.dumps(quotes, ensure_ascii=False, indent=2) + "\n\n"
        "【Feeds】:\n"  + json.dumps(feeds,  ensure_ascii=False, indent=2)
    )
    return prompt



# Risk‑Radar validate

def validate_risk_output(text: str) -> bool:

    if not re.search(r"<Title>.+?</Title>",   text, re.S):
        return False
    if not re.search(r"<Content>.+?</Content>", text, re.S):
        return False
    if not re.search(r"<Reason>.+?</Reason>",  text, re.S):
        return False
    answers = re.findall(r"<Answer>.+?</Answer>", text, re.S)
    return len(answers) >= 3





# 1. build_bullbear_prompt()  —— Bull vs Bear

def build_bullbear_prompt(quotes: List[Dict[str, Any]],
                          feeds: List[Dict[str, str]]) -> str:
    """
    生成多空对比 Prompt（含 Snapshot / News / Valuation 标签）
    quotes  : list[dict]  — Quotes API 第一只股票
    feeds   : list[dict]  — 提取的新闻条目 (title, abstract, url)
    """

    q = quotes[0] if quotes else {}
    stock_name   = q.get("displayName") or q.get("shortName") or "该股"
    last_price   = q.get("price", "N/A")
    pct_change   = q.get("priceChangePercent", "N/A")
    low_52w      = q.get("price52wLow", "N/A")
    high_52w     = q.get("price52wHigh", "N/A")
    market_cap   = round(q.get("marketCap", 0) / 1e9, 2) if q.get("marketCap") else "N/A"
    pe_ratio     = q.get("peRatio", "N/A")

    # 取 3 条新闻标题
    news_titles = [n["title"] for n in feeds[:3]] or ["暂无相关新闻"]

    # Valuation 其余占位符交给模型补充
    fwd_pe      = "{forward_pe}"
    peg_ratio   = "{peg_ratio}"

    prompt = (
        f"System Instruction:\n"
        f"Create a balanced bull‑bear table for {stock_name}. "
        "Use concise bullet points.\n\n"

        f"<Title>{stock_name} 多空论点对比</Title>\n"

        "<Snapshot>\n"
        f"  • 最新价：{last_price} USD（{pct_change}%）\n"
        f"  • 52 周区间：{low_52w} – {high_52w}\n"
        f"  • 市值：{market_cap} B\n"
        "</Snapshot>\n"

        "<Content>\n"
        "   Bull Case\n"
        "  - {bull_point_1}\n"
        "  - {bull_point_2}\n"
        "   Bear Case\n"
        "  - {bear_point_1}\n"
        "  - {bear_point_2}\n"
        "</Content>\n"

        "<News>\n"
        + "\n".join(f"  - {t}" for t in news_titles) + "\n"
        "</News>\n"

        "<Valuation>\n"
        f"  • TTM PE：{pe_ratio}\n"
        f"  • Forward PE：{fwd_pe}\n"
        f"  • PEG：{peg_ratio}\n"
        "</Valuation>\n"

        "<Poll>\n"
        "  <Question>你当前立场？</Question>\n"
        "  <Answer>Bullish</Answer>\n"
        "  <Answer>Neutral</Answer>\n"
        "  <Answer>Bearish</Answer>\n"
        "</Poll>\n\n"

        "【Quotes】:\n" + json.dumps(quotes, ensure_ascii=False, indent=2) + "\n\n"
        "【Feeds】:\n"  + json.dumps(feeds,  ensure_ascii=False, indent=2)
    )
    return prompt




def validate_bullbear_output(text: str) -> bool:

    required_tags = ("Title", "Snapshot", "Content", "News", "Valuation", "Poll")
    for tag in required_tags:
        if not re.search(fr"<{tag}>.+?</{tag}>", text, re.S):
            return False

    answers = re.findall(r"<Answer>.+?</Answer>", text, re.S)
    return len(answers) >= 3



def main():
    stock_id = "a1slm7"  # Alphabet
    # stock_id = "a1u3rw"
    quotes   = fetch_quotes([stock_id])
    feedsraw = fetch_feeds(stock_id)
    feeds    = extract_feed_items(feedsraw, limit=5)

    # 使用"a1u3rw"
    # user_prompt = build_prompt(quotes, feeds)

    # for _ in range(3):
    #     output = call_deepseek(user_prompt)
    #     if validate_output(output):
    #         break
    # else:
    #     raise RuntimeError("多次生成仍不合规，终止。")
    #
    # # 写文件
    # with open("PromptV2.txt", "w", encoding="utf-8") as f:
    #     f.write(output)
    # print("已保存 PromptV2.txt")

    # 使用"a1slm7"
    # user_prompt_risk = build_risk_prompt(quotes, feeds)
    # for _ in range(3):
    #     output = call_deepseek(user_prompt_risk)
    #     if validate_risk_output(output):
    #         break
    # else:
    #     raise RuntimeError("多次生成仍不合规，终止。")
    #
    #
    # with open("PromptV3.txt", "w", encoding="utf-8") as f:
    #     f.write(output)
    # print("Risk 已写入 PromptV3.txt")

    # 使用"a1slm7"
    prompt_bb = build_bullbear_prompt(quotes, feeds)

    for _ in range(3):
        output_bb = call_deepseek(prompt_bb)
        if validate_bullbear_output(output_bb):
            break
    else:
        raise RuntimeError("Bull vs Bear 多次生成仍不合规，终止。")

    with open("PromptV4.txt", "w", encoding="utf-8") as f:
        f.write(output_bb)

    print("✅ Bull vs Bear Case 已写入 PromptV4.txt")




if __name__ == "__main__":
    main()
