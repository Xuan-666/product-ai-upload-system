#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI工具模块
提供统一的AI调用接口，避免代码重复
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 通义千问API配置
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "“⚠️ 请替换为你的通义千问 API Key，例如 sk-xxxx”")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
# 构建完整的API URL
QWEN_API_URL = f"{QWEN_BASE_URL.rstrip('/')}/chat/completions"

def call_qwen_api(base64_image):
    """
    调用通义千问API进行商品分析
    
    参数:
        base64_image (str): Base64编码的图片数据
        
    返回:
        dict: AI分析结果
        
    异常:
        Exception: API调用失败时抛出异常
    """
    try:
        # 构建API请求参数
        prompt = """请分析这张商品图片，严格按照以下要求生成内容：
1. 首先仔细识别图片中所有可见的文字信息，特别是商品名称、标题等关键文字
2. 基于识别到的文字内容进行分析，确保生成的内容与图片中的文字信息一致
3. 生成以下内容：
   - 商品特征标签（5-10个关键词）
   - 核心卖点（3-5个要点）
   - 商品描述（100-200字）
   - 3个不同风格的商品标题
   - 5个搜索关键词推荐
   - 商品价格建议（如果图片中有价格信息，请提取并标注；如果没有，请根据商品类型给出合理的价格区间建议）

请严格按照以下JSON格式返回结果，不要添加任何其他内容：
{
  "features": ["标签1", "标签2", ...],
  "sellingPoints": [{"title": "卖点标题1", "desc": "卖点描述1"}, ...],
  "description": "商品描述...",
  "titles": ["标题1", "标题2", "标题3"],
  "keywords": ["关键词1", "关键词2", ...],
  "price": "价格信息或建议"
}"""
        
        # 发送请求到通义千问API
        response = requests.post(
            QWEN_API_URL,
            json={
                "model": "qwen-vl-plus",  # 使用支持图像的模型
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}  # 使用base64编码的图像
                        ]
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.95
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {QWEN_API_KEY}"  # 使用Bearer Token认证
            },
            timeout=60
        )
        
        # 解析API响应
        if response.status_code == 200:
            ai_response = response.json()
            print("完整API响应:", json.dumps(ai_response, ensure_ascii=False, indent=2))
            
            if ai_response.get("choices") and len(ai_response["choices"]) > 0:
                content = ai_response["choices"][0]["message"]["content"]
                print("AI原始内容:", content)
                
                # 提取JSON部分的更健壮方法
                try:
                    # 尝试找到JSON的开始和结束位置
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_content = content[json_start:json_end]
                        print("提取的JSON内容:", json_content)
                        
                        # 解析JSON
                        result = json.loads(json_content)
                        print("解析后结果:", json.dumps(result, ensure_ascii=False, indent=2))
                        return result
                    else:
                        print("无法找到JSON格式内容")
                        raise Exception("AI响应中未包含有效的JSON格式")
                        
                except json.JSONDecodeError as e:
                    print(f"解析AI响应为JSON失败: {e}")
                    print(f"AI原始响应: {content}")
                    raise Exception(f"AI响应格式错误: {e}")
            else:
                raise Exception("API响应格式不正确，缺少choices字段")
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            raise Exception(f"API请求失败: {response.status_code} - {response.text[:100]}...")
            
    except Exception as e:
        print(f"调用通义千问API失败: {e}")
        import traceback
        traceback.print_exc()
        raise

def call_qwen_text_api(user_message):
    """
    调用通义千问API进行文本聊天
    
    参数:
        user_message (str): 用户文本消息
        
    返回:
        str: AI聊天回复
        
    异常:
        Exception: API调用失败时抛出异常
    """
    try:
        # 发送请求到通义千问API
        response = requests.post(
            QWEN_API_URL,
            json={
                "model": "qwen-turbo",  # 使用文本模型
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个智能商品上架系统，专业、友好地回答用户关于商品上架、销售分析等问题。"
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.95
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {QWEN_API_KEY}"  # 使用Bearer Token认证
            },
            timeout=60
        )
        
        # 解析API响应
        if response.status_code == 200:
            ai_response = response.json()
            print("完整API响应:", json.dumps(ai_response, ensure_ascii=False, indent=2))
            
            if ai_response.get("choices") and len(ai_response["choices"]) > 0:
                content = ai_response["choices"][0]["message"]["content"]
                return content
            else:
                raise Exception("API响应格式不正确，缺少choices字段")
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            raise Exception(f"API请求失败: {response.status_code} - {response.text[:100]}...")
            
    except Exception as e:
        print(f"调用通义千问API失败: {e}")
        import traceback
        traceback.print_exc()
        raise