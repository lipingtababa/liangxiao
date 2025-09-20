#!/usr/bin/env python3
"""
端到端集成测试 - 测试完整的翻译管道
"""

import pytest
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import os

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_content_with_state import extract_from_html, extract_from_url, process_incremental
from state_manager import ArticleStateManager
from markdown_generator import generate_markdown, batch_generate
from image_processor import ImageProcessor


class TestPipelineIntegration:
    """管道集成测试类"""

    @pytest.fixture
    def complete_html_article(self):
        """完整的HTML文章内容"""
        return """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta property="og:title" content="瑞典生活完全指南：从移民到定居">
            <meta property="og:description" content="详细介绍在瑞典生活的方方面面">
            <meta name="author" content="瑞典马工">
        </head>
        <body>
            <div class="rich_media_area_primary">
                <div class="rich_media_content" id="js_content">
                    <h1 class="rich_media_title">瑞典生活完全指南：从移民到定居</h1>
                    <div class="rich_media_meta_list">
                        <em class="rich_media_meta">瑞典马工</em>
                        <em class="rich_media_meta">2024-01-20</em>
                    </div>

                    <p><strong>前言</strong></p>
                    <p>移居瑞典是人生的重大决定。本文将为您提供从申请签证到在瑞典安家的完整指南。</p>

                    <h2>第一部分：签证和居留许可</h2>
                    <p>瑞典的移民体系相对透明和高效。主要的居留许可类型包括：</p>
                    <ul>
                        <li>工作居留许可</li>
                        <li>学生居留许可</li>
                        <li>家庭团聚居留许可</li>
                        <li>自雇居留许可</li>
                    </ul>

                    <img src="https://example.com/visa-types.jpg" alt="瑞典签证类型" data-ratio="0.75">

                    <h2>第二部分：住房</h2>
                    <p>在瑞典找房子可能是最大的挑战之一，特别是在斯德哥尔摩、哥德堡和马尔默等大城市。</p>

                    <h3>租房市场</h3>
                    <p>瑞典的租房市场分为一手合同和二手合同：</p>
                    <ol>
                        <li><strong>一手合同（Förstahandskontrakt）</strong>：直接与房东或住房公司签订</li>
                        <li><strong>二手合同（Andrahandskontrakt）</strong>：从拥有一手合同的租客处转租</li>
                    </ol>

                    <blockquote>
                        <p>提示：在Bostadsförmedlingen排队是获得一手合同的主要途径，但等待时间可能长达8-10年。</p>
                    </blockquote>

                    <img data-src="https://example.com/apartment-interior.jpg" alt="典型的瑞典公寓">

                    <h2>第三部分：工作和税务</h2>
                    <p>瑞典的就业市场对外国人相对开放，特别是IT、工程和医疗领域。</p>

                    <h3>个人号码（Personnummer）</h3>
                    <p>个人号码是在瑞典生活的关键。有了个人号码，您可以：</p>
                    <ul>
                        <li>开设银行账户</li>
                        <li>签订手机合同</li>
                        <li>注册医疗服务</li>
                        <li>申请各种会员卡</li>
                    </ul>

                    <h3>税务系统</h3>
                    <p>瑞典的税率较高，但相应的社会福利也很完善。税率根据收入水平分为不同档次：</p>
                    <table>
                        <tr><th>年收入（SEK）</th><th>边际税率</th></tr>
                        <tr><td>0 - 509,300</td><td>约32%</td></tr>
                        <tr><td>509,300 - 735,600</td><td>约52%</td></tr>
                        <tr><td>735,600以上</td><td>约57%</td></tr>
                    </table>

                    <img src="https://example.com/tax-calculation.png" alt="瑞典税务计算">

                    <h2>第四部分：社会福利</h2>
                    <p>瑞典的社会福利体系世界闻名，包括：</p>
                    <ul>
                        <li><strong>医疗保健</strong>：几乎免费的医疗服务</li>
                        <li><strong>育儿假</strong>：480天的带薪育儿假</li>
                        <li><strong>儿童津贴</strong>：每月1250克朗/孩子</li>
                        <li><strong>教育</strong>：从小学到大学的免费教育</li>
                    </ul>

                    <h2>第五部分：语言学习</h2>
                    <p>虽然大多数瑞典人英语很好，但学习瑞典语对融入社会至关重要。</p>
                    <p>政府提供免费的瑞典语课程（SFI - Svenska för invandrare）给所有移民。</p>

                    <img data-src="https://example.com/sfi-classroom.jpg" alt="SFI课堂">

                    <h2>总结</h2>
                    <p>移居瑞典需要充分的准备和耐心。虽然初期可能面临各种挑战，但瑞典的高质量生活、完善的社会保障和友好的社会环境，使这里成为许多人理想的居住地。</p>

                    <p><em>希望这份指南对您有所帮助。祝您在瑞典生活愉快！</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "posts").mkdir()
            (workspace / "images").mkdir()
            (workspace / "data").mkdir()
            yield workspace

    @pytest.mark.integration
    def test_complete_pipeline_flow(self, complete_html_article, temp_workspace):
        """测试完整的处理流程"""
        # 1. 提取内容
        extracted_data = extract_from_html(complete_html_article)

        assert extracted_data["title"] == "瑞典生活完全指南：从移民到定居"
        assert extracted_data["author"] == "瑞典马工"
        assert len(extracted_data["images"]) == 4
        assert "签证和居留许可" in extracted_data["content"]["text"]
        assert "社会福利" in extracted_data["content"]["text"]

        # 2. 状态管理
        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        url = "https://mp.weixin.qq.com/s/test-article"
        extracted_data["original_url"] = url

        # 添加到状态管理
        success = state_manager.add_article(url, extracted_data)
        assert success is True

        # 验证状态
        assert state_manager.is_article_processed(url)
        article_state = state_manager.get_article_state(url)
        assert article_state["status"] == "completed"

        # 3. 生成Markdown
        markdown_result = generate_markdown(
            extracted_data,
            temp_workspace / "posts"
        )

        assert markdown_result["success"] is True
        assert markdown_result["file_path"] is not None

        # 验证生成的文件
        markdown_file = Path(markdown_result["file_path"])
        assert markdown_file.exists()

        content = markdown_file.read_text(encoding="utf-8")
        assert "瑞典生活完全指南" in content
        assert "---" in content  # frontmatter
        assert "![" in content  # 图片引用

    @pytest.mark.integration
    def test_incremental_processing(self, temp_workspace):
        """测试增量处理机制"""
        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        # 模拟文章数据
        articles = [
            {
                "url": f"https://example.com/article{i}",
                "data": {
                    "title": f"文章{i}",
                    "author": "作者",
                    "content": {"text": f"内容{i}" * 100},
                    "images": []
                }
            }
            for i in range(5)
        ]

        # 第一次处理
        for article in articles[:3]:
            state_manager.add_article(article["url"], article["data"])

        # 获取未处理的URLs
        all_urls = [a["url"] for a in articles]
        unprocessed = state_manager.get_unprocessed_urls(all_urls)

        assert len(unprocessed) == 2
        assert articles[3]["url"] in unprocessed
        assert articles[4]["url"] in unprocessed

    @pytest.mark.integration
    @patch('requests.get')
    def test_image_processing_integration(self, mock_get, temp_workspace):
        """测试图片处理集成"""
        # 模拟图片响应
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        processor = ImageProcessor(str(temp_workspace / "images"))

        # 处理HTML中的图片
        html = """
        <div class="rich_media_content">
            <img src="http://example.com/image1.jpg" alt="图片1">
            <img data-src="http://example.com/image2.jpg" alt="图片2">
        </div>
        """

        processed_html, image_mapping = processor.process_article_images(
            html, "test-article"
        )

        assert len(image_mapping) == 2
        for mapping in image_mapping:
            assert "original_url" in mapping
            assert "local_path" in mapping

    @pytest.mark.integration
    def test_error_recovery(self, temp_workspace):
        """测试错误恢复机制"""
        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        # 标记错误
        error_url = "https://example.com/error-article"
        state_manager.mark_article_error(error_url, "网络错误")

        # 验证错误状态
        article_state = state_manager.get_article_state(error_url)
        assert article_state["status"] == "error"
        assert article_state["error"] == "网络错误"

        # 统计应该反映错误
        stats = state_manager.get_statistics()
        assert stats["error_articles"] == 1

    @pytest.mark.integration
    def test_batch_processing(self, temp_workspace):
        """测试批量处理"""
        # 创建测试数据
        articles = []
        for i in range(10):
            articles.append({
                "title": f"批量文章{i+1}",
                "author": "测试作者",
                "publish_date": "2024-01-20",
                "content": {
                    "text": f"这是第{i+1}篇文章的内容。" * 50,
                    "html": f"<p>这是第{i+1}篇文章的HTML内容。</p>"
                },
                "images": []
            })

        # 保存为JSON
        json_file = temp_workspace / "data" / "articles.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        # 批量生成
        results = batch_generate(str(json_file), str(temp_workspace / "posts"))

        # 验证结果
        assert len(results) == 10
        success_count = sum(1 for r in results if r["success"])
        assert success_count == 10

        # 验证文件生成
        generated_files = list((temp_workspace / "posts").glob("*.md"))
        assert len(generated_files) == 10

    @pytest.mark.integration
    def test_content_update_detection(self, temp_workspace):
        """测试内容更新检测"""
        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        url = "https://example.com/article"
        original_data = {
            "title": "原始标题",
            "content": {"text": "原始内容"},
            "images": []
        }

        # 添加原始文章
        state_manager.add_article(url, original_data)

        # 相同内容不需要更新
        assert not state_manager.needs_update(url, "原始内容")

        # 修改后的内容需要更新
        assert state_manager.needs_update(url, "修改后的内容")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_article_processing(self, temp_workspace):
        """测试大型文章处理"""
        # 创建大型文章
        large_content = "这是一段很长的内容。" * 1000  # 约15000字符

        large_article = {
            "title": "超长文章测试",
            "author": "测试作者",
            "content": {
                "text": large_content,
                "html": f"<p>{large_content}</p>"
            },
            "images": [
                {"src": f"http://example.com/img{i}.jpg", "alt": f"图{i}"}
                for i in range(20)  # 20张图片
            ]
        }

        # 生成Markdown
        result = generate_markdown(large_article, temp_workspace / "posts")

        assert result["success"] is True
        assert result["metadata"]["word_count"] > 10000
        assert result["metadata"]["image_count"] == 20

    @pytest.mark.integration
    def test_special_characters_handling(self, temp_workspace):
        """测试特殊字符处理"""
        special_html = """
        <div class="rich_media_content">
            <h1 class="rich_media_title">标题包含特殊字符：&amp; &lt; &gt; &quot; &#39; © ® ™</h1>
            <p>内容包含emoji：😀 🎉 🚀</p>
            <p>中文标点：，。！？；：""''</p>
            <p>数学符号：± × ÷ ≈ ≠ ≤ ≥</p>
        </div>
        """

        extracted = extract_from_html(special_html)
        result = generate_markdown(extracted, temp_workspace / "posts")

        assert result["success"] is True

        # 读取生成的文件
        if result["file_path"]:
            content = Path(result["file_path"]).read_text(encoding="utf-8")
            # 应该保留特殊字符
            assert "emoji" in content or "😀" in content

    @pytest.mark.integration
    def test_concurrent_processing(self, temp_workspace):
        """测试并发处理"""
        import threading
        import time

        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        results = []
        lock = threading.Lock()

        def process_article(index):
            """处理单个文章的线程函数"""
            article_data = {
                "title": f"并发文章{index}",
                "content": {"text": f"内容{index}"},
                "images": []
            }

            url = f"https://example.com/concurrent{index}"
            success = state_manager.add_article(url, article_data)

            with lock:
                results.append((index, success))

        # 创建并启动线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=process_article, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 10
        assert all(r[1] for r in results)  # 所有操作都应该成功

        # 验证状态文件
        stats = state_manager.get_statistics()
        assert stats["total_articles"] == 10

    @pytest.mark.integration
    def test_cleanup_mechanism(self, temp_workspace):
        """测试清理机制"""
        from datetime import timedelta

        state_file = temp_workspace / "data" / "state.json"
        state_manager = ArticleStateManager(str(state_file))

        # 添加文章并修改时间
        for i in range(5):
            url = f"https://example.com/old{i}"
            data = {"title": f"旧文章{i}", "content": {"text": "内容"}, "images": []}
            state_manager.add_article(url, data)

            # 修改前3个为旧文章
            if i < 3:
                old_date = (datetime.now() - timedelta(days=35)).isoformat()
                state_manager.state_data["articles"][url]["last_processed_at"] = old_date
                state_manager._save_state()

        # 清理30天前的文章
        removed = state_manager.cleanup_old_entries(30)

        assert removed == 3
        assert len(state_manager.state_data["articles"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])