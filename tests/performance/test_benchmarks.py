#!/usr/bin/env python3
"""
性能基准测试
测试翻译管道各个组件的性能表现
"""

import unittest
import time
import tempfile
import os
import sys
import json
import random
import string
from pathlib import Path
from datetime import datetime, timedelta
import tracemalloc
import cProfile
import pstats
import io
from contextlib import contextmanager
from typing import Callable, Any, Dict, List
import threading
import multiprocessing

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from wechat_extractor import clean_text, extract_from_html
from state_manager import ArticleStateManager
from markdown_generator import (
    sanitize_slug,
    generate_tags,
    format_content_to_markdown,
    generate_markdown,
    batch_generate
)


@contextmanager
def timer(name: str = "Operation"):
    """计时器上下文管理器"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"{name} took {end - start:.4f} seconds")


@contextmanager
def memory_tracker():
    """内存跟踪器上下文管理器"""
    tracemalloc.start()
    yield
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")


def profile_function(func: Callable) -> Callable:
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        # 输出性能统计
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # 打印前10个最耗时的函数
        print(s.getvalue())

        return result
    return wrapper


class TestTextProcessingPerformance(unittest.TestCase):
    """文本处理性能测试"""

    def setUp(self):
        """生成测试数据"""
        self.short_text = "这是一段短文本" * 10
        self.medium_text = "这是中等长度的文本内容" * 100
        self.long_text = "这是一段很长的文本内容，包含各种中文字符和标点符号。" * 1000
        self.very_long_text = "超长文本内容" * 10000

    def test_clean_text_performance(self):
        """测试文本清理性能"""
        test_cases = [
            ("短文本", self.short_text, 0.001),
            ("中等文本", self.medium_text, 0.01),
            ("长文本", self.long_text, 0.1),
            ("超长文本", self.very_long_text, 1.0)
        ]

        for name, text, max_time in test_cases:
            start = time.perf_counter()
            result = clean_text(text)
            elapsed = time.perf_counter() - start

            self.assertIsNotNone(result)
            self.assertLess(elapsed, max_time,
                          f"{name}清理耗时{elapsed:.4f}秒，超过{max_time}秒限制")
            print(f"{name}清理: {elapsed:.4f}秒")

    def test_slug_generation_performance(self):
        """测试slug生成性能"""
        titles = [
            "简单标题",
            "这是一个包含很多中文字符的超长标题需要处理" * 5,
            "Title with English and 中文 mixed content @#$%",
            "包含emoji的标题 😊🎉👍 和特殊字符 ™®©"
        ]

        for title in titles:
            start = time.perf_counter()
            slug = sanitize_slug(title)
            elapsed = time.perf_counter() - start

            self.assertIsNotNone(slug)
            self.assertLess(elapsed, 0.01,
                          f"Slug生成耗时{elapsed:.4f}秒，超过0.01秒限制")

    def test_tag_generation_performance(self):
        """测试标签生成性能"""
        contents = [
            self.short_text,
            self.medium_text,
            self.long_text
        ]

        for i, content in enumerate(contents):
            start = time.perf_counter()
            tags = generate_tags(content, f"标题{i}")
            elapsed = time.perf_counter() - start

            self.assertIsNotNone(tags)
            self.assertLess(elapsed, 0.1,
                          f"标签生成耗时{elapsed:.4f}秒，超过0.1秒限制")


class TestHTMLExtractionPerformance(unittest.TestCase):
    """HTML提取性能测试"""

    def generate_complex_html(self, paragraphs: int, images: int) -> str:
        """生成复杂的HTML内容"""
        html = """
        <html>
        <head>
            <title>性能测试文章</title>
            <meta property="og:title" content="性能测试文章">
        </head>
        <body>
            <h1 class="rich_media_title">性能测试文章标题</h1>
            <span class="rich_media_meta rich_media_meta_nickname">测试作者</span>
            <em id="publish_time">2024-01-15</em>
            <div id="js_content">
        """

        for i in range(paragraphs):
            html += f"<p>这是第{i+1}段内容，包含一些文字描述。</p>\n"
            if i % 5 == 0 and i < images * 5:
                html += f'<img data-src="http://example.com/image{i//5}.jpg" alt="图片{i//5}">\n'

        html += """
            </div>
        </body>
        </html>
        """
        return html

    def test_html_extraction_scalability(self):
        """测试HTML提取的可扩展性"""
        test_cases = [
            (10, 2, 0.1),     # 10段落，2图片，0.1秒限制
            (50, 10, 0.5),    # 50段落，10图片，0.5秒限制
            (100, 20, 1.0),   # 100段落，20图片，1秒限制
            (500, 50, 5.0),   # 500段落，50图片，5秒限制
        ]

        for paragraphs, images, max_time in test_cases:
            html = self.generate_complex_html(paragraphs, images)

            start = time.perf_counter()
            result = extract_from_html(html, save_images=False)
            elapsed = time.perf_counter() - start

            self.assertIsNotNone(result)
            self.assertEqual(len(result['images']), images)
            self.assertLess(elapsed, max_time,
                          f"提取{paragraphs}段落耗时{elapsed:.4f}秒，超过{max_time}秒限制")
            print(f"提取{paragraphs}段落，{images}图片: {elapsed:.4f}秒")

    @profile_function
    def test_html_extraction_profile(self):
        """HTML提取性能分析"""
        html = self.generate_complex_html(100, 20)
        result = extract_from_html(html, save_images=False)
        self.assertIsNotNone(result)


class TestStateManagementPerformance(unittest.TestCase):
    """状态管理性能测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'state.json')

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_state_manager_scalability(self):
        """测试状态管理器的可扩展性"""
        state_manager = ArticleStateManager(self.state_file)

        # 测试不同数量的文章
        test_cases = [
            (100, 0.5),    # 100篇文章，0.5秒限制
            (500, 2.0),    # 500篇文章，2秒限制
            (1000, 5.0),   # 1000篇文章，5秒限制
        ]

        for count, max_time in test_cases:
            # 清空状态
            state_manager.state_data['articles'] = {}

            start = time.perf_counter()
            for i in range(count):
                article_data = {
                    "title": f"文章{i}",
                    "content": {"text": f"内容{i}" * 100}
                }
                state_manager.add_article(f"http://example.com/{i}", article_data)
            elapsed = time.perf_counter() - start

            self.assertEqual(len(state_manager.state_data['articles']), count)
            self.assertLess(elapsed, max_time,
                          f"添加{count}篇文章耗时{elapsed:.4f}秒，超过{max_time}秒限制")
            print(f"添加{count}篇文章: {elapsed:.4f}秒")

    def test_state_manager_query_performance(self):
        """测试状态查询性能"""
        state_manager = ArticleStateManager(self.state_file)

        # 先添加1000篇文章
        for i in range(1000):
            article_data = {
                "title": f"文章{i}",
                "content": {"text": f"内容{i}"}
            }
            state_manager.add_article(f"http://example.com/{i}", article_data)

        # 测试查询性能
        urls_to_check = [f"http://example.com/{i}" for i in range(0, 1000, 10)]

        start = time.perf_counter()
        for url in urls_to_check:
            is_processed = state_manager.is_article_processed(url)
            self.assertTrue(is_processed)
        elapsed = time.perf_counter() - start

        self.assertLess(elapsed, 0.1,
                      f"查询100个URL耗时{elapsed:.4f}秒，超过0.1秒限制")
        print(f"查询100个URL: {elapsed:.4f}秒")

    def test_concurrent_state_access(self):
        """测试并发状态访问性能"""
        def worker(thread_id: int, url_count: int):
            """工作线程"""
            state_manager = ArticleStateManager(self.state_file)
            for i in range(url_count):
                article_data = {
                    "title": f"线程{thread_id}-文章{i}",
                    "content": {"text": f"内容{i}"}
                }
                url = f"http://example.com/thread{thread_id}/article{i}"
                state_manager.add_article(url, article_data)

        thread_count = 5
        urls_per_thread = 20

        start = time.perf_counter()

        threads = []
        for i in range(thread_count):
            thread = threading.Thread(target=worker, args=(i, urls_per_thread))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        elapsed = time.perf_counter() - start

        # 验证所有文章都被添加
        state_manager = ArticleStateManager(self.state_file)
        total_articles = len(state_manager.state_data['articles'])
        self.assertEqual(total_articles, thread_count * urls_per_thread)

        self.assertLess(elapsed, 5.0,
                      f"并发处理{total_articles}篇文章耗时{elapsed:.4f}秒，超过5秒限制")
        print(f"并发处理{total_articles}篇文章: {elapsed:.4f}秒")


class TestMarkdownGenerationPerformance(unittest.TestCase):
    """Markdown生成性能测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def generate_article_data(self, content_size: str = "medium") -> Dict[str, Any]:
        """生成测试文章数据"""
        if content_size == "small":
            content = "这是短内容。" * 10
        elif content_size == "medium":
            content = "这是中等长度的内容。" * 100
        elif content_size == "large":
            content = "这是很长的内容，包含各种信息。" * 1000
        else:
            content = "超长内容" * 10000

        return {
            "title": f"测试文章-{content_size}",
            "author": "测试作者",
            "publish_date": "2024-01-15",
            "content": {"text": content, "html": f"<p>{content}</p>"},
            "images": [{"src": f"img{i}.jpg", "alt": f"图{i}"} for i in range(5)],
            "original_url": "http://example.com/test"
        }

    def test_markdown_generation_scalability(self):
        """测试Markdown生成的可扩展性"""
        test_cases = [
            ("small", 0.01),
            ("medium", 0.05),
            ("large", 0.1),
            ("xlarge", 1.0)
        ]

        for size, max_time in test_cases:
            article_data = self.generate_article_data(size)

            start = time.perf_counter()
            result = generate_markdown(article_data)
            elapsed = time.perf_counter() - start

            self.assertTrue(result['success'])
            self.assertLess(elapsed, max_time,
                          f"{size}内容生成耗时{elapsed:.4f}秒，超过{max_time}秒限制")
            print(f"{size}内容Markdown生成: {elapsed:.4f}秒")

    def test_batch_generation_performance(self):
        """测试批量生成性能"""
        # 生成测试数据
        articles = []
        for i in range(50):
            articles.append(self.generate_article_data("medium"))

        # 保存到JSON
        json_file = os.path.join(self.temp_dir, 'batch.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f)

        start = time.perf_counter()
        results = batch_generate(json_file, self.temp_dir)
        elapsed = time.perf_counter() - start

        self.assertEqual(len(results), 50)
        self.assertLess(elapsed, 10.0,
                      f"批量生成50篇文章耗时{elapsed:.4f}秒，超过10秒限制")
        print(f"批量生成50篇文章: {elapsed:.4f}秒")
        print(f"平均每篇: {elapsed/50:.4f}秒")

    def test_memory_usage_during_generation(self):
        """测试生成过程中的内存使用"""
        articles = []
        for i in range(100):
            articles.append(self.generate_article_data("large"))

        json_file = os.path.join(self.temp_dir, 'memory_test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f)

        with memory_tracker():
            results = batch_generate(json_file, self.temp_dir)
            self.assertEqual(len(results), 100)


class TestEndToEndPerformance(unittest.TestCase):
    """端到端性能测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_pipeline_performance(self):
        """测试完整管道性能"""
        # 生成测试HTML
        html = """
        <html>
            <h1 class="rich_media_title">完整管道测试文章</h1>
            <div id="js_content">
        """
        for i in range(100):
            html += f"<p>第{i+1}段内容</p>\n"
            if i % 10 == 0:
                html += f'<img src="img{i}.jpg" alt="图{i}">\n'
        html += "</div></html>"

        total_start = time.perf_counter()

        # 步骤1: 提取
        with timer("HTML提取"):
            extracted = extract_from_html(html, save_images=False)

        # 步骤2: 状态管理
        state_file = os.path.join(self.temp_dir, 'state.json')
        state_manager = ArticleStateManager(state_file)

        with timer("状态记录"):
            state_manager.add_article("http://example.com/test", extracted)

        # 步骤3: Markdown生成
        with timer("Markdown生成"):
            result = generate_markdown(extracted, Path(self.temp_dir))

        total_elapsed = time.perf_counter() - total_start

        self.assertTrue(result['success'])
        self.assertLess(total_elapsed, 2.0,
                      f"完整管道耗时{total_elapsed:.4f}秒，超过2秒限制")
        print(f"完整管道总耗时: {total_elapsed:.4f}秒")

    def test_parallel_processing(self):
        """测试并行处理性能"""
        def process_article(article_id: int):
            """处理单篇文章"""
            html = f"""
            <html>
                <h1 class="rich_media_title">文章{article_id}</h1>
                <div id="js_content">
                    <p>内容{article_id}</p>
                </div>
            </html>
            """
            extracted = extract_from_html(html, save_images=False)
            result = generate_markdown(extracted)
            return result['success']

        # 串行处理
        serial_start = time.perf_counter()
        for i in range(10):
            process_article(i)
        serial_time = time.perf_counter() - serial_start

        # 并行处理
        parallel_start = time.perf_counter()
        with multiprocessing.Pool(processes=4) as pool:
            results = pool.map(process_article, range(10))
        parallel_time = time.perf_counter() - parallel_start

        print(f"串行处理10篇文章: {serial_time:.4f}秒")
        print(f"并行处理10篇文章: {parallel_time:.4f}秒")
        print(f"加速比: {serial_time/parallel_time:.2f}x")

        # 并行应该更快
        self.assertLess(parallel_time, serial_time)


class TestResourceUsage(unittest.TestCase):
    """资源使用测试"""

    def test_cpu_usage_pattern(self):
        """测试CPU使用模式"""
        import psutil
        import os

        # 获取当前进程
        process = psutil.Process(os.getpid())

        # 记录初始CPU使用
        initial_cpu = process.cpu_percent(interval=1)

        # 执行密集操作
        for i in range(100):
            text = "测试文本" * 1000
            clean_text(text)
            sanitize_slug(f"标题{i}")
            generate_tags(text, f"标题{i}")

        # 记录结束CPU使用
        final_cpu = process.cpu_percent(interval=1)

        print(f"初始CPU使用: {initial_cpu}%")
        print(f"结束CPU使用: {final_cpu}%")

        # CPU使用应该在合理范围内
        self.assertLess(final_cpu, 80, "CPU使用率过高")

    def test_memory_leak_detection(self):
        """内存泄漏检测"""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # 记录初始内存
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 执行多次操作
        for iteration in range(10):
            # 创建和处理大量数据
            articles = []
            for i in range(100):
                article = {
                    "title": f"文章{i}",
                    "content": {"text": "内容" * 1000}
                }
                articles.append(article)

            # 处理数据
            for article in articles:
                generate_markdown(article)

            # 清理
            articles = None
            gc.collect()

        # 记录最终内存
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = final_memory - initial_memory
        print(f"初始内存: {initial_memory:.2f} MB")
        print(f"最终内存: {final_memory:.2f} MB")
        print(f"内存增长: {memory_increase:.2f} MB")

        # 内存增长应该在合理范围内（不超过100MB）
        self.assertLess(memory_increase, 100,
                      f"内存泄漏检测：内存增长{memory_increase:.2f}MB超过限制")


class TestLoadTesting(unittest.TestCase):
    """负载测试"""

    def test_sustained_load(self):
        """持续负载测试"""
        duration = 10  # 测试持续10秒
        operations_count = 0
        errors_count = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            try:
                # 执行操作
                text = "测试内容" * random.randint(10, 100)
                clean_text(text)
                sanitize_slug(f"标题{operations_count}")
                operations_count += 1
            except Exception as e:
                errors_count += 1

        elapsed = time.time() - start_time
        ops_per_second = operations_count / elapsed

        print(f"持续负载测试结果:")
        print(f"  持续时间: {elapsed:.2f}秒")
        print(f"  总操作数: {operations_count}")
        print(f"  错误数: {errors_count}")
        print(f"  操作/秒: {ops_per_second:.2f}")

        # 应该能够稳定处理
        self.assertEqual(errors_count, 0, "持续负载下出现错误")
        self.assertGreater(ops_per_second, 100, "处理速度过慢")

    def test_spike_load(self):
        """突发负载测试"""
        # 模拟突发请求
        spike_size = 100
        articles = []

        for i in range(spike_size):
            articles.append({
                "title": f"突发文章{i}",
                "content": {"text": "内容" * random.randint(50, 200)}
            })

        start = time.perf_counter()
        results = []
        for article in articles:
            result = generate_markdown(article)
            results.append(result['success'])
        elapsed = time.perf_counter() - start

        success_rate = sum(results) / len(results)
        print(f"突发负载测试 ({spike_size}篇文章):")
        print(f"  耗时: {elapsed:.2f}秒")
        print(f"  成功率: {success_rate * 100:.2f}%")
        print(f"  平均处理时间: {elapsed/spike_size:.4f}秒")

        # 所有请求都应该成功
        self.assertEqual(success_rate, 1.0, "突发负载下有失败请求")
        # 应该在合理时间内完成
        self.assertLess(elapsed, 30, f"处理{spike_size}篇文章超过30秒")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)