#!/usr/bin/env python3
"""
内容提取器的单元测试
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_content_with_state import extract_from_html, extract_from_url, process_incremental


class TestContentExtractor:
    """内容提取器测试类"""

    @pytest.fixture
    def sample_html(self):
        """示例HTML内容"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:title" content="测试文章标题">
            <meta name="author" content="测试作者">
        </head>
        <body>
            <div class="rich_media_content">
                <h1 class="rich_media_title">测试文章标题</h1>
                <em class="rich_media_meta">测试作者</em>
                <em id="publish_time">2024-01-20</em>

                <p>这是第一段内容，包含一些测试文本。</p>
                <p>这是第二段内容，继续添加更多文本。</p>

                <img src="http://example.com/image1.jpg" alt="图片1">
                <img data-src="http://example.com/image2.jpg" alt="图片2">
            </div>
        </body>
        </html>
        """

    @pytest.fixture
    def minimal_html(self):
        """最小化HTML内容"""
        return """
        <div class="rich_media_content">
            <h1 class="rich_media_title">最小测试</h1>
            <p>内容</p>
        </div>
        """

    @pytest.fixture
    def complex_html(self):
        """复杂HTML内容"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:title" content="复杂文章：包含特殊字符 & HTML实体">
        </head>
        <body>
            <div class="rich_media_content">
                <h1 class="rich_media_title">复杂文章：包含特殊字符 &amp; HTML实体</h1>

                <p><strong>加粗文本</strong>和<em>斜体文本</em></p>
                <ul>
                    <li>列表项1</li>
                    <li>列表项2</li>
                </ul>
                <ol>
                    <li>有序列表1</li>
                    <li>有序列表2</li>
                </ol>

                <blockquote>这是引用文本</blockquote>

                <img src="http://example.com/image1.jpg"
                     data-src="http://example.com/image-hd.jpg"
                     alt="高清图片"
                     style="width: 100%;">

                <script>alert('恶意脚本')</script>
                <style>body { display: none; }</style>
            </div>
        </body>
        </html>
        """

    @pytest.mark.unit
    def test_extract_title(self, sample_html):
        """测试标题提取"""
        result = extract_from_html(sample_html)
        assert result["title"] == "测试文章标题"

    @pytest.mark.unit
    def test_extract_title_from_meta(self):
        """测试从meta标签提取标题"""
        html = """
        <html>
        <head>
            <meta property="og:title" content="Meta标签标题">
        </head>
        <body>
            <div class="rich_media_content">
                <p>内容</p>
            </div>
        </body>
        </html>
        """
        result = extract_from_html(html)
        assert result["title"] == "Meta标签标题"

    @pytest.mark.unit
    def test_extract_author(self, sample_html):
        """测试作者提取"""
        result = extract_from_html(sample_html)
        assert result["author"] == "测试作者"

    @pytest.mark.unit
    def test_default_author(self, minimal_html):
        """测试默认作者"""
        result = extract_from_html(minimal_html)
        assert result["author"] == "瑞典马工"

    @pytest.mark.unit
    def test_extract_date(self, sample_html):
        """测试日期提取"""
        result = extract_from_html(sample_html)
        assert result["publish_date"] == "2024-01-20"

    @pytest.mark.unit
    def test_extract_date_formats(self):
        """测试不同日期格式"""
        test_cases = [
            ("2024-01-20", "2024-01-20"),
            ("2024/01/20", "2024-01-20"),
            ("2024/1/5", "2024-1-5"),
        ]

        for date_input, expected in test_cases:
            html = f"""
            <div class="rich_media_content">
                <h1 class="rich_media_title">测试</h1>
                <em>{date_input}</em>
                <p>内容</p>
            </div>
            """
            result = extract_from_html(html)
            assert expected in result["publish_date"]

    @pytest.mark.unit
    def test_extract_content(self, sample_html):
        """测试内容提取"""
        result = extract_from_html(sample_html)

        assert "text" in result["content"]
        assert "html" in result["content"]
        assert "第一段内容" in result["content"]["text"]
        assert "第二段内容" in result["content"]["text"]
        assert len(result["content"]["text"]) > 0

    @pytest.mark.unit
    def test_extract_images(self, sample_html):
        """测试图片提取"""
        result = extract_from_html(sample_html)

        assert len(result["images"]) == 2
        assert result["images"][0]["src"] == "http://example.com/image1.jpg"
        assert result["images"][1]["src"] == "http://example.com/image2.jpg"

    @pytest.mark.unit
    def test_extract_images_with_data_src(self, complex_html):
        """测试提取data-src属性的图片"""
        result = extract_from_html(complex_html)

        # 应该找到所有图片URL
        image_urls = [img["src"] for img in result["images"]]
        assert "http://example.com/image1.jpg" in image_urls
        assert "http://example.com/image-hd.jpg" in image_urls

    @pytest.mark.unit
    def test_word_count(self, sample_html):
        """测试字数统计"""
        result = extract_from_html(sample_html)
        assert result["word_count"] > 0
        assert result["word_count"] == len(result["content"]["text"])

    @pytest.mark.unit
    def test_extraction_metadata(self, sample_html):
        """测试提取元数据"""
        result = extract_from_html(sample_html)

        assert "extraction_metadata" in result
        metadata = result["extraction_metadata"]

        assert "extracted_at" in metadata
        assert "extractor_version" in metadata
        assert "image_count" in metadata
        assert metadata["image_count"] == len(result["images"])

    @pytest.mark.unit
    def test_empty_html(self):
        """测试空HTML"""
        result = extract_from_html("")

        assert result["title"] == ""
        assert result["content"]["text"] == ""
        assert len(result["images"]) == 0

    @pytest.mark.unit
    def test_malformed_html(self):
        """测试格式错误的HTML"""
        html = """
        <div class="rich_media_content>
            <h1 class="rich_media_title>未闭合的标签
            <p>内容
        """
        # 应该能够处理而不崩溃
        result = extract_from_html(html)
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_special_characters(self):
        """测试特殊字符处理"""
        html = """
        <div class="rich_media_content">
            <h1 class="rich_media_title">标题包含 &amp; &lt; &gt; &quot; &#39;</h1>
            <p>内容包含特殊字符：© ® ™ € £ ¥</p>
        </div>
        """
        result = extract_from_html(html)
        assert "&" in result["title"] or "标题包含" in result["title"]
        assert len(result["content"]["text"]) > 0

    @pytest.mark.unit
    def test_extract_with_scripts_and_styles(self, complex_html):
        """测试忽略脚本和样式"""
        result = extract_from_html(complex_html)

        # 不应该包含脚本内容
        assert "alert" not in result["content"]["text"]
        assert "display: none" not in result["content"]["text"]

    @pytest.mark.unit
    @pytest.mark.parametrize("url,expected_success", [
        ("https://mp.weixin.qq.com/s/test", True),
        ("invalid-url", False),
        ("", False),
    ])
    def test_extract_from_url_mock(self, url, expected_success, monkeypatch):
        """测试URL提取（使用mock）"""
        import os
        monkeypatch.setenv("GITHUB_ACTIONS", "true")

        if expected_success and "test" in url:
            # 在GitHub Actions环境中，test URL会使用mock数据
            result = extract_from_url(url)
            assert result is not None
            if not result.get("error"):
                assert "title" in result

    @pytest.mark.unit
    def test_incremental_processing(self, tmpdir, monkeypatch):
        """测试增量处理"""
        import tempfile
        from state_manager import ArticleStateManager

        # 创建临时状态文件
        state_file = tmpdir.join("state.json")
        manager = ArticleStateManager(str(state_file))

        urls = [
            "http://example.com/article1",
            "http://example.com/article2",
            "http://example.com/article3"
        ]

        # Mock extract_from_url函数
        def mock_extract(url, force_update=False, state_manager=None):
            return {
                "title": f"文章 {url}",
                "content": {"text": "测试内容"},
                "images": [],
                "original_url": url
            }

        monkeypatch.setattr("extract_content_with_state.extract_from_url", mock_extract)

        # 第一次处理
        stats = process_incremental(urls, manager, force_update=False)
        assert stats["processed"] == 3
        assert stats["skipped"] == 0

        # 第二次处理（应该全部跳过）
        stats = process_incremental(urls, manager, force_update=False)
        assert stats["processed"] == 0
        assert stats["skipped"] == 3

        # 强制更新
        stats = process_incremental(urls, manager, force_update=True)
        assert stats["processed"] == 3

    @pytest.mark.unit
    def test_html_content_cleaning(self):
        """测试HTML内容清理"""
        html = """
        <div class="rich_media_content">
            <h1 class="rich_media_title">标题</h1>
            <p>段落1</p>
            <br><br><br>
            <p>段落2</p>
            <div>   </div>
            <p>段落3</p>
        </div>
        """
        result = extract_from_html(html)

        # 内容应该被清理
        text = result["content"]["text"]
        assert "段落1" in text
        assert "段落2" in text
        assert "段落3" in text

    @pytest.mark.unit
    def test_image_metadata(self, sample_html):
        """测试图片元数据"""
        result = extract_from_html(sample_html)

        for idx, image in enumerate(result["images"]):
            assert "src" in image
            assert "alt" in image
            assert "local_filename" in image
            assert image["local_filename"] == f"image_{idx+1}.jpg"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])