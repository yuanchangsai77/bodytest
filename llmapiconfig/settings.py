"""
大模型API配置文件
支持多种主流大模型API服务
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 尝试加载dotenv,如果没有安装则忽略
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class LLMConfig:
    """大模型配置类"""
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30


class Settings:
    """配置管理类"""
    
    def __init__(self):
        self.load_from_env()
    
    def load_from_env(self):
        """从环境变量加载配置"""
        # OpenAI配置
        self.openai = LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
        
        # Claude配置
        self.claude = LLMConfig(
            api_key=os.getenv("CLAUDE_API_KEY", ""),
            base_url=os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com"),
            model=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.7"))
        )
        
        # 通义千问配置
        self.qwen = LLMConfig(
            api_key=os.getenv("QWEN_API_KEY", ""),
            base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
            model=os.getenv("QWEN_MODEL", "qwen-turbo"),
            max_tokens=int(os.getenv("QWEN_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("QWEN_TEMPERATURE", "0.7"))
        )
        
        # 智谱AI配置
        self.zhipu = LLMConfig(
            api_key=os.getenv("ZHIPU_API_KEY", ""),
            base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            model=os.getenv("ZHIPU_MODEL", "glm-4"),
            max_tokens=int(os.getenv("ZHIPU_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("ZHIPU_TEMPERATURE", "0.7"))
        )
        
        # Gemini配置
        self.gemini = LLMConfig(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        )
        
        # 默认使用的模型
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    
    def get_config(self, provider: str = None) -> LLMConfig:
        """获取指定提供商的配置"""
        provider = provider or self.default_provider
        
        config_map = {
            "openai": self.openai,
            "claude": self.claude,
            "qwen": self.qwen,
            "zhipu": self.zhipu,
            "gemini": self.gemini
        }
        
        if provider not in config_map:
            raise ValueError(f"不支持的提供商: {provider}")
        
        config = config_map[provider]
        if not config.api_key:
            raise ValueError(f"未设置 {provider} 的API密钥")
        
        return config
    
    def validate_config(self, provider: str = None) -> bool:
        """验证配置是否有效"""
        try:
            self.get_config(provider)
            return True
        except ValueError:
            return False


# 全局配置实例
settings = Settings()