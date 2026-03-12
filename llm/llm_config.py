# -*- coding: utf-8 -*-
"""
LLM 配置模块
配置 Qwen 模型连接
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(temperature: float = None, max_tokens: int = None):
    """
    获取配置好的 LLM 实例

    Args:
        temperature: 温度参数，控制随机性
        max_tokens: 最大生成token数

    Returns:
        ChatOpenAI: 配置好的LLM实例
    """

    if temperature is None:
        temperature = float(os.getenv('TEMPERATURE', '0.7'))

    if max_tokens is None:
        max_tokens = int(os.getenv('MAX_TOKENS', '4096'))

    return ChatOpenAI(
        model='qwen-max',
        temperature=temperature,
        max_tokens=max_tokens
    )
