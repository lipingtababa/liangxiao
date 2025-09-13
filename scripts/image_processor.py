#!/usr/bin/env python3
"""
图片下载和处理模块
Image Download and Processing Module

负责从微信文章下载图片并进行优化处理
Responsible for downloading and optimizing images from WeChat articles
"""

import os
import hashlib
import logging
from typing import Optional, Tuple, List
from urllib.parse import urlparse, unquote
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import re

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器类"""

    def __init__(self, download_path: Optional[str] = None):
        """
        初始化图片处理器

        Args:
            download_path: 图片下载路径，默认从环境变量读取
        """
        self.download_path = download_path or os.getenv('IMAGE_DOWNLOAD_PATH', './public/images')
        self.quality = int(os.getenv('IMAGE_QUALITY', 85))
        self.max_width = int(os.getenv('MAX_IMAGE_WIDTH', 1200))
        self.max_height = int(os.getenv('MAX_IMAGE_HEIGHT', 800))

        # 创建下载目录
        os.makedirs(self.download_path, exist_ok=True)
        logger.info(f"图片处理器初始化完成，下载路径: {self.download_path}")

    def download_image(self, image_url: str, article_slug: str) -> Optional[str]:
        """
        下载单张图片

        Args:
            image_url: 图片URL
            article_slug: 文章标识，用于组织图片存储

        Returns:
            本地图片路径，失败返回None
        """
        try:
            # 创建文章专属目录
            article_dir = os.path.join(self.download_path, article_slug)
            os.makedirs(article_dir, exist_ok=True)

            # 下载图片
            response = requests.get(image_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            # 生成文件名（使用URL的MD5作为文件名避免重复）
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]

            # 尝试从URL获取原始文件扩展名
            parsed_url = urlparse(image_url)
            path = unquote(parsed_url.path)
            ext = self._get_image_extension(response.content, path)

            filename = f"{url_hash}{ext}"
            local_path = os.path.join(article_dir, filename)

            # 处理并保存图片
            processed_image = self._process_image(response.content)
            if processed_image:
                processed_image.save(local_path, quality=self.quality, optimize=True)

                # 返回相对路径（用于前端访问）
                relative_path = f"/images/{article_slug}/{filename}"
                logger.info(f"成功下载并处理图片: {image_url} -> {relative_path}")
                return relative_path
            else:
                # 如果处理失败，直接保存原图
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                relative_path = f"/images/{article_slug}/{filename}"
                logger.warning(f"图片处理失败，保存原图: {relative_path}")
                return relative_path

        except Exception as e:
            logger.error(f"下载图片失败 {image_url}: {str(e)}")
            return None

    def _get_image_extension(self, content: bytes, url_path: str) -> str:
        """
        获取图片扩展名

        Args:
            content: 图片内容
            url_path: URL路径

        Returns:
            图片扩展名（包含点号）
        """
        # 尝试从URL路径获取扩展名
        if '.' in url_path:
            ext = os.path.splitext(url_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                return ext

        # 尝试从图片内容判断格式
        try:
            img = Image.open(BytesIO(content))
            format_map = {
                'JPEG': '.jpg',
                'PNG': '.png',
                'GIF': '.gif',
                'WEBP': '.webp',
                'BMP': '.bmp'
            }
            return format_map.get(img.format, '.jpg')
        except:
            return '.jpg'  # 默认使用jpg

    def _process_image(self, image_content: bytes) -> Optional[Image.Image]:
        """
        处理图片：调整大小、优化质量

        Args:
            image_content: 原始图片内容

        Returns:
            处理后的PIL Image对象，失败返回None
        """
        try:
            # 打开图片
            img = Image.open(BytesIO(image_content))

            # 转换RGBA为RGB（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 计算新尺寸（保持宽高比）
            width, height = img.size
            if width > self.max_width or height > self.max_height:
                ratio = min(self.max_width / width, self.max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"调整图片大小: {width}x{height} -> {new_width}x{new_height}")

            return img

        except Exception as e:
            logger.error(f"处理图片失败: {str(e)}")
            return None

    def process_article_images(self, html_content: str, article_slug: str) -> Tuple[str, List[dict]]:
        """
        处理文章中的所有图片

        Args:
            html_content: 文章HTML内容
            article_slug: 文章标识

        Returns:
            (处理后的HTML内容, 图片映射列表)
        """
        # 查找所有图片URL
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
        img_urls = img_pattern.findall(html_content)

        # 也查找data-src属性（微信懒加载）
        data_src_pattern = re.compile(r'<img[^>]+data-src=["\']([^"\']+)["\']', re.IGNORECASE)
        data_src_urls = data_src_pattern.findall(html_content)

        all_urls = list(set(img_urls + data_src_urls))

        image_mapping = []
        updated_html = html_content

        for original_url in all_urls:
            # 下载并处理图片
            local_path = self.download_image(original_url, article_slug)

            if local_path:
                # 替换HTML中的图片URL
                updated_html = updated_html.replace(original_url, local_path)

                # 记录映射关系
                image_mapping.append({
                    'original_url': original_url,
                    'local_path': local_path
                })

        logger.info(f"处理完成 {len(image_mapping)} 张图片")
        return updated_html, image_mapping

    def cleanup_old_images(self, days: int = 30):
        """
        清理旧图片

        Args:
            days: 保留最近多少天的图片
        """
        import time
        from datetime import datetime, timedelta

        cutoff_time = time.time() - (days * 24 * 60 * 60)

        for root, dirs, files in os.walk(self.download_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        logger.info(f"删除旧图片: {file_path}")
                    except Exception as e:
                        logger.error(f"删除图片失败 {file_path}: {str(e)}")


def main():
    """测试函数"""
    processor = ImageProcessor()

    # 测试下载单张图片
    test_url = "https://mmbiz.qpic.cn/test.jpg"
    result = processor.download_image(test_url, "test-article")
    print(f"下载结果: {result}")


if __name__ == "__main__":
    main()