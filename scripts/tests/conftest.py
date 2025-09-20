#!/usr/bin/env python3
"""
共享的pytest fixtures和配置
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============= 通用 Fixtures =============

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file():
    """创建临时文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


# ============= HTML内容 Fixtures =============

@pytest.fixture
def minimal_wechat_html():
    """最小的微信文章HTML"""
    return """
    <div class="rich_media_content">
        <h1 class="rich_media_title">测试标题</h1>
        <p>测试内容</p>
    </div>
    """


@pytest.fixture
def standard_wechat_html():
    """标准的微信文章HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="瑞典生活指南">
        <meta property="og:description" content="介绍瑞典生活">
        <meta name="author" content="瑞典马工">
    </head>
    <body>
        <div class="rich_media_content">
            <h1 class="rich_media_title">瑞典生活指南</h1>
            <div class="rich_media_meta_list">
                <em class="rich_media_meta">瑞典马工</em>
                <em class="rich_media_meta">2024-01-20</em>
            </div>

            <p>这是一篇关于瑞典生活的文章。</p>
            <p>瑞典是北欧最大的国家。</p>

            <img src="http://example.com/sweden.jpg" alt="瑞典风景">
        </div>
    </body>
    </html>
    """


@pytest.fixture
def complex_wechat_html():
    """复杂的微信文章HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="瑞典移民完全指南">
    </head>
    <body>
        <div class="rich_media_content">
            <h1 class="rich_media_title">瑞典移民完全指南</h1>

            <h2>第一章：签证类型</h2>
            <p>瑞典提供多种签证类型：</p>
            <ul>
                <li>工作签证</li>
                <li>学生签证</li>
                <li>家庭团聚签证</li>
            </ul>

            <h2>第二章：生活成本</h2>
            <table>
                <tr><th>项目</th><th>费用（SEK）</th></tr>
                <tr><td>房租</td><td>8000-15000</td></tr>
                <tr><td>食品</td><td>3000-5000</td></tr>
                <tr><td>交通</td><td>800-1200</td></tr>
            </table>

            <blockquote>
                <p>提示：瑞典的生活成本较高，但社会福利完善。</p>
            </blockquote>

            <img src="http://example.com/img1.jpg" alt="图1">
            <img data-src="http://example.com/img2.jpg" alt="图2">
            <img src="http://example.com/img3.jpg" data-src="http://example.com/img3-hd.jpg" alt="图3">

            <script>console.log('test');</script>
            <style>.test { color: red; }</style>
        </div>
    </body>
    </html>
    """


# ============= 文章数据 Fixtures =============

@pytest.fixture
def basic_article_data():
    """基本文章数据"""
    return {
        "title": "测试文章",
        "author": "测试作者",
        "publish_date": "2024-01-20",
        "content": {
            "text": "这是测试文章的内容。",
            "html": "<p>这是测试文章的内容。</p>"
        },
        "images": [],
        "word_count": 10
    }


@pytest.fixture
def full_article_data():
    """完整文章数据"""
    return {
        "title": "瑞典生活指南：斯德哥尔摩租房攻略",
        "author": "瑞典马工",
        "publish_date": "2024-01-20",
        "original_url": "https://mp.weixin.qq.com/s/example",
        "content": {
            "text": """在斯德哥尔摩租房是每个新移民面临的首要挑战。
            这座美丽的北欧首都拥有独特的住房体系。
            本文将详细介绍如何在斯德哥尔摩找到合适的住房。

            首先，了解瑞典的租房体系至关重要。
            瑞典有两种主要的租房形式：一手合同和二手合同。
            一手合同是直接与房东或住房公司签订的合同。
            二手合同则是从已有一手合同的租客处转租。

            其次，排队系统是获得一手合同的主要途径。
            在Bostadsförmedlingen注册后，每天都会积累排队天数。
            通常需要排队8-10年才能在市中心租到房子。

            最后，租金水平因地段和房型而异。
            市中心的单间公寓月租约8000-12000克朗。
            郊区的价格会便宜30-40%左右。""",
            "html": "<p>在斯德哥尔摩租房是每个新移民面临的首要挑战。</p>"
        },
        "images": [
            {
                "src": "http://example.com/stockholm.jpg",
                "alt": "斯德哥尔摩",
                "local_filename": "stockholm.jpg"
            },
            {
                "src": "http://example.com/apartment.jpg",
                "alt": "公寓",
                "local_filename": "apartment.jpg"
            }
        ],
        "word_count": 500,
        "extraction_metadata": {
            "extracted_at": datetime.now().isoformat(),
            "extractor_version": "2.0.0",
            "image_count": 2
        }
    }


@pytest.fixture
def article_batch():
    """批量文章数据"""
    articles = []
    for i in range(5):
        articles.append({
            "title": f"测试文章{i+1}",
            "author": "测试作者",
            "publish_date": f"2024-01-{20+i}",
            "content": {
                "text": f"这是第{i+1}篇测试文章的内容。" * 10,
                "html": f"<p>这是第{i+1}篇测试文章的内容。</p>"
            },
            "images": [],
            "word_count": 100
        })
    return articles


# ============= Mock数据 Fixtures =============

@pytest.fixture
def mock_wechat_response():
    """模拟微信文章响应"""
    return {
        "status_code": 200,
        "text": """
        <html>
        <head>
            <meta property="og:title" content="Mock文章">
        </head>
        <body>
            <div class="rich_media_content">
                <h1 class="rich_media_title">Mock文章标题</h1>
                <p>Mock内容</p>
            </div>
        </body>
        </html>
        """,
        "encoding": "utf-8"
    }


@pytest.fixture
def mock_image_data():
    """模拟图片数据"""
    # 创建一个简单的1x1像素的PNG图片
    import base64
    png_data = base64.b64decode(
        b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    return png_data


# ============= 状态管理 Fixtures =============

@pytest.fixture
def empty_state_data():
    """空的状态数据"""
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


@pytest.fixture
def populated_state_data():
    """已填充的状态数据"""
    return {
        "version": "1.0.0",
        "created_at": "2024-01-01T00:00:00",
        "last_updated": datetime.now().isoformat(),
        "articles": {
            "https://example.com/article1": {
                "url": "https://example.com/article1",
                "title": "已处理文章1",
                "status": "completed",
                "content_hash": "hash1",
                "process_count": 1,
                "first_processed_at": "2024-01-01T00:00:00",
                "last_processed_at": "2024-01-01T00:00:00"
            },
            "https://example.com/article2": {
                "url": "https://example.com/article2",
                "title": "已处理文章2",
                "status": "error",
                "error": "提取失败",
                "process_count": 1,
                "first_processed_at": "2024-01-02T00:00:00",
                "last_processed_at": "2024-01-02T00:00:00"
            }
        },
        "statistics": {
            "total_processed": 1,
            "total_updated": 0,
            "total_errors": 1
        }
    }


# ============= 测试配置 Fixtures =============

@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """重置环境变量"""
    # 清除可能影响测试的环境变量
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("CI", raising=False)


@pytest.fixture
def github_actions_env(monkeypatch):
    """模拟GitHub Actions环境"""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("CI", "true")


# ============= 测试助手函数 =============

def create_test_file(path: Path, content: str) -> None:
    """创建测试文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def create_test_json(path: Path, data: dict) -> None:
    """创建测试JSON文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============= Pytest配置 =============

def pytest_configure(config):
    """配置pytest"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "network: 需要网络的测试"
    )