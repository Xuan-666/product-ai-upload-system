#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI API调用的脚本
用于验证通义千问API是否能正常工作
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

# 通义千问API配置
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "“⚠️ 请替换为你的通义千问 API Key，例如 sk-xxxx”")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_API_URL = f"{QWEN_BASE_URL.rstrip('/')}/chat/completions"

print("=== AI API测试 ===")
print(f"API密钥: {QWEN_API_KEY}")
print(f"API基础URL: {QWEN_BASE_URL}")
print(f"完整API URL: {QWEN_API_URL}")

# 测试文本API
try:
    print("\n1. 测试文本API调用...")
    response = requests.post(
        QWEN_API_URL,
        json={
            "model": "qwen-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个智能商品上架系统，专业、友好地回答用户关于商品上架、销售分析等问题。"
                },
                {
                    "role": "user",
                    "content": "请介绍一下智能商品上架系统"
                }
            ],
            "temperature": 0.7,
            "top_p": 0.95
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {QWEN_API_KEY}"
        },
        timeout=60
    )
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        ai_response = response.json()
        print("响应内容:")
        print(json.dumps(ai_response, ensure_ascii=False, indent=2))
        print("\nAI回复:", ai_response.get("choices", [{}])[0].get("message", {}).get("content", "无内容"))
        print("文本API测试成功!")
    else:
        print(f"API请求失败: {response.text}")
        print("文本API测试失败!")
        
except Exception as e:
    print(f"文本API调用异常: {e}")
    import traceback
    traceback.print_exc()

# 测试模块导入
try:
    print("\n2. 测试模块导入...")
    from ai_utils import call_qwen_text_api
    
    result = call_qwen_text_api("这是一个测试消息")
    print("模块调用成功!")
    print(f"测试结果: {result}")
    
except Exception as e:
    print(f"模块导入/调用异常: {e}")
    import traceback
    traceback.print_exc()