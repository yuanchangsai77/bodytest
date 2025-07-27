#!/usr/bin/env python3
"""
高级测试脚本 - 验证uv Python环境的完整功能
"""

import sys
import os
import json
from datetime import datetime
import requests

def test_basic_functionality():
    """测试基本Python功能"""
    print("🔍 测试基本Python功能...")
    
    # 测试列表推导式
    squares = [x**2 for x in range(1, 6)]
    print(f"   平方数列表: {squares}")
    
    # 测试字典操作
    data = {"name": "uv测试", "version": "1.0", "status": "running"}
    print(f"   字典操作: {json.dumps(data, ensure_ascii=False)}")
    
    # 测试文件操作
    test_file = "temp_test.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("uv环境测试文件\n")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    os.remove(test_file)
    print(f"   文件操作: {content}")
    print("✅ 基本功能测试通过")

def test_network_functionality():
    """测试网络功能"""
    print("\n🌐 测试网络功能...")
    
    try:
        # 测试HTTP请求
        response = requests.get("https://httpbin.org/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   HTTP请求成功: {data.get('slideshow', {}).get('title', 'N/A')}")
        else:
            print(f"   HTTP请求失败: {response.status_code}")
    except Exception as e:
        print(f"   网络请求异常: {e}")
    
    print("✅ 网络功能测试完成")

def test_environment_info():
    """显示环境信息"""
    print("\n📋 环境信息:")
    print(f"   Python版本: {sys.version.split()[0]}")
    print(f"   Python路径: {sys.executable}")
    print(f"   工作目录: {os.getcwd()}")
    print(f"   虚拟环境: {'是' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '否'}")
    
    # 检查已安装的包
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        print(f"   已安装包数量: {len(installed_packages)}")
        print(f"   主要包: {', '.join(sorted(installed_packages)[:5])}...")
    except:
        print("   无法获取包信息")

def main():
    print("=" * 60)
    print("🚀 uv Python环境高级测试")
    print("=" * 60)
    
    test_environment_info()
    test_basic_functionality()
    test_network_functionality()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成!")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()