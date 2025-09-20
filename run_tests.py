#!/usr/bin/env python3
"""
测试运行器
提供便捷的测试执行和报告生成功能
"""

import sys
import os
import argparse
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class TestRunner:
    """测试运行器"""

    def __init__(self, verbose: bool = False):
        """
        初始化测试运行器

        Args:
            verbose: 是否显示详细输出
        """
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.test_results = []

    def run_unit_tests(self, coverage: bool = True) -> Dict[str, Any]:
        """运行单元测试"""
        print("\n" + "=" * 60)
        print("运行单元测试...")
        print("=" * 60)

        cmd = ["python", "-m", "pytest", "tests/unit/", "-v"]
        if coverage:
            cmd.extend(["--cov=scripts", "--cov-report=term", "--cov-report=html"])

        result = self._run_command(cmd)
        self.test_results.append({
            "type": "unit",
            "status": result["status"],
            "duration": result["duration"],
            "output": result["output"]
        })
        return result

    def run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        print("\n" + "=" * 60)
        print("运行集成测试...")
        print("=" * 60)

        cmd = ["python", "-m", "pytest", "tests/integration/", "-v"]
        result = self._run_command(cmd)
        self.test_results.append({
            "type": "integration",
            "status": result["status"],
            "duration": result["duration"],
            "output": result["output"]
        })
        return result

    def run_e2e_tests(self) -> Dict[str, Any]:
        """运行端到端测试"""
        print("\n" + "=" * 60)
        print("运行端到端测试...")
        print("=" * 60)

        cmd = ["python", "-m", "pytest", "tests/e2e/", "-v"]
        result = self._run_command(cmd)
        self.test_results.append({
            "type": "e2e",
            "status": result["status"],
            "duration": result["duration"],
            "output": result["output"]
        })
        return result

    def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        print("\n" + "=" * 60)
        print("运行性能测试...")
        print("=" * 60)

        cmd = ["python", "-m", "pytest", "tests/performance/", "-v", "--benchmark-only"]
        result = self._run_command(cmd)
        self.test_results.append({
            "type": "performance",
            "status": result["status"],
            "duration": result["duration"],
            "output": result["output"]
        })
        return result

    def run_specific_test(self, test_file: str) -> Dict[str, Any]:
        """运行特定测试文件"""
        print(f"\n运行测试: {test_file}")
        cmd = ["python", "-m", "pytest", test_file, "-v"]
        return self._run_command(cmd)

    def run_marked_tests(self, marker: str) -> Dict[str, Any]:
        """运行带特定标记的测试"""
        print(f"\n运行标记为 '{marker}' 的测试...")
        cmd = ["python", "-m", "pytest", "-m", marker, "-v"]
        return self._run_command(cmd)

    def run_linting(self) -> Dict[str, Any]:
        """运行代码检查"""
        print("\n" + "=" * 60)
        print("运行代码检查...")
        print("=" * 60)

        results = {}

        # Flake8
        print("\n运行 flake8...")
        flake8_cmd = ["flake8", "scripts/", "tests/", "--max-line-length=120", "--ignore=E203,W503"]
        results["flake8"] = self._run_command(flake8_cmd)

        # Black
        print("\n检查 Black 格式...")
        black_cmd = ["black", "--check", "scripts/", "tests/"]
        results["black"] = self._run_command(black_cmd)

        # isort
        print("\n检查导入排序...")
        isort_cmd = ["isort", "--check-only", "scripts/", "tests/"]
        results["isort"] = self._run_command(isort_cmd)

        return results

    def run_security_scan(self) -> Dict[str, Any]:
        """运行安全扫描"""
        print("\n" + "=" * 60)
        print("运行安全扫描...")
        print("=" * 60)

        results = {}

        # Safety
        print("\n检查依赖安全性...")
        safety_cmd = ["safety", "check", "-r", "requirements.txt"]
        results["safety"] = self._run_command(safety_cmd)

        # Bandit
        print("\n运行 Bandit 扫描...")
        bandit_cmd = ["bandit", "-r", "scripts/", "-ll"]
        results["bandit"] = self._run_command(bandit_cmd)

        return results

    def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """执行命令并返回结果"""
        start_time = time.time()

        try:
            if self.verbose:
                print(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            duration = time.time() - start_time
            status = "success" if result.returncode == 0 else "failure"

            return {
                "status": status,
                "returncode": result.returncode,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "status": "error",
                "returncode": -1,
                "duration": duration,
                "output": "",
                "error": str(e)
            }

    def generate_report(self, output_file: Optional[str] = None):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["status"] == "success"),
                "failed": sum(1 for r in self.test_results if r["status"] == "failure"),
                "errors": sum(1 for r in self.test_results if r["status"] == "error")
            },
            "results": self.test_results
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n测试报告已保存到: {output_file}")

        # 打印摘要
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        print(f"总计: {report['summary']['total']}")
        print(f"通过: {report['summary']['passed']}")
        print(f"失败: {report['summary']['failed']}")
        print(f"错误: {report['summary']['errors']}")

        return report

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("运行所有测试套件")
        print("=" * 60)

        # 单元测试
        self.run_unit_tests()

        # 集成测试
        self.run_integration_tests()

        # 端到端测试
        self.run_e2e_tests()

        # 性能测试（可选）
        # self.run_performance_tests()

        # 生成报告
        report = self.generate_report("test-report.json")

        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行测试套件')

    # 测试类型
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--e2e', action='store_true', help='运行端到端测试')
    parser.add_argument('--performance', action='store_true', help='运行性能测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')

    # 其他选项
    parser.add_argument('--lint', action='store_true', help='运行代码检查')
    parser.add_argument('--security', action='store_true', help='运行安全扫描')
    parser.add_argument('--file', help='运行特定测试文件')
    parser.add_argument('--marker', help='运行带特定标记的测试')
    parser.add_argument('--no-coverage', action='store_true', help='禁用覆盖率报告')
    parser.add_argument('--report', help='生成测试报告文件')
    parser.add_argument('--verbose', action='store_true', help='显示详细输出')

    args = parser.parse_args()

    # 创建测试运行器
    runner = TestRunner(verbose=args.verbose)

    # 执行相应的测试
    if args.all:
        runner.run_all_tests()
    else:
        if args.unit:
            runner.run_unit_tests(coverage=not args.no_coverage)

        if args.integration:
            runner.run_integration_tests()

        if args.e2e:
            runner.run_e2e_tests()

        if args.performance:
            runner.run_performance_tests()

        if args.lint:
            runner.run_linting()

        if args.security:
            runner.run_security_scan()

        if args.file:
            runner.run_specific_test(args.file)

        if args.marker:
            runner.run_marked_tests(args.marker)

        # 如果没有指定任何测试，运行默认测试
        if not any([args.unit, args.integration, args.e2e, args.performance,
                   args.lint, args.security, args.file, args.marker]):
            print("没有指定测试类型，运行单元测试...")
            runner.run_unit_tests()

    # 生成报告
    if args.report:
        runner.generate_report(args.report)
    elif runner.test_results:
        runner.generate_report()

    # 返回状态码
    failed_tests = sum(1 for r in runner.test_results if r["status"] != "success")
    sys.exit(failed_tests)


if __name__ == '__main__':
    main()