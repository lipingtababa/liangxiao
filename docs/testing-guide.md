# 测试指南 / Testing Guide

## 概述 / Overview

本项目实现了完整的自动化测试框架，用于确保翻译管道的质量和稳定性。测试覆盖了从内容提取到Markdown生成的整个流程。

## 测试架构 / Test Architecture

```
scripts/tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # 共享fixtures和配置
├── test_state_manager.py    # 状态管理器单元测试
├── test_content_extractor.py # 内容提取器单元测试
├── test_markdown_generator.py # Markdown生成器单元测试
├── test_pipeline_integration.py # 集成测试
└── test_data/               # 测试数据
    └── sample_articles.json # 示例文章数据
```

## 测试类型 / Test Types

### 1. 单元测试 (Unit Tests)

测试各个模块的独立功能：

- **状态管理器测试** (`test_state_manager.py`)
  - 初始化和加载状态文件
  - 文章处理状态跟踪
  - 内容更新检测
  - 并发安全性

- **内容提取器测试** (`test_content_extractor.py`)
  - HTML解析
  - 标题、作者、日期提取
  - 图片提取
  - 特殊字符处理

- **Markdown生成器测试** (`test_markdown_generator.py`)
  - Slug生成
  - 标签和类别判断
  - Frontmatter生成
  - 内容格式化

### 2. 集成测试 (Integration Tests)

测试模块间的交互：

- 完整管道流程测试
- 增量处理机制
- 错误恢复
- 批量处理

### 3. 端到端测试 (E2E Tests)

测试整个系统的实际运行：

- 从URL提取到Markdown生成的完整流程
- 状态持久化
- 文件生成验证

## 运行测试 / Running Tests

### 使用 Makefile

```bash
# 安装依赖
make install

# 运行所有测试
make test

# 运行特定类型的测试
make test-unit          # 单元测试
make test-integration   # 集成测试
make test-e2e          # 端到端测试

# 生成覆盖率报告
make coverage

# 代码质量检查
make lint

# 清理临时文件
make clean
```

### 使用 pytest 直接运行

```bash
# 运行所有测试
pytest scripts/tests -v

# 运行带标记的测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m e2e          # 只运行端到端测试

# 运行特定文件
pytest scripts/tests/test_state_manager.py -v

# 运行特定测试类或函数
pytest scripts/tests/test_state_manager.py::TestArticleStateManager::test_add_article -v

# 生成覆盖率报告
pytest --cov=scripts --cov-report=html --cov-report=term
```

### 使用测试运行器

```bash
# 运行测试脚本
python scripts/run_tests.py --type all --verbose

# 运行特定测试
python scripts/run_tests.py --file test_state_manager.py

# 带代码检查
python scripts/run_tests.py --lint
```

## 测试配置 / Test Configuration

### pytest.ini 配置

```ini
[pytest]
testpaths = scripts/tests tests
addopts = -v --tb=short --strict-markers
markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    slow: 慢速测试
    network: 需要网络的测试
```

### 覆盖率配置

目标覆盖率：70%

忽略的文件：
- 测试文件本身
- `__pycache__` 目录
- 示例和脚本文件

## 测试数据 / Test Data

### Fixtures

在 `conftest.py` 中定义了多个共享fixtures：

- `minimal_wechat_html` - 最小HTML示例
- `standard_wechat_html` - 标准微信文章HTML
- `complex_wechat_html` - 复杂HTML（包含表格、列表等）
- `basic_article_data` - 基本文章数据
- `full_article_data` - 完整文章数据
- `temp_dir` - 临时目录
- `mock_image_data` - 模拟图片数据

### 示例数据

`test_data/sample_articles.json` 包含真实的文章示例，用于集成测试。

## CI/CD 集成 / CI/CD Integration

### GitHub Actions

`.github/workflows/test-pipeline.yml` 配置了自动化测试流程：

1. **多版本测试** - 在 Python 3.9、3.10、3.11 上运行
2. **代码质量检查** - flake8 和 pylint
3. **测试执行** - 单元测试、集成测试、端到端测试
4. **覆盖率报告** - 上传到 Codecov
5. **性能测试** - 验证处理大文件的性能

触发条件：
- Push 到 main、develop 或 feature/* 分支
- Pull Request 到 main 分支
- 修改 scripts/ 目录或 requirements.txt

## 最佳实践 / Best Practices

### 编写测试

1. **遵循AAA模式**
   - Arrange: 准备测试数据
   - Act: 执行测试操作
   - Assert: 验证结果

2. **使用fixtures**
   - 复用测试数据
   - 管理测试环境
   - 清理资源

3. **合理使用标记**
   ```python
   @pytest.mark.unit
   def test_function():
       pass
   ```

4. **测试隔离**
   - 每个测试独立运行
   - 使用临时文件和目录
   - 清理测试产生的数据

### 测试命名

- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试函数：`test_<what_is_being_tested>`

### Mock 和 Patch

使用 `unittest.mock` 进行外部依赖模拟：

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_with_mock(mock_get):
    mock_get.return_value.status_code = 200
    # 测试代码
```

## 故障排除 / Troubleshooting

### 常见问题

1. **导入错误**
   - 确保 `scripts` 目录在 Python 路径中
   - 检查 `sys.path.insert(0, str(Path(__file__).parent.parent))`

2. **权限错误**
   - 使用临时目录进行文件操作
   - 确保有写入权限

3. **网络测试失败**
   - 使用 mock 代替真实网络请求
   - 标记为 `@pytest.mark.network`

4. **并发测试不稳定**
   - 使用文件锁确保线程安全
   - 增加超时时间

## 性能基准 / Performance Benchmarks

目标性能指标：

- 单篇文章提取：< 2秒
- Markdown生成：< 1秒
- 批量处理10篇文章：< 10秒
- 大文件处理（10000字）：< 5秒

## 持续改进 / Continuous Improvement

### 待添加的测试

- [ ] 翻译API集成测试
- [ ] 图片下载和处理测试
- [ ] 更多边界条件测试
- [ ] 压力测试和负载测试
- [ ] 安全性测试

### 提高覆盖率

当前重点提高覆盖率的模块：
- `wechat_extractor.py`
- `image_processor.py`
- 错误处理路径

## 贡献指南 / Contributing

提交代码前请确保：

1. 所有测试通过
2. 代码覆盖率不低于70%
3. 通过代码质量检查
4. 添加相应的测试用例

```bash
# 提交前检查清单
make test          # 运行测试
make coverage      # 检查覆盖率
make lint          # 代码质量检查
```