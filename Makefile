# Makefile for 瑞典马工翻译管道
# 用于简化测试和开发流程

.PHONY: help install test test-unit test-integration test-e2e coverage lint clean run-pipeline

# 默认目标
help:
	@echo "瑞典马工翻译管道 - 可用命令:"
	@echo ""
	@echo "  make install         安装依赖"
	@echo "  make test           运行所有测试"
	@echo "  make test-unit      运行单元测试"
	@echo "  make test-integration 运行集成测试"
	@echo "  make test-e2e       运行端到端测试"
	@echo "  make coverage       生成测试覆盖率报告"
	@echo "  make lint           运行代码质量检查"
	@echo "  make clean          清理临时文件"
	@echo "  make run-pipeline   运行完整管道示例"

# 安装依赖
install:
	pip install -r requirements.txt
	pip install pytest-cov pytest-html flake8 pylint

# 运行所有测试
test:
	pytest scripts/tests -v --cov=scripts --cov-report=term-missing

# 运行单元测试
test-unit:
	pytest scripts/tests -m unit -v --cov=scripts

# 运行集成测试
test-integration:
	pytest scripts/tests -m integration -v

# 运行端到端测试
test-e2e:
	pytest scripts/tests -m e2e -v

# 生成覆盖率报告
coverage:
	pytest scripts/tests --cov=scripts --cov-report=html --cov-report=term
	@echo "覆盖率报告已生成: htmlcov/index.html"

# 代码质量检查
lint:
	@echo "运行flake8..."
	-flake8 scripts --exclude=tests --max-line-length=120
	@echo ""
	@echo "运行pylint..."
	-pylint scripts --ignore=tests

# 清理临时文件
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	rm -rf htmlcov
	rm -f .coverage
	rm -f coverage.xml
	rm -f report.html
	rm -f processed_articles.json
	rm -rf test-posts
	rm -f test-output.json

# 运行完整管道示例
run-pipeline:
	@echo "运行完整的翻译管道示例..."
	@echo "1. 提取内容（使用mock数据）"
	python scripts/extract_content_with_state.py --mock --output demo-extracted.json
	@echo ""
	@echo "2. 生成Markdown"
	python scripts/markdown_generator.py --input demo-extracted.json --output-dir demo-posts
	@echo ""
	@echo "3. 查看状态"
	python scripts/state_manager.py --status
	@echo ""
	@echo "完成！查看 demo-posts/ 目录获取生成的文章"

# 运行特定测试文件
test-file:
	@read -p "输入测试文件名（如 test_state_manager.py）: " file; \
	pytest scripts/tests/$$file -v

# 监视模式（需要安装pytest-watch）
watch:
	pytest-watch scripts/tests -- -v

# 生成测试报告
report:
	pytest scripts/tests --html=report.html --self-contained-html
	@echo "测试报告已生成: report.html"

# 检查测试覆盖率是否达标
check-coverage:
	pytest scripts/tests --cov=scripts --cov-fail-under=70