#!/usr/bin/env python3
"""
内容提取验证脚本

用于验证从微信文章提取的数据是否符合格式要求
AI开发者可以使用这个脚本来验证他们的内容提取器输出
"""

import os
import sys
import json
import jsonschema
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse

def load_schema() -> Dict[str, Any]:
    """加载JSON Schema"""
    schema_path = Path(__file__).parent.parent.parent / '.github' / 'test-data' / 'validation-schemas' / 'article-schema.json'
    
    if not schema_path.exists():
        # 如果schema文件不存在，使用内置的基本schema
        return {
            "type": "object",
            "required": ["title", "author", "publish_date", "original_url", "content"],
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "author": {"type": "string", "minLength": 1},
                "publish_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "original_url": {"type": "string", "format": "uri"},
                "content": {"type": "object", "required": ["text"]}
            }
        }
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_json_structure(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """使用JSON Schema验证数据结构"""
    schema = load_schema()
    errors = []
    
    try:
        jsonschema.validate(data, schema)
        return True, []
    except jsonschema.ValidationError as e:
        errors.append(f"Schema验证错误: {e.message}")
        return False, errors
    except Exception as e:
        errors.append(f"验证过程出错: {e}")
        return False, errors

def validate_content_quality(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """验证内容质量"""
    errors = []
    warnings = []
    
    # 验证标题
    title = data.get('title', '')
    if len(title) < 5:
        errors.append("标题太短（少于5个字符）")
    elif len(title) > 200:
        errors.append("标题太长（超过200个字符）")
    
    # 验证作者
    author = data.get('author', '')
    if not author or author.strip() == '':
        errors.append("作者信息为空")
    
    # 验证内容
    content = data.get('content', {})
    if not isinstance(content, dict):
        errors.append("content字段必须是对象")
    else:
        text_content = content.get('text', '')
        if not text_content:
            errors.append("内容文本为空")
        elif len(text_content) < 50:
            warnings.append("内容较短（少于50个字符）")
        elif len(text_content) > 50000:
            warnings.append("内容很长（超过50000个字符）")
    
    # 验证URL
    original_url = data.get('original_url', '')
    if original_url:
        parsed = urlparse(original_url)
        if not parsed.scheme in ['http', 'https']:
            errors.append("URL格式不正确")
        elif 'mp.weixin.qq.com' not in parsed.netloc:
            warnings.append("URL不是微信公众号文章")
    
    # 验证图片信息
    images = data.get('images', [])
    if isinstance(images, list):
        for i, img in enumerate(images):
            if not isinstance(img, dict):
                errors.append(f"图片 {i+1} 格式错误，应为对象")
                continue
            
            if 'src' not in img:
                errors.append(f"图片 {i+1} 缺少src字段")
            elif not img['src'].startswith(('http://', 'https://')):
                errors.append(f"图片 {i+1} URL格式不正确: {img['src']}")
            
            if 'local_filename' not in img:
                errors.append(f"图片 {i+1} 缺少local_filename字段")
            elif not img['local_filename'].endswith(('.jpg', '.jpeg', '.png', '.webp')):
                warnings.append(f"图片 {i+1} 文件扩展名可能不正确: {img['local_filename']}")
    
    # 验证标签
    tags = data.get('tags', [])
    if isinstance(tags, list):
        if len(tags) > 10:
            warnings.append(f"标签数量较多 ({len(tags)} 个)")
        for tag in tags:
            if not isinstance(tag, str):
                errors.append("标签必须是字符串")
            elif len(tag) > 50:
                warnings.append(f"标签过长: {tag}")
    
    # 验证字数统计
    word_count = data.get('word_count', 0)
    if isinstance(word_count, int) and word_count > 0:
        # 简单验证字数是否合理
        actual_text = content.get('text', '')
        estimated_count = len(actual_text.replace(' ', ''))  # 简单的字数估算
        if abs(word_count - estimated_count) > estimated_count * 0.5:
            warnings.append(f"字数统计可能不准确: 声明{word_count}，估算{estimated_count}")
    
    return len(errors) == 0, errors, warnings

def validate_single_file(file_path: Path) -> Dict[str, Any]:
    """验证单个JSON文件"""
    result = {
        'file': str(file_path),
        'valid': False,
        'errors': [],
        'warnings': [],
        'metadata': {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Schema验证
        schema_valid, schema_errors = validate_json_structure(data)
        result['errors'].extend(schema_errors)
        
        # 内容质量验证
        quality_valid, quality_errors, quality_warnings = validate_content_quality(data)
        result['errors'].extend(quality_errors)
        result['warnings'].extend(quality_warnings)
        
        # 收集元数据
        result['metadata'] = {
            'title': data.get('title', ''),
            'author': data.get('author', ''),
            'word_count': data.get('word_count', 0),
            'image_count': len(data.get('images', [])),
            'tag_count': len(data.get('tags', [])),
            'has_translation_metadata': 'translation_metadata' in data
        }
        
        result['valid'] = len(result['errors']) == 0
        
    except json.JSONDecodeError as e:
        result['errors'].append(f"JSON格式错误: {e}")
    except Exception as e:
        result['errors'].append(f"处理文件时出错: {e}")
    
    return result

def validate_directory(directory: Path, pattern: str = "*.json") -> List[Dict[str, Any]]:
    """验证目录中的所有JSON文件"""
    results = []
    
    if not directory.exists():
        print(f"错误: 目录不存在 {directory}")
        return results
    
    json_files = list(directory.glob(pattern))
    if not json_files:
        print(f"警告: 在 {directory} 中未找到匹配 {pattern} 的文件")
        return results
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    for json_file in sorted(json_files):
        print(f"验证: {json_file.name}")
        result = validate_single_file(json_file)
        results.append(result)
        
        # 输出验证结果
        if result['valid']:
            print(f"  ✓ 验证通过")
            if result['warnings']:
                print(f"    ({len(result['warnings'])} 个警告)")
        else:
            print(f"  ✗ 验证失败 ({len(result['errors'])} 个错误)")
            for error in result['errors'][:2]:  # 只显示前2个错误
                print(f"    - {error}")
            if len(result['errors']) > 2:
                print(f"    ... 还有 {len(result['errors']) - 2} 个错误")
        
        # 显示元数据
        metadata = result['metadata']
        if metadata.get('title'):
            print(f"    标题: {metadata['title'][:50]}...")
        if metadata.get('word_count'):
            print(f"    字数: {metadata['word_count']} | 图片: {metadata['image_count']} | 标签: {metadata['tag_count']}")
    
    return results

def generate_validation_report(results: List[Dict[str, Any]], output_file: str = None):
    """生成验证报告"""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['valid'])
    invalid_files = total_files - valid_files
    
    # 统计信息
    total_word_count = sum(r['metadata'].get('word_count', 0) for r in results)
    total_image_count = sum(r['metadata'].get('image_count', 0) for r in results)
    total_warning_count = sum(len(r['warnings']) for r in results)
    
    # 统计错误类型
    error_types = {}
    for result in results:
        for error in result['errors']:
            error_type = error.split(':')[0] if ':' in error else error[:50]
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    report = {
        'summary': {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0,
            'total_warnings': total_warning_count,
            'total_word_count': total_word_count,
            'total_image_count': total_image_count
        },
        'error_types': error_types,
        'details': results
    }
    
    # 输出摘要
    print(f"\n=== 内容提取验证报告 ===")
    print(f"总文件数: {total_files}")
    print(f"验证通过: {valid_files}")
    print(f"验证失败: {invalid_files}")
    print(f"成功率: {report['summary']['success_rate']:.1f}%")
    print(f"总警告数: {total_warning_count}")
    print(f"总字数: {total_word_count:,}")
    print(f"总图片数: {total_image_count}")
    
    if error_types:
        print(f"\n常见错误类型:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {error_type}: {count} 次")
    
    # 保存报告文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存到: {output_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description='验证微信文章提取数据')
    parser.add_argument('path', help='要验证的文件或目录路径')
    parser.add_argument('--pattern', default='*.json', help='文件匹配模式（默认: *.json）')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告也视为错误）')
    parser.add_argument('--quiet', action='store_true', help='安静模式（减少输出）')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"错误: 路径不存在 {path}")
        sys.exit(1)
    
    # 验证文件或目录
    if path.is_file():
        if not args.quiet:
            print(f"验证单个文件: {path}")
        result = validate_single_file(path)
        results = [result]
    else:
        if not args.quiet:
            print(f"验证目录: {path}")
        results = validate_directory(path, args.pattern)
    
    if not results:
        print("没有找到要验证的文件")
        sys.exit(1)
    
    # 生成报告
    report = generate_validation_report(results, args.output)
    
    # 在严格模式下，有警告也视为失败
    if args.strict:
        for result in results:
            if result['warnings']:
                result['valid'] = False
                result['errors'].extend([f"警告: {w}" for w in result['warnings']])
    
    # 检查是否有验证失败的文件
    failed_files = [r for r in results if not r['valid']]
    if failed_files:
        if not args.quiet:
            print(f"\n验证失败的文件 ({len(failed_files)} 个):")
            for result in failed_files:
                print(f"  {result['file']}")
        sys.exit(1)
    else:
        if not args.quiet:
            print(f"\n所有文件验证通过! ✓")
        sys.exit(0)

if __name__ == '__main__':
    main()