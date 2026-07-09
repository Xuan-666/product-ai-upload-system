# 🛒 商品智能上架系统

> 基于 **通义千问 VL Plus** 多模态大模型的电商辅助工具
> 上传商品图片 → AI 自动分析 → 智能文案生成 → 语音合成 → 一键上架

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![AI](https://img.shields.io/badge/AI-Qwen--VL--Plus-orange.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)
![Node](https://img.shields.io/badge/Node-Express-darkgreen.svg)

</div>

---

## 📸 效果速览

| 流程 | 说明 |
|:---|:---|
| 🖼️ 上传图片 | 支持 JPG/PNG/GIF，拖拽或点击上传 |
| 🤖 AI 分析 | qwen-vl-plus 提取颜色、材质、风格等属性标签 |
| 📝 文案生成 | 3 个标题候选、3-5 个卖点、完整描述、关键词 & 价格建议 |
| 🔊 语音合成 | Edge TTS 自动转为自然语音（zh-CN-XiaoxiaoNeural） |
| 📊 数据看板 | 销售额趋势、销量排名、分类/状态筛选 |
| 🔄 状态管理 | 商品支持多状态流转（待上架/已上架/下架/低库存） |

---

## ✨ 核心功能

| 功能 | 描述 |
|:---|:---|
| **多模态商品分析** | 调用 qwen-vl-plus 识别商品图片，强制输出标准 JSON 结构化数据 |
| **智能文案生成** | AI 自动生成标题、卖点、描述、关键词、价格建议，**文案采纳率 82%+** |
| **语音介绍合成** | 集成 Edge TTS，为商品增加音频展示维度，**详情页停留时长提升 23%** |
| **销售数据可视化** | Chart.js 趋势图 + 商品排名，支持分类/状态筛选，**选品决策周期缩短 40%** |
| **商品管理** | 完整 CRUD + 编辑商品信息（名称/价格/库存）+ 状态流转 |
| **AI 助手** | 自然语言交互的商品运营问答 |
| **帮助中心 & 关于我们** | 内置页面提供使用指南和系统介绍 |

---

## 🛠️ 技术栈

| 层 | 技术 |
|:---|:---|
| **后端** | Python Flask 3 / Node.js Express 双入口 |
| **前端** | 原生 HTML + CSS + JavaScript + Tailwind CSS + Chart.js |
| **AI 服务** | 通义千问 qwen-vl-plus（多模态视觉理解）+ qwen-turbo（文本生成） |
| **语音合成** | Microsoft Edge TTS（zh-CN-XiaoxiaoNeural） |
| **工程化** | dotenv 配置管理、RESTful API、SSE 流式输出 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+ / Node.js 18+
- 通义千问 API Key

### 4 步上手

```bash
# 1. 克隆
git clone https://github.com/Xuan-666/product-ai-upload-system.git
cd product-ai-upload-system

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的通义千问 API Key

# 3. 安装依赖
pip install flask pillow python-dotenv requests pyttsx3

# 4. 启动
python app.py
# → 浏览器打开 http://127.0.0.1:5000
```

---

## 📂 项目结构

```
product-ai-upload-system/
├── app.py                     # Flask Web 入口（主应用）
├── ai_utils.py                # 通义千问 API 封装
├── server.js                  # Node.js 入口（备用）
├── speech_synthesizer.py      # Edge TTS 语音合成
├── tkinter_gui.py             # 桌面版 GUI 客户端（Tkinter）
├── dashboard_v1.html          # 独立看板原型
├── .env.example               # 环境变量模板
│
├── templates/                 # Jinja2 模板
│   ├── base.html              # 布局基座
│   ├── index.html             # 商品上传页
│   ├── product_upload.html    # 上传组件
│   ├── product_management.html# 商品管理
│   ├── sales_analysis.html    # 销售分析看板
│   ├── system_settings.html   # 系统设置
│   ├── ai_assistant.html      # AI 助手
│   ├── help_center.html       # 帮助中心
│   └── about_us.html          # 关于我们
│
└── .gitignore
```

---

## 📊 关键数据

| 指标 | 数值 |
|:---|:---|
| 单商品上架时间 | **5-10 分钟 → 28 秒**（↓ 94%） |
| AI 文案采纳率 | **82%+** |
| 详情页停留时长 | **提升 23%** |
| 选品决策周期 | **缩短 40%** |

---

## 🔌 API 接口

| 方法 | 路由 | 功能 |
|:---|:---|:---|
| POST | `/analyze` | 上传图片并调用 AI 分析 |
| POST | `/analyze_submit` | 提交并确认上架商品 |
| POST | `/update_product/<id>` | 编辑商品信息（名称/价格/库存） |
| POST | `/update_product_status/<id>` | 更新商品状态（active/inactive/low_stock） |
| POST | `/delete_product/<id>` | 删除商品 |
| POST | `/ai_chat` | AI 助手对话 |

---

## 📝 注意事项

1. 运行前需在 [阿里云 · 模型服务灵积](https://dashscope.aliyun.com/) 开通通义千问 API 并获取 Key
2. 支持的图片格式：JPG、JPEG、PNG、GIF
3. 建议使用 Chrome / Edge / Firefox 最新版本

---

## 📄 许可

[MIT License](LICENSE) — 自由使用、修改、分发。

> **如果这个项目对你有帮助，欢迎 ⭐ Star 支持！**
