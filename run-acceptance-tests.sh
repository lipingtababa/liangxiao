#!/bin/bash

# 运行验收测试脚本
# 确保测试环境正确设置并运行所有验收测试

set -e

echo "🚀 准备运行验收测试..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Node.js版本
NODE_VERSION=$(node -v)
echo "📦 Node.js版本: $NODE_VERSION"

# 检查Python版本
PYTHON_VERSION=$(python3 --version)
echo "🐍 Python版本: $PYTHON_VERSION"

# 安装依赖
echo ""
echo "📦 安装依赖..."
npm ci

# 安装Playwright浏览器
echo ""
echo "🌐 安装测试浏览器..."
npx playwright install chromium

# 创建必要的目录
echo ""
echo "📁 创建测试目录..."
mkdir -p test-results
mkdir -p test-results/screenshots
mkdir -p test-results/data
mkdir -p posts
mkdir -p public/images

# 清理旧的测试结果
echo ""
echo "🧹 清理旧的测试结果..."
rm -rf test-results/*

# 构建应用
echo ""
echo "🏗️ 构建应用..."
npm run build

# 启动应用服务器
echo ""
echo "🚀 启动应用服务器..."
npm start &
SERVER_PID=$!
sleep 5

# 检查服务器是否启动成功
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo -e "${GREEN}✅ 服务器启动成功${NC}"
else
    echo -e "${RED}❌ 服务器启动失败${NC}"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# 运行测试
echo ""
echo "🧪 开始运行验收测试..."
echo "================================"

# 定义测试套件
TEST_SUITES=("extraction" "translation" "publishing" "e2e")
FAILED_SUITES=()

# 运行每个测试套件
for suite in "${TEST_SUITES[@]}"; do
    echo ""
    echo -e "${YELLOW}📝 运行测试套件: $suite${NC}"

    case $suite in
        "extraction")
            FEATURE_FILE="features/01_article_extraction.feature"
            ;;
        "translation")
            FEATURE_FILE="features/02_translation.feature"
            ;;
        "publishing")
            FEATURE_FILE="features/03_publishing.feature"
            ;;
        "e2e")
            FEATURE_FILE="features/04_end_to_end_workflow.feature"
            ;;
    esac

    if npm run test:acceptance -- $FEATURE_FILE; then
        echo -e "${GREEN}✅ $suite 测试通过${NC}"
    else
        echo -e "${RED}❌ $suite 测试失败${NC}"
        FAILED_SUITES+=($suite)
    fi
done

# 生成HTML报告
echo ""
echo "📊 生成测试报告..."
if [ -f test-results/cucumber-report.json ]; then
    npx cucumber-html-reporter \
        --input test-results/cucumber-report.json \
        --output test-results/cucumber-report.html \
        --reportSuiteAsScenarios true \
        --launchReport false
    echo -e "${GREEN}✅ 报告生成成功: test-results/cucumber-report.html${NC}"
fi

# 停止服务器
echo ""
echo "🛑 停止应用服务器..."
kill $SERVER_PID 2>/dev/null || true

# 显示测试结果汇总
echo ""
echo "================================"
echo "📊 测试结果汇总"
echo "================================"

TOTAL_SUITES=${#TEST_SUITES[@]}
PASSED_SUITES=$((TOTAL_SUITES - ${#FAILED_SUITES[@]}))

echo "总测试套件: $TOTAL_SUITES"
echo -e "${GREEN}通过: $PASSED_SUITES${NC}"
echo -e "${RED}失败: ${#FAILED_SUITES[@]}${NC}"

if [ ${#FAILED_SUITES[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}失败的测试套件:${NC}"
    for suite in "${FAILED_SUITES[@]}"; do
        echo -e "${RED}  - $suite${NC}"
    done
    echo ""
    echo -e "${YELLOW}💡 提示: 查看 test-results/ 目录获取详细信息${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}🎉 所有验收测试通过！${NC}"
fi

# 设置正确的文件权限（确保组用户可写）
chmod -R g+w test-results/ 2>/dev/null || true
chmod -R g+w posts/ 2>/dev/null || true
chmod -R g+w public/images/ 2>/dev/null || true

echo ""
echo "✨ 测试完成！"