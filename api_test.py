import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_siliconflow_api():
    """测试SiliconFlow API调用"""
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    payload = {
        "model": "Qwen/QwQ-32B",
        "messages": [
            {
                "role": "user",
                "content": "What opportunities and challenges will the Chinese large model industry face in 2025?"
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        
        result = response.json()
        print("API调用成功!")
        print("响应内容:")
        print(result.get('choices', [{}])[0].get('message', {}).get('content', '无内容'))
        
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        print(f"响应状态码: {response.status_code if 'response' in locals() else '无响应'}")
        print(f"响应内容: {response.text if 'response' in locals() else '无响应'}")

if __name__ == "__main__":
    test_siliconflow_api()