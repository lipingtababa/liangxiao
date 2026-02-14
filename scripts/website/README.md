# 微信文章内容提取器

这是一个专门用于从微信公众号文章中提取内容的Python工具。

## 功能特性

- ✅ 提取文章标题、作者、发布时间
- ✅ 提取完整的文章内容（HTML和纯文本格式）
- ✅ 自动下载文章中的所有图片到本地
- ✅ 处理微信的反爬虫机制
- ✅ 完善的错误处理和日志记录
- ✅ 支持批量处理多个URL

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：

- requests - HTTP请求
- beautifulsoup4 - HTML解析
- lxml - HTML解析器

## 使用方法

### 1. 提取单个文章

```bash
python scripts/website/wechat_extractor.py --url "https://mp.weixin.qq.com/s/xxxxx"
```

### 2. 批量提取

创建一个包含URL列表的文件 `articles.txt`：

```
https://mp.weixin.qq.com/s/article1
https://mp.weixin.qq.com/s/article2
https://mp.weixin.qq.com/s/article3
```

然后运行：

```bash
python scripts/website/wechat_extractor.py --input articles.txt --output results.json
```

### 3. 不下载图片

如果只需要文本内容，可以添加 `--no-images` 参数：

```bash
python scripts/website/wechat_extractor.py --url "URL" --no-images
```

### 4. 指定图片保存目录

```bash
python scripts/website/wechat_extractor.py --url "URL" --image-dir ./my_images
```

## 输出格式

提取的内容以JSON格式保存，结构如下：

```json
{
  "title": "文章标题",
  "author": "作者名称",
  "publish_date": "2024-01-15",
  "original_url": "原文链接",
  "content": {
    "text": "纯文本内容",
    "html": "HTML格式内容"
  },
  "images": [
    {
      "src": "图片原始URL",
      "alt": "图片描述",
      "local_filename": "本地文件名",
      "local_path": "本地文件路径"
    }
  ],
  "word_count": 1234,
  "extraction_metadata": {
    "extracted_at": "提取时间",
    "extractor_version": "2.0.0",
    "image_count": 5,
    "images_downloaded": true
  }
}
```

## 测试

运行单元测试：

```bash
python -m pytest scripts/test/test_wechat_extractor.py -v
```

运行本地测试：

```bash
python scripts/test_extractor.py
```

## 注意事项

1. **反爬虫机制**：微信有反爬虫机制，建议：
   - 添加适当的延迟
   - 使用真实的User-Agent
   - 避免频繁请求

2. **图片下载**：
   - 图片默认保存在 `extracted_images/` 目录
   - 自动处理不同图片格式（jpg, png, gif, webp）
   - 失败的图片会记录日志但不会中断程序

3. **编码处理**：
   - 自动检测网页编码
   - 默认使用UTF-8

4. **错误处理**：
   - 网络错误会返回错误信息但不会抛出异常
   - 提取失败的字段会使用默认值

## 开发说明

主要模块：

- `wechat_extractor.py` - 主提取器
- `extract_from_html()` - HTML内容解析
- `extract_from_url()` - URL内容获取
- `download_image()` - 图片下载功能

## 更新日志

### v2.0.0 (2025-01-13)

- 完整实现微信文章提取功能
- 添加图片下载功能
- 改进错误处理
- 添加单元测试

### v1.0.0 (初始版本)

- 基础框架搭建
