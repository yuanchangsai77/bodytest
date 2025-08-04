#!/bin/bash

# LLM API 项目运行脚本
# 支持 python3 和 uv run 两种方式

echo "🚀 LLM API 项目运行脚本"
echo "=========================="

# 检查 uv 是否可用
if command -v uv &> /dev/null; then
    echo "✅ 找到 uv: $(which uv)"
    echo "📋 uv版本: $(uv --version)"
    UV_AVAILABLE=true
else
    echo "⚠️  未找到 uv 命令"
    UV_AVAILABLE=false
fi

# 检查 python3 是否可用
if command -v python3 &> /dev/null; then
    echo "✅ 找到 python3: $(which python3)"
    echo "📋 Python版本: $(python3 --version)"
    PYTHON3_AVAILABLE=true
else
    echo "❌ 未找到 python3 命令"
    PYTHON3_AVAILABLE=false
fi

if [ "$UV_AVAILABLE" = false ] && [ "$PYTHON3_AVAILABLE" = false ]; then
    echo "❌ 没有可用的Python运行环境"
    exit 1
fi

echo ""
echo "📁 可用的运行命令:"
echo "1. 测试 LLM API 配置"
echo "2. 运行 shell 示例"
echo "3. 运行 pyshell 示例"
echo "4. 运行示例用法"
echo ""

# 询问用户要运行哪个脚本
echo "请选择要运行的脚本 (1-4) 或按 Enter 退出:"
read -r choice

# 询问运行方式
if [ "$UV_AVAILABLE" = true ] && [ "$PYTHON3_AVAILABLE" = true ]; then
    echo ""
    echo "选择运行方式:"
    echo "u) 使用 uv run (推荐,自动管理依赖)"
    echo "p) 使用 python3"
    echo ""
    echo "请选择运行方式 (u/p):"
    read -r run_method
elif [ "$UV_AVAILABLE" = true ]; then
    run_method="u"
    echo "🔧 使用 uv run"
else
    run_method="p"
    echo "🔧 使用 python3"
fi

# 设置运行命令
if [ "$run_method" = "u" ]; then
    RUN_CMD="uv run python"
else
    RUN_CMD="python3"
fi

case $choice in
    1)
        echo "🧪 运行 LLM API 测试..."
        $RUN_CMD test_llm_api.py
        ;;
    2)
        echo "🔧 运行 shell 示例..."
        $RUN_CMD shell/llm_example.py
        ;;
    3)
        echo "🔧 运行 pyshell 示例..."
        $RUN_CMD shell/pyshell/llm_example.py
        ;;
    4)
        echo "📖 运行示例用法..."
        $RUN_CMD -c "import asyncio; from llmapiconfig.example_usage import main; asyncio.run(main())"
        ;;
    "")
        echo "👋 退出"
        ;;
    *)
        echo "❌ 无效选择"
        ;;
esac