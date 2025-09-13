#!/bin/bash

# 测试GitHub Actions工作流配置
# 用于本地验证工作流语法和逻辑

echo "================================================"
echo "GitHub Actions 工作流测试脚本"
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_workflow_syntax() {
    echo -e "\n${YELLOW}1. 检查工作流文件语法${NC}"

    workflow_file=".github/workflows/process-articles.yml"

    if [ ! -f "$workflow_file" ]; then
        echo -e "${RED}✗ 工作流文件不存在: $workflow_file${NC}"
        return 1
    fi

    # 检查YAML语法（需要安装yamllint）
    if command -v yamllint &> /dev/null; then
        if yamllint "$workflow_file" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ YAML语法正确${NC}"
        else
            echo -e "${RED}✗ YAML语法错误${NC}"
            yamllint "$workflow_file"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ yamllint未安装，跳过语法检查${NC}"
        echo "  安装命令: pip install yamllint"
    fi

    # 检查必要的字段
    echo -e "\n${YELLOW}2. 检查必要的工作流字段${NC}"

    if grep -q "^name:" "$workflow_file"; then
        echo -e "${GREEN}✓ 包含name字段${NC}"
    else
        echo -e "${RED}✗ 缺少name字段${NC}"
    fi

    if grep -q "^on:" "$workflow_file"; then
        echo -e "${GREEN}✓ 包含触发器配置${NC}"
    else
        echo -e "${RED}✗ 缺少触发器配置${NC}"
    fi

    if grep -q "^jobs:" "$workflow_file"; then
        echo -e "${GREEN}✓ 包含jobs定义${NC}"
    else
        echo -e "${RED}✗ 缺少jobs定义${NC}"
    fi
}

test_file_monitoring() {
    echo -e "\n${YELLOW}3. 测试文件监控配置${NC}"

    workflow_file=".github/workflows/process-articles.yml"

    # 检查是否监控articles.txt
    if grep -q "paths:" "$workflow_file" && grep -q "'articles.txt'" "$workflow_file"; then
        echo -e "${GREEN}✓ 配置了articles.txt文件监控${NC}"
    else
        echo -e "${RED}✗ 未配置articles.txt文件监控${NC}"
    fi

    # 检查是否支持手动触发
    if grep -q "workflow_dispatch:" "$workflow_file"; then
        echo -e "${GREEN}✓ 支持手动触发${NC}"
    else
        echo -e "${YELLOW}⚠ 不支持手动触发${NC}"
    fi
}

test_python_scripts() {
    echo -e "\n${YELLOW}4. 检查Python脚本可用性${NC}"

    # 检查提取脚本
    if [ -f "scripts/extract_content_starter.py" ]; then
        echo -e "${GREEN}✓ 提取脚本存在${NC}"

        # 测试脚本语法
        if python -m py_compile scripts/extract_content_starter.py 2>/dev/null; then
            echo -e "${GREEN}✓ 提取脚本语法正确${NC}"
        else
            echo -e "${RED}✗ 提取脚本有语法错误${NC}"
        fi
    else
        echo -e "${RED}✗ 提取脚本不存在${NC}"
    fi

    # 检查翻译脚本（可选）
    if [ -f "scripts/translate_article.py" ]; then
        echo -e "${GREEN}✓ 翻译脚本存在${NC}"
    else
        echo -e "${YELLOW}⚠ 翻译脚本不存在（将跳过翻译步骤）${NC}"
    fi

    # 检查Markdown生成脚本（可选）
    if [ -f "scripts/generate_markdown.py" ]; then
        echo -e "${GREEN}✓ Markdown生成脚本存在${NC}"
    else
        echo -e "${YELLOW}⚠ Markdown生成脚本不存在（将使用简单生成）${NC}"
    fi
}

test_dependencies() {
    echo -e "\n${YELLOW}5. 检查依赖配置${NC}"

    # 检查requirements.txt
    if [ -f "requirements.txt" ]; then
        echo -e "${GREEN}✓ requirements.txt存在${NC}"

        # 检查是否包含必要的包
        if grep -q "requests" requirements.txt; then
            echo -e "${GREEN}✓ 包含requests库${NC}"
        else
            echo -e "${YELLOW}⚠ 未包含requests库${NC}"
        fi
    else
        echo -e "${RED}✗ requirements.txt不存在${NC}"
    fi
}

test_articles_file() {
    echo -e "\n${YELLOW}6. 检查articles.txt文件${NC}"

    if [ -f "articles.txt" ]; then
        echo -e "${GREEN}✓ articles.txt存在${NC}"

        # 统计URL数量
        url_count=$(grep -c "^http" articles.txt || echo 0)
        echo -e "  包含 ${url_count} 个URL"

        # 检查格式
        if grep -v "^http\|^$\|^#" articles.txt > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ 文件包含非URL行${NC}"
        fi
    else
        echo -e "${RED}✗ articles.txt不存在${NC}"
    fi
}

simulate_workflow() {
    echo -e "\n${YELLOW}7. 模拟工作流执行${NC}"

    # 创建临时目录
    temp_dir=$(mktemp -d)
    echo "使用临时目录: $temp_dir"

    # 模拟提取步骤
    echo -e "\n${YELLOW}模拟提取文章...${NC}"
    if [ -f "scripts/extract_content_starter.py" ]; then
        # 使用mock模式测试
        python scripts/extract_content_starter.py --mock --output "$temp_dir/test.json" 2>/dev/null

        if [ -f "$temp_dir/test.json" ]; then
            echo -e "${GREEN}✓ 提取模拟成功${NC}"
        else
            echo -e "${RED}✗ 提取模拟失败${NC}"
        fi
    fi

    # 清理临时目录
    rm -rf "$temp_dir"
}

# 主测试流程
main() {
    echo "开始测试..."
    echo "当前目录: $(pwd)"

    # 运行各项测试
    test_workflow_syntax
    test_file_monitoring
    test_python_scripts
    test_dependencies
    test_articles_file
    simulate_workflow

    echo -e "\n================================================"
    echo -e "${GREEN}测试完成！${NC}"
    echo "================================================"

    echo -e "\n${YELLOW}后续步骤：${NC}"
    echo "1. 提交工作流文件到GitHub"
    echo "2. 在GitHub Actions页面查看工作流状态"
    echo "3. 修改articles.txt文件测试自动触发"
    echo "4. 配置部署webhook（可选）: DEPLOY_HOOK"
    echo "5. 配置通知webhook（可选）: NOTIFICATION_WEBHOOK"
}

# 运行主函数
main