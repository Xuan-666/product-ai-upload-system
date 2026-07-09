const express = require('express');
const multer = require('multer');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

// 创建Express应用
const app = express();

// 配置CORS，允许前端跨域请求
app.use(cors());

// 配置Multer，用于处理文件上传
const storage = multer.memoryStorage(); // 暂时存储在内存中
const upload = multer({ storage: storage });

// 通义千问API配置
const API_KEY = process.env.QWEN_API_KEY || '“⚠️ 请替换为你的通义千问 API Key，例如 sk-xxxx”'; // 使用用户提供的API Key作为默认值
const API_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';

/**
 * 调用通义千问API进行商品分析
 * @param {string} imageBase64 图片的Base64编码
 * @returns {Promise<Object>} AI分析结果
 */
async function analyzeProduct(imageBase64) {
    try {
        // 构建API请求参数
    const prompt = `请分析这张商品图片，严格按照以下要求生成内容：
1. 首先仔细识别图片中所有可见的文字信息，特别是商品名称、标题等关键文字
2. 基于识别到的文字内容进行分析，确保生成的内容与图片中的文字信息一致
3. 生成以下内容：
   - 商品特征标签（5-10个关键词）
   - 核心卖点（3-5个要点）
   - 商品描述（100-200字）
   - 3个不同风格的商品标题
   - 5个搜索关键词推荐

请按照以下JSON格式返回结果：
{
  "features": ["标签1", "标签2", ...],
  "sellingPoints": [{"title": "卖点标题1", "desc": "卖点描述1"}, ...],
  "description": "商品描述...",
  "titles": ["标题1", "标题2", "标题3"],
  "keywords": ["关键词1", "关键词2", ...]
}`;
        
        // 发送请求到通义千问API
        const response = await axios.post(API_URL, {
            model: "qwen-plus", // 使用qwen-plus模型
            messages: [
                {
                    role: "user",
                    content: [
                        { type: "text", text: prompt },
                        { type: "image_url", image_url: { url: `data:image/jpeg;base64,${imageBase64}` } }
                    ]
                }
            ],
            temperature: 0.7,
            top_p: 0.95
        }, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${API_KEY}` // 使用Bearer Token认证
            }
        });
        
        // 解析API响应
        let aiResponse = response.data.choices[0].message.content;
        
        // 去除Markdown代码块标记（如果存在）
        aiResponse = aiResponse.replace(/^```json\n/, '').replace(/```$/, '').trim();
        
        // 尝试将响应解析为JSON
        try {
            return JSON.parse(aiResponse);
        } catch (parseError) {
            console.error('解析AI响应为JSON失败:', parseError);
            console.error('AI原始响应:', response.data.choices[0].message.content);
            console.error('处理后响应:', aiResponse);
            throw new Error('AI响应格式错误');
        }
    } catch (error) {
        console.error('调用通义千问API失败:', error);
        console.error('错误详情:', error.response ? error.response.data : error.message);
        throw error;
    }
}

// 定义API路由

// 根路径路由
app.get('/', (req, res) => {
    res.json({
        message: '商品智能上架系统 - 后端API服务器',
        status: 'running',
        api_endpoints: {
            health: '/api/health',
            analyze: '/api/analyze'
        },
        description: '用于商品图片智能分析的后端服务，基于通义千问API'
    });
});

// 健康检查路由
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: '服务器运行正常' });
});

// 商品分析路由
app.post('/api/analyze', upload.single('image'), async (req, res) => {
    try {
        // 检查是否有文件上传
        if (!req.file) {
            return res.status(400).json({ error: '没有上传文件' });
        }
        
        // 将图片转换为Base64编码
        const imageBase64 = req.file.buffer.toString('base64');
        
        // 调用AI分析
        const result = await analyzeProduct(imageBase64);
        
        // 返回分析结果
        res.json({ success: true, data: result });
    } catch (error) {
        console.error('分析商品失败:', error);
        res.status(500).json({ success: false, error: error.message || '分析失败，请重试' });
    }
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`服务器运行在 http://localhost:${PORT}`);
    console.log('API端点:');
    console.log(`  - 健康检查: http://localhost:${PORT}/api/health`);
    console.log(`  - 商品分析: http://localhost:${PORT}/api/analyze`);
});