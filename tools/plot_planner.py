# -*- coding: utf-8 -*-
"""
情节规划器
将章节的"写作主题"与"写作目的"转化为具体情节点序列
"""
import json
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from llm.llm_config import get_llm
from models.database import SessionLocal
from models.chapter_plot import ChapterPlot
from prompts.plot_prompt import plot_prompt

class PlotPlan(BaseModel):
    情节规划 : list[Dict[str, Any]] = Field(description="本章节的情节点")

@tool(description = "将写作主题、写作目的、写作素材转化为具体情节点序列（3-5个关键事件）")
def gen_plot(chapter_id: int,theme: str, purpose: str, material: str) -> Dict[str, Any]:
    """
    生成情节规划
    Args:
        chapter_id: 章节id
        theme: 写作主题
        purpose: 写作目的
        material: 写作素材
    Returns:
        Dict: 结构化情节点
    """
    print("开始情节设计")
    prompt = ChatPromptTemplate.from_messages([
        ("system", plot_prompt),
        ("human", "写作主题：{theme}、写作目的：{purpose}、写作素材：{material}")
    ])
    my_llm = get_llm().with_structured_output(PlotPlan)
    chain = prompt | my_llm
    try:
        plot_plan = chain.invoke({"theme":theme, "purpose": purpose, "material": material})
        plot_write(plot_plan.__dict__, chapter_id)
        print("情节设计完成")
        return plot_plan.__dict__
    except Exception as e:
        print(e)
        return {"失败":e}

def plot_write(plot_plan: dict[str,Any],chapter_id: int) -> int:
    """
    将情节保存到数据库
    Args:
        plot_plan: 情节字典
        chapter_id: 章节id
    """
    db = SessionLocal()
    plot = ChapterPlot(
        chapter_id = chapter_id,
        plots = json.dumps(plot_plan.get("情节规划",[]),ensure_ascii=False)
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    print("情节存储成功")
    return chapter_id
