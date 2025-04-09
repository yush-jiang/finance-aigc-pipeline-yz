import requests

API_KEY = "sk-a013cb27adc2449cb42cef63630d3d38"
ENDPOINT = "https://api.deepseek.com/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 初始对话
conversation_history = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello! How can I assist you today? "}
]


payload = {
    "model": "deepseek-chat",
    "messages": conversation_history
}

response = requests.post(ENDPOINT, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    reply = result["choices"][0]["message"]["content"]
    print("DeepSeek 回复：", reply)
else:
    print("请求失败，状态码：", response.status_code)
    print("错误信息：", response.text)
