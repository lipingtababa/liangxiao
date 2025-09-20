#!/usr/bin/env python3
"""
Mock翻译服务
用于测试时模拟Google Translate API
"""

import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib
import json


@dataclass
class TranslationResult:
    """翻译结果"""
    text: str
    src: str
    dest: str
    confidence: float = 0.95
    pronunciation: Optional[str] = None


class MockTranslator:
    """Mock翻译器"""

    def __init__(self, delay: float = 0.1, error_rate: float = 0.0):
        """
        初始化Mock翻译器

        Args:
            delay: 模拟网络延迟（秒）
            error_rate: 错误率（0-1之间）
        """
        self.delay = delay
        self.error_rate = error_rate
        self.translation_cache = {}
        self.call_count = 0
        self.error_count = 0

        # 预定义的翻译映射
        self.predefined_translations = {
            # 常见短语
            "瑞典": "Sweden",
            "斯德哥尔摩": "Stockholm",
            "瑞典马工": "Swedish Ma Gong",
            "生活": "life",
            "工作": "work",
            "教育": "education",
            "移民": "immigration",
            "政策": "policy",
            "创业": "entrepreneurship",
            "科技": "technology",
            "文化": "culture",
            "美食": "cuisine",

            # 句子
            "瑞典是一个美丽的国家": "Sweden is a beautiful country",
            "斯德哥尔摩是瑞典的首都": "Stockholm is the capital of Sweden",
            "这里的生活质量很高": "The quality of life here is very high",
            "瑞典的教育系统很完善": "Sweden's education system is well-developed",
            "工作与生活的平衡": "Work-life balance",
        }

    def translate(self, text: str, dest: str = 'en', src: str = 'auto') -> TranslationResult:
        """
        模拟翻译

        Args:
            text: 要翻译的文本
            dest: 目标语言
            src: 源语言（auto表示自动检测）

        Returns:
            翻译结果
        """
        self.call_count += 1

        # 模拟延迟
        if self.delay > 0:
            time.sleep(self.delay)

        # 模拟错误
        if random.random() < self.error_rate:
            self.error_count += 1
            raise Exception("Mock translation service error")

        # 检查缓存
        cache_key = f"{text}:{src}:{dest}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        # 如果源语言是auto，自动检测
        if src == 'auto':
            src = self._detect_language(text)

        # 执行翻译
        if dest == 'en' and src == 'zh-CN':
            translated = self._translate_chinese_to_english(text)
        elif dest == 'zh-CN' and src == 'en':
            translated = self._translate_english_to_chinese(text)
        else:
            # 其他语言对，返回占位文本
            translated = f"[Translated from {src} to {dest}]: {text[:50]}..."

        result = TranslationResult(
            text=translated,
            src=src,
            dest=dest,
            confidence=0.85 + random.random() * 0.15
        )

        # 缓存结果
        self.translation_cache[cache_key] = result

        return result

    def translate_batch(self, texts: List[str], dest: str = 'en', src: str = 'auto') -> List[TranslationResult]:
        """批量翻译"""
        return [self.translate(text, dest, src) for text in texts]

    def _detect_language(self, text: str) -> str:
        """检测语言"""
        # 简单的语言检测逻辑
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_chars = sum(1 for char in text if 'a' <= char.lower() <= 'z')

        if chinese_chars > english_chars:
            return 'zh-CN'
        elif english_chars > 0:
            return 'en'
        else:
            return 'auto'

    def _translate_chinese_to_english(self, text: str) -> str:
        """中文翻译成英文"""
        # 检查预定义翻译
        if text in self.predefined_translations:
            return self.predefined_translations[text]

        # 简单的词对词翻译
        translated = text
        for chinese, english in self.predefined_translations.items():
            translated = translated.replace(chinese, english)

        # 如果没有找到翻译，生成mock翻译
        if translated == text:
            # 基于文本哈希生成确定性的翻译
            hash_val = hashlib.md5(text.encode()).hexdigest()[:8]
            translated = f"Translation of '{text[:20]}...' (mock_{hash_val})"

        return translated

    def _translate_english_to_chinese(self, text: str) -> str:
        """英文翻译成中文"""
        # 反向查找预定义翻译
        reverse_translations = {v: k for k, v in self.predefined_translations.items()}

        if text in reverse_translations:
            return reverse_translations[text]

        # 简单的词对词翻译
        translated = text
        for english, chinese in reverse_translations.items():
            translated = translated.replace(english, chinese)

        # 如果没有找到翻译，生成mock翻译
        if translated == text:
            hash_val = hashlib.md5(text.encode()).hexdigest()[:8]
            translated = f"「{text[:20]}...」的翻译 (mock_{hash_val})"

        return translated

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "call_count": self.call_count,
            "error_count": self.error_count,
            "cache_size": len(self.translation_cache),
            "error_rate": self.error_count / self.call_count if self.call_count > 0 else 0
        }

    def reset(self):
        """重置翻译器状态"""
        self.translation_cache.clear()
        self.call_count = 0
        self.error_count = 0


class MockTranslationService:
    """Mock翻译服务（模拟完整的翻译API）"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化翻译服务

        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.translator = MockTranslator(
            delay=self.config.get('delay', 0.1),
            error_rate=self.config.get('error_rate', 0.0)
        )
        self.api_key = self.config.get('api_key', 'mock_api_key')
        self.rate_limit = self.config.get('rate_limit', 100)  # 每秒请求限制
        self.last_request_time = 0
        self.request_count = 0

    def translate_text(self, text: str, target_language: str = 'en',
                      source_language: str = 'auto') -> Dict[str, Any]:
        """
        翻译文本（模拟API响应格式）

        Args:
            text: 要翻译的文本
            target_language: 目标语言代码
            source_language: 源语言代码

        Returns:
            API响应格式的字典
        """
        # 检查速率限制
        current_time = time.time()
        if current_time - self.last_request_time < 1.0:
            self.request_count += 1
            if self.request_count > self.rate_limit:
                return {
                    "error": {
                        "code": 429,
                        "message": "Rate limit exceeded"
                    }
                }
        else:
            self.request_count = 1
            self.last_request_time = current_time

        try:
            result = self.translator.translate(text, target_language, source_language)
            return {
                "data": {
                    "translations": [{
                        "translatedText": result.text,
                        "detectedSourceLanguage": result.src,
                        "model": "mock",
                        "confidence": result.confidence
                    }]
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": 500,
                    "message": str(e)
                }
            }

    def translate_batch(self, texts: List[str], target_language: str = 'en',
                       source_language: str = 'auto') -> Dict[str, Any]:
        """批量翻译文本"""
        try:
            results = self.translator.translate_batch(texts, target_language, source_language)
            return {
                "data": {
                    "translations": [
                        {
                            "translatedText": result.text,
                            "detectedSourceLanguage": result.src,
                            "model": "mock",
                            "confidence": result.confidence
                        }
                        for result in results
                    ]
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": 500,
                    "message": str(e)
                }
            }

    def detect_language(self, text: str) -> Dict[str, Any]:
        """检测语言"""
        detected = self.translator._detect_language(text)
        return {
            "data": {
                "detections": [[{
                    "language": detected,
                    "isReliable": True,
                    "confidence": 0.95
                }]]
            }
        }

    def get_supported_languages(self, target: str = 'en') -> Dict[str, Any]:
        """获取支持的语言列表"""
        return {
            "data": {
                "languages": [
                    {"language": "en", "name": "English"},
                    {"language": "zh-CN", "name": "Chinese (Simplified)"},
                    {"language": "sv", "name": "Swedish"},
                    {"language": "fr", "name": "French"},
                    {"language": "de", "name": "German"},
                    {"language": "es", "name": "Spanish"},
                    {"language": "ja", "name": "Japanese"},
                    {"language": "ko", "name": "Korean"}
                ]
            }
        }


class TranslationTestHelper:
    """翻译测试辅助类"""

    @staticmethod
    def create_test_article(language: str = 'zh-CN') -> Dict[str, str]:
        """创建测试文章"""
        if language == 'zh-CN':
            return {
                "title": "瑞典生活指南",
                "content": """
                瑞典是一个位于北欧的美丽国家。斯德哥尔摩是瑞典的首都，
                也是最大的城市。这里的生活质量很高，社会福利完善。
                瑞典的教育系统世界闻名，从幼儿园到大学都是免费的。
                工作与生活的平衡是瑞典文化的重要组成部分。
                """,
                "author": "瑞典马工"
            }
        elif language == 'en':
            return {
                "title": "Guide to Living in Sweden",
                "content": """
                Sweden is a beautiful country located in Northern Europe. Stockholm is the capital of Sweden,
                and also the largest city. The quality of life here is very high, with comprehensive social welfare.
                Sweden's education system is world-renowned, free from kindergarten to university.
                Work-life balance is an important part of Swedish culture.
                """,
                "author": "Swedish Ma Gong"
            }
        else:
            return {
                "title": f"Test Article in {language}",
                "content": f"Test content in {language}",
                "author": "Test Author"
            }

    @staticmethod
    def create_batch_test_data(count: int = 10, language: str = 'zh-CN') -> List[Dict[str, str]]:
        """创建批量测试数据"""
        articles = []
        for i in range(count):
            if language == 'zh-CN':
                article = {
                    "title": f"测试文章{i+1}",
                    "content": f"这是第{i+1}篇测试文章的内容。",
                    "author": "测试作者"
                }
            else:
                article = {
                    "title": f"Test Article {i+1}",
                    "content": f"This is the content of test article {i+1}.",
                    "author": "Test Author"
                }
            articles.append(article)
        return articles

    @staticmethod
    def verify_translation(original: str, translated: str,
                         source_lang: str = 'zh-CN', target_lang: str = 'en') -> bool:
        """验证翻译结果"""
        # 基本验证
        if not translated:
            return False

        # 确保翻译后的文本不同于原文
        if translated == original:
            return False

        # 检查语言特征
        if target_lang == 'en' and source_lang == 'zh-CN':
            # 翻译成英文后不应该包含中文字符
            chinese_chars = sum(1 for char in translated if '\u4e00' <= char <= '\u9fff')
            if chinese_chars > 0:
                return False

        return True


# 创建全局mock实例
default_mock_translator = MockTranslator()
default_mock_service = MockTranslationService()


def mock_translate(text: str, dest: str = 'en', src: str = 'auto') -> str:
    """便捷的mock翻译函数"""
    result = default_mock_translator.translate(text, dest, src)
    return result.text


if __name__ == '__main__':
    # 测试示例
    translator = MockTranslator()

    # 测试中文到英文
    chinese_text = "瑞典是一个美丽的国家"
    result = translator.translate(chinese_text, 'en', 'zh-CN')
    print(f"中文: {chinese_text}")
    print(f"英文: {result.text}")
    print(f"置信度: {result.confidence:.2f}")

    # 测试英文到中文
    english_text = "Sweden is a beautiful country"
    result = translator.translate(english_text, 'zh-CN', 'en')
    print(f"\n英文: {english_text}")
    print(f"中文: {result.text}")

    # 测试批量翻译
    texts = ["瑞典", "斯德哥尔摩", "生活", "工作"]
    results = translator.translate_batch(texts)
    print(f"\n批量翻译:")
    for text, result in zip(texts, results):
        print(f"  {text} -> {result.text}")

    # 显示统计
    stats = translator.get_statistics()
    print(f"\n统计信息:")
    print(f"  调用次数: {stats['call_count']}")
    print(f"  缓存大小: {stats['cache_size']}")

    # 测试API服务
    service = MockTranslationService()
    api_result = service.translate_text("测试文本", 'en', 'zh-CN')
    print(f"\nAPI响应:")
    print(json.dumps(api_result, ensure_ascii=False, indent=2))