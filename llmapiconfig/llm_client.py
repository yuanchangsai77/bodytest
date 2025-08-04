"""
大模型客户端封装
提供统一的接口调用不同的大模型API
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
from .settings import settings, LLMConfig


class LLMClient:
    """大模型客户端基类"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.default_provider
        self.config = settings.get_config(self.provider)
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """聊天补全接口"""
        if self.provider == "openai":
            return await self._openai_chat(messages, stream, **kwargs)
        elif self.provider == "claude":
            return await self._claude_chat(messages, stream, **kwargs)
        elif self.provider == "qwen":
            return await self._qwen_chat(messages, stream, **kwargs)
        elif self.provider == "zhipu":
            return await self._zhipu_chat(messages, stream, **kwargs)
        elif self.provider == "gemini":
            return await self._gemini_chat(messages, stream, **kwargs)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
    
    async def _openai_chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """OpenAI API调用"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": stream
        }
        
        url = f"{self.config.base_url}/chat/completions"
        
        if stream:
            return await self._stream_request(url, headers, data)
        else:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def _claude_chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Claude API调用"""
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Claude API格式转换
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)
        
        data = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "messages": claude_messages,
            "stream": stream
        }
        
        if system_message:
            data["system"] = system_message
        
        url = f"{self.config.base_url}/v1/messages"
        
        if stream:
            return await self._stream_request(url, headers, data)
        else:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def _qwen_chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """通义千问API调用"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": stream
            }
        }
        
        url = f"{self.config.base_url}/chat/completions"
        
        if stream:
            return await self._stream_request(url, headers, data)
        else:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def _zhipu_chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """智谱AI API调用"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": stream
        }
        
        url = f"{self.config.base_url}/chat/completions"
        
        if stream:
            return await self._stream_request(url, headers, data)
        else:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def _gemini_chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Gemini API调用"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini API格式转换
        gemini_contents = []
        system_instruction = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant":
                gemini_contents.append({
                    "role": "model",
                    "parts": [{"text": msg["content"]}]
                })
        
        data = {
            "contents": gemini_contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
            }
        }
        
        if system_instruction:
            data["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        # 构建URL
        method = "streamGenerateContent" if stream else "generateContent"
        url = f"{self.config.base_url}/models/{self.config.model}:{method}?key={self.config.api_key}"
        
        if stream:
            return await self._gemini_stream_request(url, headers, data)
        else:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def _gemini_stream_request(self, url: str, headers: Dict, data: Dict) -> AsyncGenerator:
        """Gemini流式请求处理"""
        async with self.client.stream("POST", url, headers=headers, json=data) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        # Gemini流式响应格式处理
                        if line.startswith("data: "):
                            chunk_data = line[6:]
                        else:
                            chunk_data = line
                        yield json.loads(chunk_data)
                    except json.JSONDecodeError:
                        continue
        """流式请求处理"""
        async with self.client.stream("POST", url, headers=headers, json=data) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk_data = line[6:]
                    if chunk_data.strip() == "[DONE]":
                        break
                    try:
                        yield json.loads(chunk_data)
                    except json.JSONDecodeError:
                        continue


# 便捷函数
async def chat(
    messages: List[Dict[str, str]], 
    provider: str = None,
    stream: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """便捷的聊天函数"""
    async with LLMClient(provider) as client:
        return await client.chat_completion(messages, stream, **kwargs)


async def simple_chat(
    prompt: str, 
    provider: str = None,
    **kwargs
) -> str:
    """简单的聊天函数,返回文本内容"""
    messages = [{"role": "user", "content": prompt}]
    response = await chat(messages, provider, **kwargs)
    
    # 确定实际使用的提供商
    actual_provider = provider or settings.default_provider
    
    # 根据不同提供商解析响应
    if actual_provider in ["openai", "zhipu"]:
        return response["choices"][0]["message"]["content"]
    elif actual_provider == "claude":
        return response["content"][0]["text"]
    elif actual_provider == "qwen":
        return response["output"]["choices"][0]["message"]["content"]
    elif actual_provider == "gemini":
        return response["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise ValueError(f"不支持的提供商: {actual_provider}")