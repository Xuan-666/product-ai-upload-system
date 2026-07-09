#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品智能上架平台
基于Python的电商辅助工具，支持商品图片识别、文案生成和语音合成
"""

import os
import sys
import base64
import pyttsx3
from tkinter import Tk, Frame, Label, Button, Entry, Text, filedialog, messagebox, Scrollbar, ttk
from PIL import Image, ImageTk
from dotenv import load_dotenv
from ai_utils import call_qwen_api  # 导入统一的AI调用函数

# 加载环境变量
load_dotenv()

class ProductSmartUploader:
    """商品智能上架平台主类"""
    
    def __init__(self, root):
        """初始化应用程序"""
        self.root = root
        self.root.title("商品智能上架平台")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 初始化变量
        self.image_path = None
        self.analyze_result = None
        self.speech_engine = pyttsx3.init()
        
        # 使用ai_utils.py中的统一API配置
        
        # 创建UI界面
        self.create_ui()
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧：图片上传和显示区域
        left_frame = Frame(main_frame, width=400)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 图片上传按钮
        upload_btn = Button(left_frame, text="上传商品图片", command=self.upload_image, 
                          font=("Arial", 12), bg="#4CAF50", fg="white", height=2)
        upload_btn.pack(fill="x", pady=10)
        
        # 图片显示区域
        self.image_label = Label(left_frame, text="请上传商品图片", bg="#f0f0f0", 
                               font=("Arial", 10), relief="sunken")
        self.image_label.pack(fill="both", expand=True, pady=10)
        
        # 分析按钮
        analyze_btn = Button(left_frame, text="智能分析商品", command=self.analyze_product, 
                          font=("Arial", 12), bg="#2196F3", fg="white", height=2)
        analyze_btn.pack(fill="x", pady=10)
        
        # 语音播放按钮
        self.speech_btn = Button(left_frame, text="播放语音介绍", command=self.play_speech, 
                              font=("Arial", 12), bg="#FF9800", fg="white", height=2, state="disabled")
        self.speech_btn.pack(fill="x", pady=10)
        
        # 导出按钮
        self.export_btn = Button(left_frame, text="一键导出文案", command=self.export_content, 
                              font=("Arial", 12), bg="#9C27B0", fg="white", height=2, state="disabled")
        self.export_btn.pack(fill="x", pady=10)
        
        # 右侧：分析结果显示区域
        right_frame = Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 创建标签页
        tab_control = ttk.Notebook(right_frame)
        
        # 商品标题标签页
        self.titles_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.titles_tab, text="商品标题")
        
        # 核心卖点标签页
        self.selling_points_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.selling_points_tab, text="核心卖点")
        
        # 商品描述标签页
        self.description_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.description_tab, text="商品描述")
        
        # 特征标签标签页
        self.features_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.features_tab, text="特征标签")
        
        # 搜索关键词标签页
        self.keywords_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.keywords_tab, text="搜索关键词")
        
        # 商品价格标签页
        self.price_tab = Text(tab_control, wrap="word", font=("Arial", 10))
        tab_control.add(self.price_tab, text="商品价格")
        
        tab_control.pack(fill="both", expand=True)
    
    def upload_image(self):
        """上传商品图片"""
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择商品图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        
        if file_path:
            self.image_path = file_path
            # 显示图片
            self.display_image()
    
    def display_image(self):
        """在界面上显示上传的图片"""
        try:
            # 打开图片并调整大小
            image = Image.open(self.image_path)
            # 计算合适的显示尺寸
            max_width = 380
            max_height = 400
            width, height = image.size
            
            if width > max_width or height > max_height:
                ratio = min(max_width/width, max_height/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # 转换为Tkinter可用的格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新标签
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # 保持引用，防止垃圾回收
            
        except Exception as e:
            messagebox.showerror("错误", f"显示图片失败：{str(e)}")
    
    def call_qwen_api(self, base64_image):
        """调用通义千问API进行商品分析"""
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
                self.QWEN_API_URL,
                json={
                    "model": "qwen-vl-plus",  # 使用支持图像的模型
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    "temperature": 0.7,
                    "top_p": 0.95
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.QWEN_API_KEY}"  # 使用Bearer Token认证
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
    
    def analyze_product(self):
        """分析商品图片，生成营销文案"""
        if not self.image_path:
            messagebox.showwarning("警告", "请先上传商品图片")
            return
        
        try:
            # 显示加载状态
            messagebox.showinfo("提示", "正在分析商品，请稍候...")
            
            # 将图片转换为base64编码
            with open(self.image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
            
            # 直接调用通义千问API
            self.analyze_result = self.call_qwen_api(base64_image)
            
            print("分析结果:", json.dumps(self.analyze_result, ensure_ascii=False, indent=2))
            
            # 显示分析结果
            self.display_result()
            
            # 启用功能按钮
            self.speech_btn.config(state="normal")
            self.export_btn.config(state="normal")
            
            messagebox.showinfo("成功", "商品分析完成！")
                
        except Exception as e:
            print(f"分析过程中出错: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"分析失败：{str(e)}")
    
    def display_result(self):
        """在界面上显示分析结果"""
        print("进入display_result方法，当前analyze_result:")
        print(type(self.analyze_result))
        print(self.analyze_result)
        
        if not self.analyze_result:
            print("analyze_result为空")
            return
        
        # 确保analyze_result是字典类型
        if not isinstance(self.analyze_result, dict):
            print(f"analyze_result不是字典类型，而是{type(self.analyze_result)}")
            raise Exception("分析结果格式错误，预期为字典类型")
        
        print("analyze_result的键:", list(self.analyze_result.keys()))
        
        # 显示商品标题
        self.titles_tab.delete(1.0, "end")
        if "titles" in self.analyze_result:
            print(f"titles字段存在，类型为{type(self.analyze_result['titles'])}")
            print(f"titles内容: {self.analyze_result['titles']}")
            if isinstance(self.analyze_result["titles"], list):
                for i, title in enumerate(self.analyze_result["titles"], 1):
                    self.titles_tab.insert("end", f"{i}. {title}\n\n")
            else:
                self.titles_tab.insert("end", "未生成商品标题：格式错误")
        else:
            self.titles_tab.insert("end", "未生成商品标题")
        
        # 显示核心卖点
        self.selling_points_tab.delete(1.0, "end")
        if "sellingPoints" in self.analyze_result:
            print(f"sellingPoints字段存在，类型为{type(self.analyze_result['sellingPoints'])}")
            print(f"sellingPoints内容: {self.analyze_result['sellingPoints']}")
            if isinstance(self.analyze_result["sellingPoints"], list):
                for i, point in enumerate(self.analyze_result["sellingPoints"], 1):
                    if isinstance(point, dict) and "title" in point and "desc" in point:
                        self.selling_points_tab.insert("end", f"{i}. {point['title']}\n   {point['desc']}\n\n")
                    else:
                        print(f"卖点格式错误: {point}")
            else:
                self.selling_points_tab.insert("end", "未生成核心卖点：格式错误")
        else:
            self.selling_points_tab.insert("end", "未生成核心卖点")
        
        # 显示商品描述
        self.description_tab.delete(1.0, "end")
        if "description" in self.analyze_result:
            print(f"description字段存在，类型为{type(self.analyze_result['description'])}")
            print(f"description内容: {self.analyze_result['description']}")
            if isinstance(self.analyze_result["description"], str):
                self.description_tab.insert("end", self.analyze_result["description"])
            else:
                self.description_tab.insert("end", "未生成商品描述：格式错误")
        else:
            self.description_tab.insert("end", "未生成商品描述")
        
        # 显示特征标签
        self.features_tab.delete(1.0, "end")
        if "features" in self.analyze_result:
            print(f"features字段存在，类型为{type(self.analyze_result['features'])}")
            print(f"features内容: {self.analyze_result['features']}")
            if isinstance(self.analyze_result["features"], list):
                features = ", ".join(self.analyze_result["features"])
                self.features_tab.insert("end", features)
            else:
                self.features_tab.insert("end", "未生成特征标签：格式错误")
        else:
            self.features_tab.insert("end", "未生成特征标签")
        
        # 显示搜索关键词
        self.keywords_tab.delete(1.0, "end")
        if "keywords" in self.analyze_result:
            print(f"keywords字段存在，类型为{type(self.analyze_result['keywords'])}")
            print(f"keywords内容: {self.analyze_result['keywords']}")
            if isinstance(self.analyze_result["keywords"], list):
                for i, keyword in enumerate(self.analyze_result["keywords"], 1):
                    self.keywords_tab.insert("end", f"{i}. {keyword}\n")
            else:
                self.keywords_tab.insert("end", "未生成搜索关键词：格式错误")
        else:
            self.keywords_tab.insert("end", "未生成搜索关键词")
        
        # 显示商品价格
        self.price_tab.delete(1.0, "end")
        if "price" in self.analyze_result:
            print(f"price字段存在，类型为{type(self.analyze_result['price'])}")
            print(f"price内容: {self.analyze_result['price']}")
            if isinstance(self.analyze_result["price"], str):
                self.price_tab.insert("end", self.analyze_result["price"])
            else:
                self.price_tab.insert("end", "未生成商品价格：格式错误")
        else:
            self.price_tab.insert("end", "未生成商品价格")
    
    def play_speech(self):
        """播放语音介绍"""
        if not self.analyze_result or not isinstance(self.analyze_result, dict):
            messagebox.showwarning("警告", "请先分析商品")
            return
        
        try:
            # 准备语音内容
            speech_content = ""
            
            # 添加商品标题
            if "titles" in self.analyze_result and isinstance(self.analyze_result["titles"], list) and self.analyze_result["titles"]:
                speech_content += f"商品标题：{self.analyze_result['titles'][0]}\n"
            
            # 添加商品描述
            if "description" in self.analyze_result and isinstance(self.analyze_result["description"], str):
                speech_content += f"商品描述：{self.analyze_result['description'][:100]}...\n"
            
            # 添加核心卖点
            if "sellingPoints" in self.analyze_result and isinstance(self.analyze_result["sellingPoints"], list):
                speech_content += "核心卖点：\n"
                for point in self.analyze_result["sellingPoints"]:
                    if isinstance(point, dict) and "title" in point and "desc" in point:
                        speech_content += f"{point['title']}，{point['desc'][:50]}...\n"
            
            # 确保有内容才播放
            if speech_content:
                # 播放语音
                self.speech_engine.say(speech_content)
                self.speech_engine.runAndWait()
            else:
                messagebox.showwarning("警告", "没有可播放的语音内容")
                
        except Exception as e:
            messagebox.showerror("错误", f"语音播放失败：{str(e)}")
    
    def export_content(self):
        """一键导出文案"""
        if not self.analyze_result or not isinstance(self.analyze_result, dict):
            messagebox.showwarning("警告", "请先分析商品")
            return
        
        try:
            # 选择导出路径
            export_path = filedialog.asksaveasfilename(
                title="导出文案",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            
            if export_path:
                # 准备导出内容
                export_content = "===== 商品智能上架文案 =====\n\n"
                
                export_content += "【商品标题】\n"
                if "titles" in self.analyze_result and isinstance(self.analyze_result["titles"], list):
                    for i, title in enumerate(self.analyze_result["titles"], 1):
                        export_content += f"{i}. {title}\n"
                else:
                    export_content += "未生成商品标题\n"
                export_content += "\n"
                
                export_content += "【核心卖点】\n"
                if "sellingPoints" in self.analyze_result and isinstance(self.analyze_result["sellingPoints"], list):
                    for i, point in enumerate(self.analyze_result["sellingPoints"], 1):
                        if isinstance(point, dict) and "title" in point and "desc" in point:
                            export_content += f"{i}. {point['title']}\n   {point['desc']}\n"
                else:
                    export_content += "未生成核心卖点\n"
                export_content += "\n"
                
                export_content += "【商品描述】\n"
                if "description" in self.analyze_result and isinstance(self.analyze_result["description"], str):
                    export_content += f"{self.analyze_result['description']}\n"
                else:
                    export_content += "未生成商品描述\n"
                export_content += "\n"
                
                export_content += "【特征标签】\n"
                if "features" in self.analyze_result and isinstance(self.analyze_result["features"], list):
                    export_content += f"{', '.join(self.analyze_result['features'])}\n"
                else:
                    export_content += "未生成特征标签\n"
                export_content += "\n"
                
                export_content += "【搜索关键词】\n"
                if "keywords" in self.analyze_result and isinstance(self.analyze_result["keywords"], list):
                    for i, keyword in enumerate(self.analyze_result["keywords"], 1):
                        export_content += f"{i}. {keyword}\n"
                else:
                    export_content += "未生成搜索关键词\n"
                
                export_content += "\n【商品价格】\n"
                if "price" in self.analyze_result and isinstance(self.analyze_result["price"], str):
                    export_content += f"{self.analyze_result['price']}\n"
                else:
                    export_content += "未生成商品价格\n"
                
                # 写入文件
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write(export_content)
                
                messagebox.showinfo("成功", f"文案已导出到：{export_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

if __name__ == "__main__":
    # 检查是否已安装必要的依赖
    try:
        import PIL
        import requests
        import pyttsx3
        import dotenv
    except ImportError as e:
        missing_module = str(e).split(" ")[-1]
        print(f"缺少必要的依赖模块：{missing_module}")
        print("请运行以下命令安装：")
        print(f"pip install {missing_module}")
        sys.exit(1)
    
    # 创建并运行应用程序
    root = Tk()
    app = ProductSmartUploader(root)
    root.mainloop()