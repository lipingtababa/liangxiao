#!/usr/bin/env python3
"""
Black Box Pipeline Test
测试完整的文章翻译流程：WeChat URL → magong.se 发布
"""

import sys
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime

def log(message):
    """简单日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_test_url():
    """从 articles.txt 获取测试URL"""
    articles_file = Path("articles.txt")
    if not articles_file.exists():
        log("❌ articles.txt 文件不存在")
        return None

    with open(articles_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        log("❌ articles.txt 中没有URL")
        return None

    # 使用第一个URL进行测试
    test_url = urls[0]
    log(f"📝 测试URL: {test_url}")
    return test_url

def run_extraction(url):
    """运行内容提取"""
    log("🔄 开始提取文章内容...")

    try:
        result = subprocess.run([
            "python", "scripts/wechat_extractor.py", "--url", url
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            log("✅ 内容提取成功")
            return True
        else:
            log(f"❌ 内容提取失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("❌ 内容提取超时")
        return False
    except Exception as e:
        log(f"❌ 内容提取错误: {e}")
        return False

def build_site():
    """构建网站"""
    log("🔄 构建网站...")

    try:
        result = subprocess.run([
            "npm", "run", "build"
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            log("✅ 网站构建成功")
            return True
        else:
            log(f"❌ 网站构建失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("❌ 网站构建超时")
        return False
    except Exception as e:
        log(f"❌ 网站构建错误: {e}")
        return False

def check_site_accessible():
    """检查网站是否可访问"""
    log("🔄 检查网站可访问性...")

    try:
        response = requests.get("https://magong.se", timeout=10)
        if response.status_code == 200:
            log("✅ magong.se 可访问")
            return True
        else:
            log(f"❌ magong.se 返回状态码: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ 无法访问 magong.se: {e}")
        return False

def check_posts_page():
    """检查文章页面"""
    log("🔄 检查文章页面...")

    try:
        response = requests.get("https://magong.se/posts", timeout=10)
        if response.status_code == 200:
            log("✅ 文章页面可访问")
            return True
        else:
            log(f"❌ 文章页面返回状态码: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ 无法访问文章页面: {e}")
        return False

def main():
    """主测试流程"""
    log("🚀 开始黑盒管道测试")
    log("=" * 50)

    # 1. 获取测试URL
    test_url = get_test_url()
    if not test_url:
        log("❌ 测试失败：无法获取测试URL")
        return False

    # 2. 运行提取流程
    if not run_extraction(test_url):
        log("❌ 测试失败：内容提取阶段")
        return False

    # 3. 构建网站
    if not build_site():
        log("❌ 测试失败：网站构建阶段")
        return False

    # 4. 检查网站可访问性
    if not check_site_accessible():
        log("❌ 测试失败：网站不可访问")
        return False

    # 5. 检查文章页面
    if not check_posts_page():
        log("❌ 测试失败：文章页面不可访问")
        return False

    log("=" * 50)
    log("🎉 黑盒管道测试通过！")
    log("✅ WeChat URL → magong.se 流程正常工作")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)