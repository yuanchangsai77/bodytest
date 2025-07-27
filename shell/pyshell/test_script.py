#!/usr/bin/env python3
"""
测试脚本 - 验证uv Python环境是否正常工作
"""

import sys
import os
from datetime import datetime

def main():
    print("=" * 50)
    print("Python环境测试脚本")
    print("=" * 50)
    
    # 显示Python版本信息
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件路径: {sys.executable}")
    print(f"Python路径: {sys.path[0]}")
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 显示环境变量
    print(f"PATH环境变量: {os.environ.get('PATH', 'Not found')}")
    
    # 测试基本功能
    print(f"当前时间: {datetime.now()}")
    
    # 测试简单计算
    result = sum(range(1, 101))
    print(f"1到100的和: {result}")
    
    # 测试导入标准库
    try:
        import json
        import requests
        print("✅ 标准库导入成功")
        print("✅ requests库可用")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    
    print("=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    main()