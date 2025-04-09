import requests
import json
import re

# 使用 DeepSeek API
API_KEY = "sk-a013cb27adc2449cb42cef63630d3d38"
ENDPOINT = "https://api.deepseek.com/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 调用 finance API

def get_quotes_data(stock_ids):
    """
    调用 Quotes API 获取股票实时价格信息
    """
    quotes_api = "https://assets.msn.com/service/Finance/Quotes"
    params = {
        "apikey": "0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM",
        "ocid": "finance-utils-peregrine",
        "cm": "en-us",
        "ids": ",".join(stock_ids),
        "wrapodata": "false"
    }
    response = requests.get(quotes_api, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Quotes API 请求失败，状态码：", response.status_code)
        return None

def get_feeds_data(stock_id):
    """
    调用 Feed API 获取金融资讯数据
    """
    feeds_api = "https://assets.msn.com/service/MSN/Feed/me"
    params = {
        "$top": "30",
        "DisableTypeSerialization": "true",
        "apikey": "0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM",
        "cm": "en-us",
        "contentType": "article,video,slideshow,webcontent",
        "entityids": stock_id,
        "ocid": "finance-data-feeds",
        "query": "finance_stock",
        "responseSchema": "cardview",
        "scn": "ANON",
        "timeOut": "3000",
        "wrapodata": "false"
    }
    response = requests.get(feeds_api, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Feeds API 请求失败，状态码：", response.status_code)
        return None

# Prompt 模板构建及格式校验

def generate_prompt(quotes_data, feeds_data):
    feed_item = feeds_data[0]
    prompt = (
        "系统角色说明: 你是一位金融数据专家，熟悉股票报价和新闻资讯。你的任务是根据下列提供的金融数据生成一份内容，输出格式必须严格符合以下要求，否则请重新生成：\n\n"
        "生成内容格式要求:\n"
        "<Title>标题</Title>\n"
        "<Content>内容</Content>\n"
        "<Poll>\n"
        "  <Question>调查问题</Question>\n"
        "  <Answer>选项1</Answer>\n"
        "  <Answer>选项2</Answer>\n"
        "  <Answer>选项3</Answer>\n"
        "</Poll>\n\n"
        "【Quotes 数据】:\n" + json.dumps(quotes_data, ensure_ascii=False, indent=2) + "\n\n"
        "【Feeds 数据】:\n" + json.dumps(feed_item, ensure_ascii=False, indent=2)
    )
    return prompt

def validate_output(content):
    title_pattern = r"<Title>.+</Title>"
    content_pattern = r"<Content>.+</Content>"
    poll_pattern = r"<Poll>\s*<Question>.+</Question>\s*<Answer>.+</Answer>\s*<Answer>.+</Answer>\s*<Answer>.+</Answer>\s*</Poll>"
    if (re.search(title_pattern, content, re.DOTALL) and
            re.search(content_pattern, content, re.DOTALL) and
            re.search(poll_pattern, content, re.DOTALL)):
        return True
    else:
        return False

def call_chat_model(prompt):

    conversation = [
        {"role": "system", "content": "你是一位金融数据专家。"},
        {"role": "user", "content": prompt}
    ]
    payload = {
        "model": "deepseek-chat",
        "messages": conversation
    }
    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print("DeepSeek API 请求失败，状态码：", response.status_code)
        print("错误信息：", response.text)
        return None

def main():
    # 示例股票 ID 列表，可根据需要修改
    stock_ids = ["a1u3rw", "a1u3p2"]

    quotes_data = get_quotes_data(stock_ids)
    feeds_data = get_feeds_data("a1u3rw")

    if quotes_data is None or feeds_data is None:
        print("API 数据获取失败，请检查接口参数及网络连接。")
        return

    # 生成 Prompt（用于向大模型传递数据和格式要求）
    prompt = generate_prompt(quotes_data, feeds_data)
    print("生成的 Prompt 为：\n", prompt)

    # 调用大模型生成内容，若生成内容格式不符合要求，则重试（最多尝试 3 次）
    max_attempts = 3
    final_output = None
    for attempt in range(max_attempts):
        generated_output = call_chat_model(prompt)
        if generated_output is None:
            print("生成内容失败。")
            return

        print(f"\n第 {attempt + 1} 次生成的结果：\n{generated_output}\n")
        if validate_output(generated_output):
            print("生成内容格式合规。")
            final_output = generated_output
            break
        else:
            print("生成内容格式不合规，正在重新生成...")
    else:
        print("经过多次尝试，未能生成合规的输出格式。")
        return

    # 将最终生成结果保存到当前文件夹下的 PromptV1.txt
    file_path = "PromptV1.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    main()
