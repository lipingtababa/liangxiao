#!/usr/bin/env python3
"""
测试数据管理
提供各种测试场景的数据fixtures
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import string


class TestDataManager:
    """测试数据管理器"""

    def __init__(self):
        """初始化测试数据管理器"""
        self.fixtures_dir = Path(__file__).parent
        self.sample_articles = self._load_sample_articles()

    def _load_sample_articles(self) -> List[Dict[str, Any]]:
        """加载示例文章数据"""
        return [
            # 生活类文章
            {
                "title": "瑞典超市购物指南",
                "author": "瑞典马工",
                "publish_date": "2024-01-10",
                "category": "生活",
                "content": {
                    "text": """
                    瑞典的超市种类很多，主要有ICA、Coop、Hemköp和Willys等。
                    ICA是最常见的连锁超市，价格适中，商品种类齐全。
                    Willys主打低价，适合大批量采购。
                    Coop是合作社性质的超市，会员有优惠。
                    购物时记得自备购物袋，塑料袋需要额外付费。
                    """,
                    "html": "<p>瑞典的超市种类很多...</p>"
                },
                "images": [
                    {"src": "ica_store.jpg", "alt": "ICA超市"},
                    {"src": "shopping_bag.jpg", "alt": "环保购物袋"}
                ]
            },

            # 工作类文章
            {
                "title": "瑞典IT行业求职经验分享",
                "author": "瑞典马工",
                "publish_date": "2024-01-12",
                "category": "工作",
                "content": {
                    "text": """
                    瑞典的IT行业非常发达，特别是在斯德哥尔摩地区。
                    主要的科技公司包括Spotify、Klarna、King等。
                    求职时，LinkedIn是最重要的平台。
                    面试通常包括技术面试和文化匹配面试。
                    工作与生活的平衡是瑞典职场文化的核心。
                    Fika（咖啡时间）是瑞典职场的重要传统。
                    """,
                    "html": "<p>瑞典的IT行业非常发达...</p>"
                },
                "images": [
                    {"src": "spotify_office.jpg", "alt": "Spotify办公室"},
                    {"src": "fika_time.jpg", "alt": "Fika时间"}
                ]
            },

            # 教育类文章
            {
                "title": "瑞典大学申请全攻略",
                "author": "瑞典马工",
                "publish_date": "2024-01-15",
                "category": "教育",
                "content": {
                    "text": """
                    瑞典的高等教育质量世界领先，多所大学排名全球前列。
                    卡罗林斯卡学院、隆德大学、乌普萨拉大学都是知名学府。
                    EU/EEA公民可以免费就读，其他国际学生需要支付学费。
                    申请通过universityadmissions.se统一进行。
                    瑞典政府和各大学提供多种奖学金机会。
                    """,
                    "html": "<p>瑞典的高等教育质量世界领先...</p>"
                },
                "images": [
                    {"src": "uppsala_university.jpg", "alt": "乌普萨拉大学"}
                ]
            },

            # 移民类文章
            {
                "title": "2024年瑞典移民政策最新变化",
                "author": "瑞典马工",
                "publish_date": "2024-01-20",
                "category": "移民",
                "content": {
                    "text": """
                    2024年瑞典移民政策有重大调整。
                    工作签证的最低工资要求提高到月薪27,360克朗。
                    永久居留权申请需要通过瑞典语和社会知识测试。
                    家庭团聚的维持费要求有所提高。
                    留学生毕业后找工作的时间延长至12个月。
                    创业签证的申请条件有所放宽。
                    """,
                    "html": "<p>2024年瑞典移民政策有重大调整...</p>"
                },
                "images": [
                    {"src": "migration_office.jpg", "alt": "瑞典移民局"}
                ]
            },

            # 文化类文章
            {
                "title": "瑞典传统节日：仲夏节庆祝指南",
                "author": "瑞典马工",
                "publish_date": "2024-06-20",
                "category": "文化",
                "content": {
                    "text": """
                    仲夏节是瑞典最重要的传统节日之一。
                    通常在六月第三个周五庆祝。
                    传统活动包括竖立五月柱、跳青蛙舞、吃腌鲱鱼。
                    新土豆配莳萝是必备的节日美食。
                    许多瑞典人会去乡下的夏季小屋庆祝。
                    这是体验瑞典文化的最佳时机。
                    """,
                    "html": "<p>仲夏节是瑞典最重要的传统节日之一...</p>"
                },
                "images": [
                    {"src": "midsummer_pole.jpg", "alt": "五月柱"},
                    {"src": "herring_potatoes.jpg", "alt": "腌鲱鱼和新土豆"}
                ]
            }
        ]

    def get_sample_article(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        获取示例文章

        Args:
            category: 文章类别（可选）

        Returns:
            文章数据字典
        """
        if category:
            filtered = [a for a in self.sample_articles if a.get('category') == category]
            if filtered:
                return random.choice(filtered)
        return random.choice(self.sample_articles)

    def get_sample_articles(self, count: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取多篇示例文章

        Args:
            count: 文章数量
            category: 文章类别（可选）

        Returns:
            文章数据列表
        """
        if category:
            filtered = [a for a in self.sample_articles if a.get('category') == category]
            if filtered:
                return random.sample(filtered, min(count, len(filtered)))

        # 如果文章数量不够，重复选择
        if count <= len(self.sample_articles):
            return random.sample(self.sample_articles, count)
        else:
            articles = []
            for i in range(count):
                articles.append(self.sample_articles[i % len(self.sample_articles)].copy())
            return articles

    def generate_html_content(self, title: str, paragraphs: List[str],
                            images: List[Dict[str, str]] = None) -> str:
        """
        生成HTML内容

        Args:
            title: 文章标题
            paragraphs: 段落列表
            images: 图片列表

        Returns:
            HTML字符串
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <meta property="og:title" content="{title}">
        </head>
        <body>
            <div class="rich_media">
                <h1 class="rich_media_title">{title}</h1>
                <div class="rich_media_meta_list">
                    <span class="rich_media_meta rich_media_meta_nickname">瑞典马工</span>
                    <em id="publish_time">{datetime.now().strftime('%Y-%m-%d')}</em>
                </div>
                <div id="js_content" class="rich_media_content">
        """

        for i, para in enumerate(paragraphs):
            html += f"        <p>{para}</p>\n"

            # 在段落之间插入图片
            if images and i < len(images):
                img = images[i]
                html += f'        <img data-src="{img["src"]}" alt="{img.get("alt", "")}">\n'

        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def generate_random_article(self) -> Dict[str, Any]:
        """生成随机文章数据"""
        categories = ["生活", "工作", "教育", "科技", "文化", "旅游", "美食"]
        category = random.choice(categories)

        title = f"测试文章 - {category} - {random.randint(1000, 9999)}"
        paragraphs = []
        for i in range(random.randint(3, 10)):
            para = f"这是第{i+1}段内容。" + "测试文本" * random.randint(10, 50)
            paragraphs.append(para)

        images = []
        for i in range(random.randint(0, 5)):
            images.append({
                "src": f"http://example.com/image{i}.jpg",
                "alt": f"图片{i}"
            })

        return {
            "title": title,
            "author": "测试作者",
            "publish_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "category": category,
            "content": {
                "text": "\n\n".join(paragraphs),
                "html": self.generate_html_content(title, paragraphs, images)
            },
            "images": images,
            "original_url": f"http://mp.weixin.qq.com/s/{self._generate_random_id()}"
        }

    def generate_batch_articles(self, count: int) -> List[Dict[str, Any]]:
        """生成批量文章数据"""
        return [self.generate_random_article() for _ in range(count)]

    def _generate_random_id(self, length: int = 10) -> str:
        """生成随机ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def save_to_json(self, data: Any, filename: str):
        """保存数据到JSON文件"""
        filepath = self.fixtures_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_json(self, filename: str) -> Any:
        """从JSON文件加载数据"""
        filepath = self.fixtures_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


class TestHTMLGenerator:
    """测试HTML生成器"""

    @staticmethod
    def create_minimal_html() -> str:
        """创建最小HTML"""
        return """
        <html>
            <body>
                <h1>标题</h1>
                <p>内容</p>
            </body>
        </html>
        """

    @staticmethod
    def create_wechat_article_html(title: str = "测试文章",
                                  content: str = "测试内容",
                                  author: str = "测试作者",
                                  date: str = None) -> str:
        """创建微信文章格式的HTML"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta property="og:title" content="{title}">
            <meta property="og:description" content="{content[:100]}">
            <meta name="author" content="{author}">
            <title>{title}</title>
        </head>
        <body>
            <div class="rich_media">
                <div class="rich_media_inner">
                    <h1 class="rich_media_title">{title}</h1>
                    <div class="rich_media_meta_list">
                        <span class="rich_media_meta rich_media_meta_nickname">
                            <a href="javascript:void(0);">{author}</a>
                        </span>
                        <em id="publish_time" class="rich_media_meta rich_media_meta_text">{date}</em>
                    </div>
                    <div id="js_content" class="rich_media_content">
                        <p>{content}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def create_complex_html(paragraphs: int = 10, images: int = 5) -> str:
        """创建复杂HTML（多段落、图片）"""
        html = """
        <html>
        <head>
            <title>复杂测试文章</title>
        </head>
        <body>
            <h1 class="rich_media_title">复杂测试文章</h1>
            <div id="js_content">
        """

        for i in range(paragraphs):
            html += f"        <p>这是第{i+1}段内容，包含各种文字信息。</p>\n"

            if i < images:
                html += f'        <img data-src="http://example.com/image{i}.jpg" alt="图片{i}">\n'

        html += """
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def create_malformed_html() -> str:
        """创建格式错误的HTML（用于错误处理测试）"""
        return """
        <html>
            <h1>未闭合的标题
            <div>
                <p>段落内容
            </div
        </html
        """


class TestStateGenerator:
    """测试状态生成器"""

    @staticmethod
    def create_empty_state() -> Dict[str, Any]:
        """创建空状态"""
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "articles": {},
            "statistics": {
                "total_processed": 0,
                "total_updated": 0,
                "total_errors": 0
            }
        }

    @staticmethod
    def create_state_with_articles(article_count: int = 10) -> Dict[str, Any]:
        """创建包含文章的状态"""
        state = TestStateGenerator.create_empty_state()

        for i in range(article_count):
            url = f"http://example.com/article{i}"
            state["articles"][url] = {
                "url": url,
                "title": f"文章{i}",
                "author": "作者",
                "publish_date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "content_hash": f"hash_{i}",
                "word_count": random.randint(100, 1000),
                "image_count": random.randint(0, 10),
                "first_processed_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "last_processed_at": datetime.now().isoformat(),
                "process_count": random.randint(1, 5),
                "status": "completed" if i % 5 != 0 else "error",
                "error": "处理错误" if i % 5 == 0 else None
            }

        state["statistics"]["total_processed"] = article_count
        state["statistics"]["total_errors"] = article_count // 5

        return state


class PerformanceTestData:
    """性能测试数据"""

    @staticmethod
    def generate_large_text(size_kb: int) -> str:
        """生成指定大小的文本"""
        # 每个字符约1字节，1KB = 1024字节
        char_count = size_kb * 1024
        return "测试文本" * (char_count // 8)

    @staticmethod
    def generate_large_article(content_size_kb: int = 100) -> Dict[str, Any]:
        """生成大型文章"""
        return {
            "title": "大型测试文章",
            "content": {
                "text": PerformanceTestData.generate_large_text(content_size_kb)
            },
            "images": [
                {"src": f"http://example.com/large_image{i}.jpg", "alt": f"大图{i}"}
                for i in range(50)
            ]
        }

    @staticmethod
    def generate_stress_test_batch(article_count: int = 1000) -> List[Dict[str, Any]]:
        """生成压力测试批量数据"""
        articles = []
        for i in range(article_count):
            articles.append({
                "title": f"压力测试文章{i}",
                "content": {
                    "text": f"压力测试内容{i}" * random.randint(50, 200)
                },
                "images": [
                    {"src": f"http://example.com/stress{i}_{j}.jpg", "alt": f"图{j}"}
                    for j in range(random.randint(0, 10))
                ]
            })
        return articles


# 创建全局测试数据管理器实例
test_data_manager = TestDataManager()


if __name__ == "__main__":
    # 测试示例
    manager = TestDataManager()

    # 获取示例文章
    article = manager.get_sample_article(category="工作")
    print(f"示例文章: {article['title']}")

    # 生成随机文章
    random_article = manager.generate_random_article()
    print(f"随机文章: {random_article['title']}")

    # 生成HTML
    html_gen = TestHTMLGenerator()
    html = html_gen.create_wechat_article_html("测试标题", "测试内容")
    print(f"HTML长度: {len(html)}")

    # 生成状态
    state_gen = TestStateGenerator()
    state = state_gen.create_state_with_articles(5)
    print(f"状态包含文章数: {len(state['articles'])}")

    # 性能测试数据
    perf_data = PerformanceTestData()
    large_text = perf_data.generate_large_text(10)
    print(f"大文本长度: {len(large_text)} 字符")