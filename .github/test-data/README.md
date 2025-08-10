# 测试数据和工作流使用指南

这个目录包含了用于测试AI开发者实现的测试数据、验证脚本和工作流。

## 目录结构

```
.github/
├── workflows/
│   ├── test-extractor.yml          # 测试微信内容提取器
│   ├── test-translator.yml         # 测试翻译引擎
│   ├── test-markdown-generator.yml # 测试Markdown生成器
│   ├── test-full-pipeline.yml      # 测试完整流水线
│   └── validate-output.yml         # 验证输出格式
└── test-data/
    ├── sample-articles.txt         # 测试用文章URL
    ├── sample-wechat-response.html # 样本微信文章HTML
    ├── expected-output/            # 预期输出样本
    │   ├── sample-extracted-data.json
    │   ├── sample-translated-data.json
    │   └── sample-final-markdown.md
    └── validation-schemas/         # JSON验证Schema
        ├── article-schema.json
        └── markdown-frontmatter-schema.json
```

## 测试工作流使用方法

### 1. 微信内容提取器测试 (test-extractor.yml)

**用途**: 测试从微信文章URL提取内容的功能

**如何使用**:
1. 进入GitHub仓库的Actions页面
2. 选择"测试微信内容提取器"工作流
3. 点击"Run workflow"
4. 可选输入自定义测试URL
5. 查看运行结果和上传的artifacts

**参数**:
- `test_url`: 要测试的微信文章URL（可选，默认使用sample-articles.txt第一个）
- `debug_mode`: 是否启用调试模式（默认true）

### 2. 翻译引擎测试 (test-translator.yml)

**用途**: 测试中英文翻译功能

**如何使用**:
1. 先在仓库Settings -> Secrets中配置API密钥
2. 进入Actions页面，选择"测试翻译引擎"
3. 点击"Run workflow"
4. 输入要测试的中文文本
5. 查看翻译结果

**参数**:
- `test_text`: 要翻译的中文文本
- `target_language`: 目标语言（默认en）
- `debug_mode`: 调试模式

**必需的Secrets**:
- `GOOGLE_API_KEY` 或 `DEEPL_API_KEY`

### 3. Markdown生成器测试 (test-markdown-generator.yml)

**用途**: 测试将翻译数据转换为Markdown文件

**如何使用**:
1. 进入Actions页面，选择"测试Markdown生成器"
2. 点击"Run workflow"
3. 可选输入自定义标题和内容
4. 查看生成的Markdown文件

**参数**:
- `test_title`: 测试文章标题
- `test_content`: 测试文章内容
- `debug_mode`: 调试模式

### 4. 完整流水线测试 (test-full-pipeline.yml)

**用途**: 测试从提取到生成的完整处理流程

**如何使用**:
1. 确保已配置翻译API密钥
2. 进入Actions页面，选择"测试完整流水线"
3. 点击"Run workflow"
4. 选择测试参数
5. 查看完整处理报告

**参数**:
- `use_sample_data`: 是否使用样本数据（推荐true）
- `test_articles_count`: 测试文章数量（默认2）
- `debug_mode`: 调试模式

### 5. 输出格式验证 (validate-output.yml)

**用途**: 验证生成的文件是否符合格式要求

**如何使用**:
1. 先运行其他测试工作流生成输出文件
2. 进入Actions页面，选择"验证输出格式"
3. 输入要验证的路径
4. 查看验证报告

**参数**:
- `output_path`: 要验证的输出路径（如posts/或test-output/）
- `strict_mode`: 严格模式（警告也视为错误）

## 验证脚本使用方法

项目提供了三个Python验证脚本，位于`scripts/test/`目录：

### 1. validate_extraction.py - 验证提取数据

```bash
# 验证单个JSON文件
python scripts/test/validate_extraction.py path/to/data.json

# 验证整个目录
python scripts/test/validate_extraction.py path/to/directory/

# 生成详细报告
python scripts/test/validate_extraction.py path/to/directory/ --output report.json

# 严格模式（警告也视为错误）
python scripts/test/validate_extraction.py path/to/directory/ --strict
```

### 2. validate_markdown.py - 验证Markdown文件

```bash
# 验证Markdown文件
python scripts/test/validate_markdown.py path/to/posts/

# 指定文件匹配模式
python scripts/test/validate_markdown.py path/to/posts/ --pattern "*.md"

# 生成报告
python scripts/test/validate_markdown.py path/to/posts/ --output validation-report.json
```

### 3. validate_images.py - 验证图片文件

```bash
# 验证图片目录
python scripts/test/validate_images.py path/to/images/

# 根据JSON文件验证图片
python scripts/test/validate_images.py --json-mode article-data.json --base-dir images/

# 严格模式
python scripts/test/validate_images.py path/to/images/ --strict
```

## 测试数据说明

### sample-articles.txt
包含测试用的微信文章URL。AI开发者可以：
- 替换为实际可访问的URL进行测试
- 添加更多URL扩展测试覆盖范围

### sample-wechat-response.html
模拟的微信文章HTML响应，用于测试HTML解析逻辑。

### expected-output/
包含预期的输出格式样本：
- `sample-extracted-data.json`: 内容提取后的JSON格式
- `sample-translated-data.json`: 翻译后的JSON格式  
- `sample-final-markdown.md`: 最终生成的Markdown文件

### validation-schemas/
JSON Schema文件，用于验证数据格式：
- `article-schema.json`: 文章数据结构验证
- `markdown-frontmatter-schema.json`: Markdown frontmatter验证

## 开发建议

1. **先运行单元测试**: 从test-extractor.yml开始，逐步验证每个组件
2. **使用样本数据**: 初始开发时使用提供的sample-articles.txt
3. **查看artifacts**: 所有测试工作流都会上传结果文件，可下载查看
4. **阅读验证脚本**: 了解具体的验证规则和要求
5. **参考预期输出**: 使用expected-output目录中的样本作为实现参考

## 故障排查

### 常见问题
1. **API密钥未配置**: 检查GitHub Secrets设置
2. **Python依赖错误**: 确保requirements.txt包含所有必要依赖
3. **文件路径错误**: 注意GitHub Actions中的工作目录
4. **网络访问问题**: 微信URL可能需要特殊处理

### 调试技巧
1. 启用debug_mode查看详细日志
2. 下载artifacts查看中间输出文件
3. 使用验证脚本本地测试输出格式
4. 查看GitHub Actions运行日志定位错误

## 性能注意事项

- 测试工作流有2分钟超时限制
- 避免在测试中下载大量图片
- 使用样本数据进行快速迭代测试
- 完整测试建议限制在2-3篇文章

## 更新测试数据

AI开发者可以根据需要更新测试数据：
1. 修改sample-articles.txt添加新的测试URL
2. 更新预期输出样本文件
3. 调整validation schemas以适应新的数据格式

记住：测试数据的更新应该通过Pull Request进行，确保所有开发者使用一致的测试标准。