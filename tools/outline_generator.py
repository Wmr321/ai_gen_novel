# -*- coding: utf-8 -*-
"""
大纲生成器
根据用户输入的主题生成结构化大纲
"""
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from llm.llm_config import get_llm
from prompts.outline_prompt import xuanhuan_outline_prompt


class OutlineXuanhuan(BaseModel):
    """大纲输出结构"""
    小说标题: str = Field(description="小说标题")
    预估总字数: str = Field(description="预估总字数")
    全局设定: Dict[str, Any] = Field(description="全局设定")
    章节计划: list = Field(description="章节计划")


class OutlineGenerator:
    """大纲生成器类"""
    def __init__(self):
        self.llm = get_llm(temperature=0.8, max_tokens=4096)

    def xuanhuan_generate(self, theme: str) -> Dict[str, Any]:
        """
        根据主题生成大纲

        Args:
            theme: 小说主题，如"九霄灵脉"

        Returns:
            Dict: 结构化大纲数据
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", xuanhuan_outline_prompt),
            ("human", "请根据以下主题生成玄幻小说大纲：{theme}")
        ])
        my_llm = self.llm.with_structured_output(OutlineXuanhuan)
        chain = prompt | my_llm
        result = chain.invoke({"theme": theme})
        return result.__dict__

def save_to_db(outline_data: Dict[str, Any], db_session) -> int:
    """
    将大纲保存到数据库

    Args:
        outline_data: 大纲数据字典
        db_session: 数据库会话

    Returns:
        int: 大纲ID
    """
    from models import Outline

    outline = Outline(
        title=outline_data.get("小说标题", "未命名"),
        word_count=outline_data.get("预估总字数", 0),
        global_settings=json.dumps(outline_data.get("全局设定", {}), ensure_ascii=False),
        chapters=json.dumps(outline_data.get("章节计划", []), ensure_ascii=False),
        status="created"
    )

    db_session.add(outline)
    db_session.commit()
    db_session.refresh(outline)

    return outline.id

if __name__ == "__main__":
    generate = OutlineGenerator()
    result1 = generate.xuanhuan_generate(theme="九霄灵脉")
    print(1)
    print(result1.__dict__)