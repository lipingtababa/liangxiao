#!/bin/bash

# 验证验收测试设置脚本
echo "🔍 验证验收测试设置..."

# 检查必要的文件
echo ""
echo "📁 检查文件结构..."
FILES_TO_CHECK=(
    "cucumber.js"
    "features/00_smoke_test.feature"
    "features/01_article_extraction.feature"
    "features/02_translation.feature"
    "features/03_publishing.feature"
    "features/04_end_to_end_workflow.feature"
    "features/step_definitions/common_steps.js"
    "features/step_definitions/extraction_steps.js"
    "features/step_definitions/translation_steps.js"
    "features/step_definitions/publishing_steps.js"
    "features/support/world.js"
    "features/README.md"
)

MISSING_FILES=()
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        MISSING_FILES+=("$file")
    fi
done

# 检查依赖
echo ""
echo "📦 检查依赖..."
DEPS=("@cucumber/cucumber" "chai" "playwright")
for dep in "${DEPS[@]}"; do
    if grep -q "\"$dep\"" package.json; then
        echo "✅ $dep 已安装"
    else
        echo "❌ $dep 未安装"
    fi
done

# 运行冒烟测试
echo ""
echo "🧪 运行冒烟测试..."
NODE_ENV=test npx cucumber-js features/00_smoke_test.feature --format progress-bar --fail-fast

if [ $? -eq 0 ]; then
    echo ""
    echo "✨ 验收测试设置完成！"
    echo ""
    echo "可用的命令："
    echo "  npm run test:acceptance          - 运行所有验收测试"
    echo "  npm run test:acceptance:watch    - 监视模式"
    echo "  ./run-acceptance-tests.sh        - 完整测试流程"
else
    echo ""
    echo "⚠️ 冒烟测试失败，请检查设置"
    exit 1
fi

# 设置文件权限
chmod g+w features/ -R 2>/dev/null || true
chmod g+w test-results/ -R 2>/dev/null || true