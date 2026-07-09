#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品智能上架平台 - Flask后端
基于Python的电商辅助工具,支持商品图片识别、文案生成和语音合成
"""

import os
import sys
import base64
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from PIL import Image
from dotenv import load_dotenv
from ai_utils import call_qwen_api, call_qwen_text_api  # 导入统一的AI调用函数
from speech_synthesizer import SpeechSynthesizer  # 导入语音合成模块

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于会话管理

# 配置上传文件夹
UPLOAD_FOLDER = os.path.abspath('uploads')  # 使用绝对路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 配置音频文件夹
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# 存储商品数据的全局变量（实际项目中应使用数据库）
products = []
product_id_counter = 1

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 主页路由
@app.route('/')
def index():
    """主页"""
    filename = session.get('filename')
    analyze_result = session.get('analyze_result')
    error = request.args.get('error')
    return render_template('index.html', filename=filename, product_info=analyze_result, error=error)

# 图片上传路由
@app.route('/upload', methods=['POST'])
def upload_image():
    """处理图片上传"""
    if 'image' not in request.files:
        return redirect(url_for('index', error='未选择文件'))
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(url_for('index', error='未选择文件'))
    
    if file and allowed_file(file.filename):
        # 保存文件
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 将图片转换为base64编码
        with open(filepath, "rb") as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
        
        # 调用通义千问API
        try:
            analyze_result = call_qwen_api(base64_image)
            
            # 保存分析结果到会话
            session['analyze_result'] = analyze_result
            session['filename'] = filename
            
            return redirect(url_for('index'))
        except Exception as e:
            return redirect(url_for('index', error=f'分析失败: {str(e)}'))
    else:
        return redirect(url_for('index', error='文件类型不允许'))

# 这些路由已合并到index.html中，不再需要单独的页面
# # 商品标题页面
# @app.route('/titles')
# def titles():
#     """商品标题页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('titles.html', result=analyze_result)

# # 核心卖点页面
# @app.route('/selling_points')
# def selling_points():
#     """核心卖点页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('selling_points.html', result=analyze_result)

# # 商品描述页面
# @app.route('/description')
# def description():
#     """商品描述页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('description.html', result=analyze_result)

# # 特征标签页面
# @app.route('/features')
# def features():
#     """特征标签页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('features.html', result=analyze_result)

# # 搜索关键词页面
# @app.route('/keywords')
# def keywords():
#     """搜索关键词页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('keywords.html', result=analyze_result)

# # 商品价格页面
# @app.route('/price')
# def price():
#     """商品价格页面"""
#     analyze_result = session.get('analyze_result')
#     return render_template('price.html', result=analyze_result)

# 商品管理页面
@app.route('/product_management')
def product_management():
    """商品管理页面"""
    # 获取URL参数
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    # 过滤商品列表
    filtered_products = products
    
    if search:
        filtered_products = [p for p in filtered_products if search.lower() in p['name'].lower() or search in p['sku']]
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    if status:
        filtered_products = [p for p in filtered_products if p['status'] == status]
    
    # 分页逻辑
    per_page = 4  # 每页显示4个商品
    total = len(filtered_products)
    total_pages = (total + per_page - 1) // per_page  # 计算总页数
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = filtered_products[start:end]
    
    return render_template('product_management.html', 
                           products=paginated_products, 
                           total=total, 
                           page=page, 
                           per_page=per_page, 
                           total_pages=total_pages,
                           search=search, 
                           category=category, 
                           status=status)

# 删除商品路由
@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除指定ID的商品"""
    global products
    # 从商品列表中删除指定ID的商品
    products = [p for p in products if p['id'] != product_id]
    return jsonify({'success': True, 'message': '商品删除成功'})

# 更新商品信息路由
@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    """更新指定ID的商品信息"""
    global products
    
    # 查找商品
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False, 'message': '商品不存在'}), 404
    
    # 获取更新数据
    data = request.json
    if 'name' in data:
        product['name'] = data['name']
    if 'price' in data:
        product['price'] = data['price']
    if 'stock' in data:
        product['stock'] = data['stock']
    
    return jsonify({'success': True, 'message': '商品信息更新成功'})

# 更新商品状态路由
@app.route('/update_product_status/<int:product_id>', methods=['POST'])
def update_product_status(product_id):
    """更新指定ID的商品状态"""
    global products
    
    # 查找商品
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False, 'message': '商品不存在'}), 404
    
    # 获取新状态
    data = request.json
    new_status = data.get('status')
    
    if new_status in ['active', 'inactive', 'low_stock']:
        product['status'] = new_status
        return jsonify({'success': True, 'message': '商品状态更新成功'})
    else:
        return jsonify({'success': False, 'message': '无效的状态值'}), 400

# 商品上传页面
@app.route('/product_upload')
def product_upload():
    """商品上传页面"""
    return render_template('product_upload.html')

# 商品上架处理路由
@app.route('/product_upload', methods=['POST'])
def product_upload_post():
    """处理商品上架表单提交"""
    global product_id_counter
    try:
        # 获取表单数据
        product_name = request.form.get('product_name')
        product_category = request.form.get('product_category')
        product_price = request.form.get('product_price')
        product_stock = request.form.get('product_stock')
        product_description = request.form.get('product_description')
        product_tags = request.form.get('product_tags')
        
        # 获取上传的图片
        images = request.files.getlist('images')
        
        # 验证必要字段
        if not all([product_name, product_category, product_price, product_stock]):
            return redirect(url_for('product_upload', error='请填写所有必填字段'))
        
        # 处理图片上传
        uploaded_images = []
        main_image = None
        for image in images:
            if image and allowed_file(image.filename):
                # 保存图片到uploads文件夹
                filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filename)
                uploaded_images.append(image.filename)
                # 设置第一张图片为主图
                if not main_image:
                    main_image = image.filename
        
        # 创建商品对象
        product = {
            'id': product_id_counter,
            'name': product_name,
            'price': float(product_price),
            'stock': int(product_stock),
            'category': product_category,
            'status': 'active',  # 默认状态为上架
            'sku': f'SP{product_id_counter:03d}',
            'image': main_image,
            'description': product_description
        }
        
        # 添加到商品列表
        products.append(product)
        product_id_counter += 1
        
        # 保存成功后重定向到商品管理页面
        return redirect(url_for('product_management', success='商品上架成功'))
        
    except Exception as e:
        # 处理异常
        return redirect(url_for('product_upload', error=f'上架失败：{str(e)}'))

# 销售分析页面
@app.route('/sales_analysis')
def sales_analysis():
    """销售分析页面"""
    return render_template('sales_analysis.html')

# 系统设置页面
@app.route('/system_settings')
def system_settings():
    """系统设置页面"""
    return render_template('system_settings.html')

# AI助手页面
@app.route('/ai_assistant')
def ai_assistant():
    """AI助手页面"""
    return render_template('ai_assistant.html')

# 帮助中心页面
@app.route('/help_center')
def help_center():
    """帮助中心页面"""
    return render_template('help_center.html')

# 关于我们页面
@app.route('/about_us')
def about_us():
    """关于我们页面"""
    return render_template('about_us.html')

# AI助手API路由
@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    """处理AI助手的聊天请求"""
    try:
        # 获取用户消息
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 调用通义千问API
        try:
            # 使用ai_utils中的call_qwen_text_api函数调用API
            response = call_qwen_text_api(user_message)
            
            # 格式化返回结果
            return jsonify({
                'success': True,
                'message': response
            })
        except Exception as e:
            # 如果API调用失败，返回模拟回复
            return jsonify({
                'success': True,
                'message': f'非常抱歉，AI服务暂时不可用。您的问题是："{user_message}"。\n\n建议您稍后再试，或者查看常见问题解答。'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 保存修改的路由
@app.route('/save_modifications', methods=['POST'])
def save_modifications():
    """保存分析结果的修改并上架商品"""
    global product_id_counter
    
    # 获取表单数据
    product_name = request.form.get('product_name')
    titles = request.form.getlist('titles[]')
    description = request.form.get('description')
    selling_points = request.form.getlist('selling_points[]')
    price = request.form.get('price')
    product_category = request.form.get('product_category', 'electronics')
    stock_quantity = request.form.get('stock_quantity', '100')
    tags = request.form.getlist('tags[]')
    
    # 获取当前的分析结果
    analyze_result = session.get('analyze_result', {})
    
    # 更新分析结果
    if product_name:
        analyze_result['titles'] = analyze_result.get('titles', [])
        if analyze_result['titles']:
            analyze_result['titles'][0] = product_name
        else:
            analyze_result['titles'] = [product_name]
    
    if titles:
        analyze_result['titles'] = titles
    
    if description:
        analyze_result['description'] = description
    
    if selling_points:
        analyze_result['sellingPoints'] = [{'title': point} for point in selling_points]
    
    if price:
        analyze_result['price'] = price
    
    if product_category:
        analyze_result['category'] = product_category
    
    if tags:
        analyze_result['features'] = tags
    
    # 保存更新后的结果到会话
    session['analyze_result'] = analyze_result
    
    # 创建商品对象并上架到商品管理页面
    if product_name and price:
        product = {
            'id': product_id_counter,
            'name': product_name,
            'price': price,
            'stock': int(stock_quantity),
            'category': product_category,
            'status': 'active',
            'sku': f'SP{product_id_counter:03d}',
            'image': session.get('filename'),
            'description': description
        }
        
        # 添加到商品列表
        products.append(product)
        product_id_counter += 1
    
    return redirect(url_for('product_management'))

# 获取上传的文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """返回上传的文件"""
    # 确保只返回上传文件夹中的文件，防止目录遍历攻击
    safe_filename = os.path.basename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)

# 语音合成路由
@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    """
    生成商品语音介绍
    """
    try:
        # 获取商品信息
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        features = request.form.getlist('features[]')
        selling_points = request.form.getlist('selling_points[]')
        
        # 如果没有获取到特征，可以使用卖点
        if not features and selling_points:
            features = selling_points
        
        # 创建商品信息字典
        product_info = {
            'product_name': product_name,
            'description': description,
            'features': features
        }
        
        # 生成唯一的音频文件名
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        
        # 初始化语音合成器
        synthesizer = SpeechSynthesizer()
        
        # 生成语音
        result = synthesizer.generate_product_speech(product_info, audio_path)
        
        if result['success']:
            # 获取当前的分析结果
            analyze_result = session.get('analyze_result', {})
            
            # 更新分析结果，添加音频文件名
            analyze_result['audio_filename'] = audio_filename
            session['analyze_result'] = analyze_result
            
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index', error=f'语音生成失败：{result["error"]}'))
            
    except Exception as e:
        return redirect(url_for('index', error=f'语音生成失败：{str(e)}'))

# 销售数据导出路由
@app.route('/export_sales_data')
def export_sales_data():
    """
    导出销售数据为CSV文件
    
    返回:
        CSV文件下载
    """
    import csv
    from io import StringIO
    
    # 生成模拟销售数据
    sales_data = []
    for i in range(1, 11):
        sales_data.append({
            'order_id': f'ORD-{20240000 + i}',
            'product_name': f'智能手表 Pro {i}',
            'category': '电子数码',
            'price': 1500 + (i * 100),
            'quantity': 2 + i,
            'amount': (1500 + (i * 100)) * (2 + i),
            'status': '已完成'
        })
    
    # 创建CSV文件
    csv_buffer = StringIO()
    fieldnames = ['订单编号', '商品名称', '分类', '单价', '数量', '销售额', '状态']
    
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    # 写入数据
    for row in sales_data:
        writer.writerow({
            '订单编号': row['order_id'],
            '商品名称': row['product_name'],
            '分类': row['category'],
            '单价': f'¥{row["price"]}',
            '数量': row['quantity'],
            '销售额': f'¥{row["amount"]}',
            '状态': row['status']
        })
    
    # 在Windows系统中，CSV文件需要使用UTF-8-BOM编码才能正确显示中文
    csv_content = '\ufeff' + csv_buffer.getvalue()
    
    # 设置响应头
    response = app.response_class(
        response=csv_content,
        status=200,
        mimetype='text/csv; charset=utf-8'
    )
    
    # 添加下载头
    response.headers.set(
        'Content-Disposition',
        'attachment',
        filename=f'sales_data_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
    
    return response

if __name__ == "__main__":
    # 检查是否已安装必要的依赖
    try:
        import PIL
        import requests
        import pyttsx3
        import dotenv
        import flask
    except ImportError as e:
        missing_module = str(e).split(" ")[-1]
        print(f"缺少必要的依赖模块：{missing_module}")
        print("请运行以下命令安装：")
        print(f"pip install {missing_module}")
        sys.exit(1)
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)