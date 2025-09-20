#!/usr/bin/env python3
"""
测试运行器 - 执行所有测试并生成报告
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=True):
    """
    运行测试

    Args:
        test_type: 测试类型 (all, unit, integration, e2e)
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
    """
    # 构建pytest命令
    cmd = ["pytest"]

    # 添加测试路径
    test_dir = Path(__file__).parent / "tests"
    cmd.append(str(test_dir))

    # 根据测试类型添加标记
    if test_type != "all":
        cmd.extend(["-m", test_type])

    # 详细输出
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # 覆盖率
    if coverage:
        cmd.extend([
            "--cov=scripts",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml"
        ])

    # 其他选项
    cmd.extend([
        "--tb=short",
        "--color=yes",
        "-W", "ignore::DeprecationWarning"
    ])

    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 60)

    # 执行测试
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"测试运行失败: {e}")
        return 1


def run_specific_test(test_file, test_function=None):
    """
    运行特定的测试文件或函数

    Args:
        test_file: 测试文件路径
        test_function: 测试函数名（可选）
    """
    cmd = ["pytest", "-v"]

    if test_function:
        cmd.append(f"{test_file}::{test_function}")
    else:
        cmd.append(test_file)

    print(f"运行命令: {' '.join(cmd)}")
    subprocess.run(cmd)


def generate_coverage_report():
    """生成详细的覆盖率报告"""
    print("\n生成覆盖率报告...")
    subprocess.run(["coverage", "report", "-m"], check=False)
    subprocess.run(["coverage", "html"], check=False)
    print("HTML覆盖率报告已生成: htmlcov/index.html")


def run_linting():
    """运行代码质量检查"""
    print("\n运行代码质量检查...")

    # 运行flake8（如果安装）
    try:
        subprocess.run(["flake8", "scripts", "--exclude=tests"], check=False)
    except FileNotFoundError:
        print("flake8未安装，跳过")

    # 运行pylint（如果安装）
    try:
        subprocess.run(["pylint", "scripts", "--ignore=tests"], check=False)
    except FileNotFoundError:
        print("pylint未安装，跳过")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行测试套件")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "e2e"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="运行代码质量检查"
    )
    parser.add_argument(
        "--file",
        help="运行特定的测试文件"
    )
    parser.add_argument(
        "--function",
        help="运行特定的测试函数（需要配合--file使用）"
    )

    args = parser.parse_args()

    # 运行代码质量检查
    if args.lint:
        run_linting()

    # 运行特定测试
    if args.file:
        run_specific_test(args.file, args.function)
        return 0

    # 运行测试套件
    exit_code = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage
    )

    # 生成覆盖率报告
    if not args.no_coverage and exit_code == 0:
        generate_coverage_report()

    # 显示结果
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())