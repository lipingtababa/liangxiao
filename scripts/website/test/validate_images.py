#!/usr/bin/env python3
"""
图片文件验证脚本

用于验证下载的图片文件是否有效
AI开发者可以使用这个脚本来验证图片下载和处理结果
"""

import os
import sys
import json
import argparse
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Tuple
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def validate_image_file(file_path: Path) -> Dict[str, Any]:
    """验证单个图片文件"""
    result = {
        'file': str(file_path),
        'valid': False,
        'errors': [],
        'warnings': [],
        'metadata': {}
    }
    
    try:
        # 检查文件是否存在
        if not file_path.exists():
            result['errors'].append("文件不存在")
            return result
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        result['metadata']['file_size'] = file_size
        
        if file_size == 0:
            result['errors'].append("文件为空")
            return result
        elif file_size < 1024:  # 小于1KB
            result['warnings'].append(f"文件很小 ({file_size} 字节)")
        elif file_size > 10 * 1024 * 1024:  # 大于10MB
            result['warnings'].append(f"文件很大 ({file_size / 1024 / 1024:.1f} MB)")
        
        # 检查文件扩展名
        file_ext = file_path.suffix.lower()
        supported_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        if file_ext not in supported_extensions:
            result['warnings'].append(f"不常见的图片扩展名: {file_ext}")
        
        # 检查MIME类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        result['metadata']['mime_type'] = mime_type
        
        if mime_type and not mime_type.startswith('image/'):
            result['errors'].append(f"MIME类型不是图片: {mime_type}")
            return result
        
        # 使用PIL进行更详细的验证（如果可用）
        if PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    result['metadata']['format'] = img.format
                    result['metadata']['mode'] = img.mode
                    result['metadata']['size'] = img.size
                    
                    width, height = img.size
                    
                    # 检查图片尺寸
                    if width < 50 or height < 50:
                        result['warnings'].append(f"图片尺寸很小: {width}x{height}")
                    elif width > 5000 or height > 5000:
                        result['warnings'].append(f"图片尺寸很大: {width}x{height}")
                    
                    # 检查图片格式
                    if img.format not in ['JPEG', 'PNG', 'WebP', 'GIF']:
                        result['warnings'].append(f"不常见的图片格式: {img.format}")
                    
                    # 检查颜色模式
                    if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                        result['warnings'].append(f"不常见的颜色模式: {img.mode}")
                    
                    # 尝试验证图片数据完整性
                    img.verify()
                    
            except Exception as e:
                result['errors'].append(f"PIL验证失败: {e}")
                return result
        else:
            # 没有PIL时的简单验证
            try:
                # 尝试读取文件头来检查格式
                with open(file_path, 'rb') as f:
                    header = f.read(16)
                
                # 检查常见图片格式的文件头
                if header.startswith(b'\xFF\xD8\xFF'):
                    result['metadata']['format'] = 'JPEG'
                elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                    result['metadata']['format'] = 'PNG'
                elif header.startswith(b'RIFF') and b'WEBP' in header:
                    result['metadata']['format'] = 'WebP'
                elif header.startswith(b'GIF'):
                    result['metadata']['format'] = 'GIF'
                else:
                    result['warnings'].append("无法识别图片格式")
                    
            except Exception as e:
                result['errors'].append(f"读取文件头失败: {e}")
                return result
        
        # 检查文件名规范
        filename = file_path.name
        if not filename.replace('-', '').replace('_', '').replace('.', '').replace(' ', '').isalnum():
            result['warnings'].append("文件名包含特殊字符")
        
        if ' ' in filename:
            result['warnings'].append("文件名包含空格")
        
        if len(filename) > 100:
            result['warnings'].append("文件名过长")
        
        result['valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"验证过程出错: {e}")
    
    return result

def validate_directory(directory: Path, pattern: str = "*") -> List[Dict[str, Any]]:
    """验证目录中的所有图片文件"""
    results = []
    
    if not directory.exists():
        print(f"错误: 目录不存在 {directory}")
        return results
    
    # 查找图片文件
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(directory.glob(ext))
        image_files.extend(directory.glob(ext.upper()))
    
    # 如果指定了pattern，进一步过滤
    if pattern != "*":
        image_files = [f for f in image_files if f.match(pattern)]
    
    if not image_files:
        print(f"警告: 在 {directory} 中未找到图片文件")
        return results
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    for img_file in sorted(image_files):
        print(f"验证: {img_file.name}")
        result = validate_image_file(img_file)
        results.append(result)
        
        # 输出验证结果
        if result['valid']:
            print(f"  ✓ 验证通过")
            if result['warnings']:
                print(f"    ({len(result['warnings'])} 个警告)")
        else:
            print(f"  ✗ 验证失败 ({len(result['errors'])} 个错误)")
            for error in result['errors'][:2]:
                print(f"    - {error}")
            if len(result['errors']) > 2:
                print(f"    ... 还有 {len(result['errors']) - 2} 个错误")
        
        # 显示元数据
        metadata = result['metadata']
        if 'size' in metadata:
            width, height = metadata['size']
            size_mb = metadata.get('file_size', 0) / 1024 / 1024
            print(f"    {metadata.get('format', 'Unknown')} | {width}x{height} | {size_mb:.1f}MB")
        elif 'file_size' in metadata:
            size_mb = metadata['file_size'] / 1024 / 1024
            print(f"    {metadata.get('format', 'Unknown')} | {size_mb:.1f}MB")
    
    return results

def validate_from_json(json_file: Path, base_dir: Path = None) -> List[Dict[str, Any]]:
    """从JSON文件中的图片信息验证图片文件"""
    results = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        images = data.get('images', [])
        if not images:
            print(f"JSON文件中没有图片信息")
            return results
        
        print(f"从JSON文件中找到 {len(images)} 个图片记录")
        
        for i, img_info in enumerate(images):
            img_path = None
            
            # 尝试不同的路径字段
            if 'local_path' in img_info:
                img_path = Path(img_info['local_path'])
            elif 'local_filename' in img_info:
                if base_dir:
                    img_path = base_dir / img_info['local_filename']
                else:
                    img_path = Path(img_info['local_filename'])
            
            if not img_path:
                print(f"  图片 {i+1}: 无法确定本地路径")
                continue
            
            # 如果路径是相对路径且指定了base_dir
            if base_dir and not img_path.is_absolute():
                img_path = base_dir / img_path
            
            print(f"验证: {img_path.name}")
            result = validate_image_file(img_path)
            
            # 添加额外的元数据
            result['metadata']['json_index'] = i
            result['metadata']['original_url'] = img_info.get('src', '')
            result['metadata']['alt_text'] = img_info.get('alt', '')
            
            results.append(result)
            
            # 输出结果
            if result['valid']:
                print(f"  ✓ 验证通过")
            else:
                print(f"  ✗ 验证失败")
                for error in result['errors'][:2]:
                    print(f"    - {error}")
    
    except Exception as e:
        print(f"处理JSON文件时出错: {e}")
    
    return results

def generate_validation_report(results: List[Dict[str, Any]], output_file: str = None):
    """生成验证报告"""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['valid'])
    invalid_files = total_files - valid_files
    
    # 统计信息
    total_size = sum(r['metadata'].get('file_size', 0) for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)
    
    # 统计格式分布
    formats = {}
    sizes = []
    for result in results:
        fmt = result['metadata'].get('format', 'Unknown')
        formats[fmt] = formats.get(fmt, 0) + 1
        
        if 'size' in result['metadata']:
            sizes.append(result['metadata']['size'])
    
    report = {
        'summary': {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0,
            'total_warnings': total_warnings,
            'total_size_mb': total_size / 1024 / 1024,
            'format_distribution': formats
        },
        'details': results
    }
    
    # 输出摘要
    print(f"\n=== 图片验证报告 ===")
    print(f"总文件数: {total_files}")
    print(f"验证通过: {valid_files}")
    print(f"验证失败: {invalid_files}")
    print(f"成功率: {report['summary']['success_rate']:.1f}%")
    print(f"总警告数: {total_warnings}")
    print(f"总大小: {total_size / 1024 / 1024:.1f} MB")
    
    if formats:
        print(f"\n格式分布:")
        for fmt, count in sorted(formats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {fmt}: {count} 个")
    
    if sizes:
        widths = [s[0] for s in sizes]
        heights = [s[1] for s in sizes]
        print(f"\n尺寸统计:")
        print(f"  - 平均宽度: {sum(widths) / len(widths):.0f}px")
        print(f"  - 平均高度: {sum(heights) / len(heights):.0f}px")
        print(f"  - 最大尺寸: {max(widths)}x{max(heights)}")
        print(f"  - 最小尺寸: {min(widths)}x{min(heights)}")
    
    # 保存报告文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存到: {output_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description='验证图片文件')
    parser.add_argument('path', help='要验证的文件、目录或JSON文件路径')
    parser.add_argument('--pattern', default='*', help='文件匹配模式（默认: *）')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--json-mode', action='store_true', help='从JSON文件中读取图片信息进行验证')
    parser.add_argument('--base-dir', help='图片文件的基础目录（JSON模式时使用）')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告也视为错误）')
    parser.add_argument('--quiet', action='store_true', help='安静模式（减少输出）')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"错误: 路径不存在 {path}")
        sys.exit(1)
    
    # 根据模式验证
    if args.json_mode:
        if not args.quiet:
            print(f"从JSON文件验证图片: {path}")
        base_dir = Path(args.base_dir) if args.base_dir else None
        results = validate_from_json(path, base_dir)
    elif path.is_file():
        if not args.quiet:
            print(f"验证单个图片文件: {path}")
        result = validate_image_file(path)
        results = [result]
    else:
        if not args.quiet:
            print(f"验证图片目录: {path}")
        results = validate_directory(path, args.pattern)
    
    if not results:
        print("没有找到要验证的图片文件")
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
            print(f"\n验证失败的图片 ({len(failed_files)} 个):")
            for result in failed_files:
                print(f"  {Path(result['file']).name}")
        sys.exit(1)
    else:
        if not args.quiet:
            print(f"\n所有图片验证通过! ✓")
        sys.exit(0)

if __name__ == '__main__':
    main()