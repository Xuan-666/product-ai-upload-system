import os
import edge_tts
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SpeechSynthesizer:
    def __init__(self):
        self.voice = "zh-CN-XiaoxiaoNeural"  # 默认使用中文晓晓语音
        self.rate = "+0%"  # 语速正常
        self.pitch = "+0Hz"  # 音调正常
    
    async def synthesize_text(self, text, output_path):
        """使用edge-tts合成语音"""
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            await communicate.save(output_path)
            return {
                "success": True,
                "audio_path": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"语音合成失败：{str(e)}"
            }
    
    def set_voice(self, voice):
        """设置语音类型"""
        self.voice = voice
    
    def set_rate(self, rate):
        """设置语速，如 "+10%" 或 "-5%"""
        self.rate = rate
    
    def set_pitch(self, pitch):
        """设置音调，如 "+5Hz" 或 "-3Hz"""
        self.pitch = pitch
    
    def generate_product_speech(self, product_info, output_path):
        """生成商品语音介绍"""
        try:
            # 构建语音文案
            speech_text = self._build_speech_text(product_info)
            
            # 执行语音合成
            result = asyncio.run(self.synthesize_text(speech_text, output_path))
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成商品语音失败：{str(e)}"
            }
    
    def _build_speech_text(self, product_info):
        """构建语音合成的文本内容"""
        product_name = product_info.get('product_name', '商品')
        description = product_info.get('description', '')
        features = product_info.get('features', [])
        
        # 构建语音文案
        speech_text = f"欢迎选购{product_name}！"
        
        if description:
            # 从描述中提取关键信息
            speech_text += description[:200]  # 限制长度
        
        if features:
            speech_text += "\n\n本商品的主要特点有："
            for i, feature in enumerate(features[:3], 1):  # 只取前3个特点
                speech_text += f"\n{i}. {feature}"
        
        speech_text += "\n\n品质保证，欢迎购买！"
        
        return speech_text

# 测试代码
if __name__ == "__main__":
    synthesizer = SpeechSynthesizer()
    
    # 示例商品信息
    product_info = {
        "product_name": "新鲜青苹果",
        "description": "这是来自山东烟台的新鲜青苹果，口感脆甜，富含维生素C，绿色健康。",
        "features": ["脆甜可口", "富含维生素C", "绿色健康", "产地直供"]
    }
    
    output_path = "test_audio.mp3"
    
    print("开始生成商品语音...")
    result = synthesizer.generate_product_speech(product_info, output_path)
    
    if result['success']:
        print(f"语音生成成功，保存路径：{result['audio_path']}")
    else:
        print(f"语音生成失败：{result['error']}")
