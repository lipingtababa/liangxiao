# API配置说明 - AI开发者必读

## 🔑 **API密钥配置**

### **重要**: 密钥映射关系

GitHub Secrets中的密钥名称和代码中使用的环境变量名称**不同**：

| GitHub Secret 名称 | 代码中的环境变量 | 用途 |
|-------------------|------------------|------|
| `GOOGLE_GEMINI_API_KEY` | `GOOGLE_API_KEY` | Google翻译服务 |
| `DEEPL_API_KEY` | `DEEPL_API_KEY` | DeepL翻译服务 |

### **在代码中正确使用:**

```python
import os

# 正确的用法
google_api_key = os.environ.get('GOOGLE_API_KEY', '')  # 会自动映射到 GOOGLE_GEMINI_API_KEY
deepl_api_key = os.environ.get('DEEPL_API_KEY', '')

# 错误的用法 - 不要这样做
# wrong_key = os.environ.get('GOOGLE_GEMINI_API_KEY', '')  # 这样取不到值
```

## 🧪 **在测试工作流中的使用**

所有测试工作流已经正确配置了环境变量映射：

```yaml
env:
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_GEMINI_API_KEY }}
  DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
```

## 📋 **API密钥检查清单**

### 对于AI开发者:

1. **✅ 在代码中使用**: `os.environ.get('GOOGLE_API_KEY')`
2. **❌ 不要使用**: `os.environ.get('GOOGLE_GEMINI_API_KEY')`  
3. **✅ 错误处理**: 检查密钥是否存在
4. **❌ 不要打印**: 永远不要在日志中打印API密钥

### 示例代码:

```python
import os
import sys

def get_translation_api_key():
    """获取翻译API密钥"""
    api_key = os.environ.get('GOOGLE_API_KEY', '')
    
    if not api_key:
        print("警告: Google API密钥未配置，翻译功能将受限", file=sys.stderr)
        return None
    
    # 不要打印完整密钥，只显示前几位用于调试
    print(f"✓ API密钥已配置 (开头: {api_key[:8]}...)", file=sys.stderr)
    return api_key

# 在翻译器中使用
api_key = get_translation_api_key()
if api_key:
    # 执行翻译
    pass
else:
    # 使用备用方法或返回错误
    pass
```

## 🚨 **安全提醒**

1. **永远不要**在代码、日志或输出中显示完整的API密钥
2. **只在**GitHub Secrets中存储密钥，不要硬编码
3. **检查**密钥是否存在并提供友好的错误信息
4. **使用**正确的环境变量名称(`GOOGLE_API_KEY`)

## 🧪 **测试密钥配置**

使用debug工具检查密钥是否正确配置：

```yaml
# 在 debug-ai-env.yml 中运行:
python_test: "import os; print('API Key configured:' if os.environ.get('GOOGLE_API_KEY') else 'No API Key')"
```

记住：AI开发者应该优雅地处理缺失的API密钥，让系统在没有翻译功能的情况下仍能正常工作！