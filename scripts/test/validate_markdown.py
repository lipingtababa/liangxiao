#!/usr/bin/env python3
"""
Markdown文件验证脚本

用于验证生成的Markdown文件是否符合格式要求
AI开发者可以使用这个脚本来验证他们生成的Markdown文件
"""

import os
import sys
import json
import yaml
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

def validate_yaml_frontmatter(content: str) -> Tuple[bool, Dict, List[str]]:
    """验证YAML frontmatter格式和必需字段"""
    errors = []
    frontmatter_data = {}
    
    # 检查是否以---开始
    if not content.startswith('---\n'):
        errors.append("文件必须以 '---' 开始")
        return False, {}, errors
    
    # 提取frontmatter
    try:
        # 找到第二个---的位置
        end_pos = content.find('\n---\n', 4)
        if end_pos == -1:
            errors.append("找不到frontmatter结束标记 '---'")
            return False, {}, errors
            
        frontmatter_content = content[4:end_pos]
        frontmatter_data = yaml.safe_load(frontmatter_content)
        
        if not isinstance(frontmatter_data, dict):
            errors.append("frontmatter必须是有效的YAML对象")
            return False, {}, errors
            
    except yaml.YAMLError as e:
        errors.append(f"YAML格式错误: {e}")
        return False, {}, errors
    
    # 检查必需字段
    required_fields = ['title', 'date', 'author', 'description']
    for field in required_fields:
        if field not in frontmatter_data:
            errors.append(f"缺少必需字段: {field}")
        elif not frontmatter_data[field]:
            errors.append(f"字段 {field} 不能为空")
    
    # 验证日期格式
    if 'date' in frontmatter_data:
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, str(frontmatter_data['date'])):
            errors.append(f"日期格式错误，应为 YYYY-MM-DD: {frontmatter_data['date']}")
    
    # 验证tags格式
    if 'tags' in frontmatter_data:
        tags = frontmatter_data['tags']
        if not isinstance(tags, list):
            errors.append("tags必须是数组格式")
        elif len(tags) == 0:
            errors.append("tags不能为空数组")
        elif len(tags) > 10:
            errors.append("tags数量不能超过10个")
    
    # 验证slug格式
    if 'slug' in frontmatter_data:
        slug = frontmatter_data['slug']
        slug_pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
        if not re.match(slug_pattern, slug):
            errors.append(f"slug格式错误，应只包含小写字母、数字和连字符: {slug}")
    
    return len(errors) == 0, frontmatter_data, errors

def validate_markdown_content(content: str, frontmatter_end: int) -> Tuple[bool, List[str]]:
    """验证Markdown内容部分"""
    errors = []
    
    # 获取内容部分
    markdown_content = content[frontmatter_end + 5:]  # 跳过 \n---\n
    
    if len(markdown_content.strip()) < 50:
        errors.append("Markdown内容太短，至少需要50个字符")
    
    # 检查是否有主标题
    if not re.search(r'^# .+', markdown_content, re.MULTILINE):
        errors.append("缺少主标题（# 格式）")
    
    # 检查图片引用格式
    image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', markdown_content)
    for alt_text, img_path in image_refs:
        # 检查本地图片路径
        if not img_path.startswith(('http://', 'https://')):
            if not img_path.startswith('images/'):
                errors.append(f"本地图片路径应以 'images/' 开头: {img_path}")
            
            # 检查图片文件扩展名
            if not re.search(r'\.(jpg|jpeg|png|webp)$', img_path.lower()):
                errors.append(f"不支持的图片格式: {img_path}")
    
    # 检查链接格式
    link_refs = re.findall(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', markdown_content)
    for link_text, link_url in link_refs:
        if link_url.startswith('http'):
            continue  # 外部链接，跳过
        # 检查内部链接格式
        if not link_url.startswith('/') and not link_url.startswith('#'):
            errors.append(f"内部链接格式可能有误: {link_url}")
    
    return len(errors) == 0, errors

def validate_single_markdown_file(file_path: Path) -> Dict[str, Any]:
    """验证单个Markdown文件"""
    result = {
        'file': str(file_path),
        'valid': False,
        'errors': [],
        'warnings': [],
        'metadata': {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            result['errors'].append("文件为空")
            return result
        
        # 验证frontmatter
        fm_valid, fm_data, fm_errors = validate_yaml_frontmatter(content)
        result['errors'].extend(fm_errors)
        result['metadata'] = fm_data
        
        if fm_valid:
            # 验证Markdown内容
            frontmatter_end = content.find('\n---\n', 4)
            if frontmatter_end != -1:
                content_valid, content_errors = validate_markdown_content(content, frontmatter_end)
                result['errors'].extend(content_errors)
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size < 500:
            result['warnings'].append(f"文件较小 ({file_size} 字节)")
        elif file_size > 50000:
            result['warnings'].append(f"文件较大 ({file_size} 字节)")
        
        # 计算统计信息
        result['stats'] = {
            'file_size': file_size,
            'line_count': len(content.splitlines()),
            'char_count': len(content),
            'word_count': len(content.split())
        }
        
        result['valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"读取文件时出错: {e}")
    
    return result

def validate_directory(directory: Path, pattern: str = "*.md") -> List[Dict[str, Any]]:
    """验证目录中的所有Markdown文件"""
    results = []
    
    if not directory.exists():
        print(f"错误: 目录不存在 {directory}")
        return results
    
    markdown_files = list(directory.glob(pattern))
    if not markdown_files:
        print(f"警告: 在 {directory} 中未找到匹配 {pattern} 的文件")
        return results
    
    print(f"找到 {len(markdown_files)} 个Markdown文件")
    
    for md_file in sorted(markdown_files):
        print(f"验证: {md_file.name}")
        result = validate_single_markdown_file(md_file)
        results.append(result)
        
        # 输出验证结果
        if result['valid']:
            print(f"  ✓ 验证通过")
        else:
            print(f"  ✗ 验证失败 ({len(result['errors'])} 个错误)")
            for error in result['errors'][:3]:  # 只显示前3个错误
                print(f"    - {error}")
            if len(result['errors']) > 3:
                print(f"    ... 还有 {len(result['errors']) - 3} 个错误")
        
        if result['warnings']:
            for warning in result['warnings']:
                print(f"  ⚠ {warning}")
    
    return results

def generate_validation_report(results: List[Dict[str, Any]], output_file: str = None):
    """生成验证报告"""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['valid'])
    invalid_files = total_files - valid_files
    
    # 统计错误类型
    error_types = {}
    for result in results:
        for error in result['errors']:
            error_type = error.split(':')[0] if ':' in error else error
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    report = {
        'summary': {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0
        },
        'error_types': error_types,
        'details': results
    }
    
    # 输出摘要
    print(f"\n=== 验证报告摘要 ===")
    print(f"总文件数: {total_files}")
    print(f"验证通过: {valid_files}")
    print(f"验证失败: {invalid_files}")
    print(f"成功率: {report['summary']['success_rate']:.1f}%")
    
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
    parser = argparse.ArgumentParser(description='验证Markdown文件格式')
    parser.add_argument('path', help='要验证的文件或目录路径')
    parser.add_argument('--pattern', default='*.md', help='文件匹配模式（默认: *.md）')
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
        result = validate_single_markdown_file(path)
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