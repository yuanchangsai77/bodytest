"""
从shell文件夹调用LLM API的示例 - 优化版本
演示如何在项目的任何子文件夹中使用llmapiconfig
减少不必要的API消耗
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

from llmapiconfig.llm_client import simple_chat, chat
from llmapiconfig.settings import settings


async def shell_ai_assistant():
    """Shell AI助手示例"""
    print("🤖 Shell AI助手启动")
    print(f"当前使用的AI模型: {settings.default_provider} - {settings.get_config().model}")
    print("=" * 50)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n💬 请输入你的问题 (输入'quit'退出): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见!")
                break
            
            if not user_input:
                continue
            
            print("🤔 AI思考中...")
            
            # 调用AI
            response = await simple_chat(user_input)
            print(f"🤖 AI回复: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 用户中断,再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            print("请检查网络连接和API配置")


async def code_analysis_example():
    """代码分析示例 - 可选执行"""
    print("\n🔍 代码分析示例")
    print("=" * 30)
    
    # 示例代码
    code_snippet = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
    '''
    
    prompt = f"""
请分析以下Python代码:
{code_snippet}

请提供:
1. 代码功能说明
2. 时间复杂度分析
3. 优化建议
"""
    
    try:
        response = await simple_chat(prompt)
        print("📝 代码分析结果:")
        print(response)
    except Exception as e:
        print(f"❌ 代码分析失败: {e}")


async def multi_provider_comparison():
    """多提供商对比示例 - 可选执行"""
    print("\n🔄 多提供商对比示例")
    print("=" * 30)
    
    question = "请用一句话解释什么是机器学习"
    providers = ["gemini", "openai", "claude", "qwen", "zhipu"]
    
    for provider in providers:
        try:
            if settings.validate_config(provider):
                print(f"\n🤖 {provider.upper()}:")
                response = await simple_chat(question, provider=provider)
                print(f"   {response}")
            else:
                print(f"\n⚠️  {provider.upper()}: 配置无效,跳过")
        except Exception as e:
            print(f"\n❌ {provider.upper()}: 调用失败 - {e}")


def show_menu():
    """显示菜单选项"""
    print("\n📋 请选择功能:")
    print("1. 启动AI助手 (交互式对话)")
    print("2. 运行代码分析示例 (消耗1次API调用)")
    print("3. 运行多提供商对比 (消耗多次API调用)")
    print("4. 查看配置状态 (不消耗API)")
    print("0. 退出")
    return input("请输入选项 (0-4): ").strip()


def show_config_status():
    """显示配置状态 - 不消耗API"""
    print("\n⚙️  配置状态检查:")
    print("=" * 30)
    
    providers = ["gemini", "openai", "claude", "qwen", "zhipu"]
    
    for provider in providers:
        status = "✅ 已配置" if settings.validate_config(provider) else "❌ 未配置"
        print(f"{provider.upper()}: {status}")
    
    print(f"\n默认提供商: {settings.default_provider.upper()}")


async def main():
    """主函数 - 优化版本"""
    print("🚀 Shell文件夹LLM API调用示例 (优化版)")
    print(f"📁 当前工作目录: {os.getcwd()}")
    print(f"📁 项目根目录: {project_root}")
    
    # 检查默认配置
    if not settings.validate_config():
        print("❌ 默认LLM API配置无效,请检查.env文件中的API密钥设置")
        print("你仍然可以查看配置状态或配置其他提供商")
    else:
        print("✅ 默认LLM API配置有效")
    
    # 菜单循环
    while True:
        choice = show_menu()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            if settings.validate_config():
                await shell_ai_assistant()
            else:
                print("❌ 请先配置有效的API密钥")
        elif choice == "2":
            if settings.validate_config():
                await code_analysis_example()
            else:
                print("❌ 请先配置有效的API密钥")
        elif choice == "3":
            print("⚠️  警告: 此操作将对所有配置的提供商进行API调用")
            confirm = input("确认执行? (y/N): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                await multi_provider_comparison()
            else:
                print("已取消")
        elif choice == "4":
            show_config_status()
        else:
            print("❌ 无效选项,请重新选择")


if __name__ == "__main__":
    asyncio.run(main())