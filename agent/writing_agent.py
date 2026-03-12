# -*- coding: utf-8 -*-
"""
写作 Agent
核心智能体，负责协调各工具完成章节写作任务
"""
import json
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig


from llm.llm_config import get_llm
from models.database import SessionLocal
from models.outline import Outline
from tools.plot_planner import gen_plot
from prompts import writer_prompt
from tools.chapter_writer import chapter_write,get_chapter

class WritingAgent:
    """写作 Agent 类"""

    def __init__(self, outline_id: int):
        """
        初始化写作 Agent

        Args:
            outline_id: 大纲ID
        """
        self.outline_id = outline_id
        self.llm = get_llm(temperature=0.7, max_tokens=4096)

        # 加载大纲
        self.outline = self._load_outline()
        self.global_settings = self.outline.get_global_settings()
        self.chapters = self.outline.get_chapters()

        # 初始化工具
        self.plot_planner = gen_plot
        self.chapter_writer = chapter_write
        self.chapter_get = get_chapter

        # 构建 Agent
        self.tools = [
            self.chapter_get,
            self.plot_planner,
            self.chapter_writer
        ]

    def _load_outline(self) -> Outline:
        """加载大纲数据"""
        db = SessionLocal()
        try:
            outline = db.query(Outline).filter(Outline.id == self.outline_id).first()
            if not outline:
                raise ValueError(f"找不到大纲 ID: {self.outline_id}")
            return outline
        finally:
            db.close()

    def my_create_agent(self) :
        """创建 Agent"""
        checkpointer = InMemorySaver()
        agent = create_agent(
            model = self.llm,
            tools = self.tools,
            checkpointer = checkpointer,
            system_prompt = writer_prompt.xuanhuan_prompt
        )
        return agent


    def run(self):
        """
        执行章节写作循环
        """
        writer = self.my_create_agent()
        nums = len(self.chapters)

        print(f"\n{'#'*20}")
        print(f"# 开始写作: 《{self.outline.title}》")
        print(f"# 共{nums}章")
        print(f"{'#'*20}\n")

        config = RunnableConfig(configurable={"thread_id":"1"})
        json_str = json.dumps(self.outline.to_dict(),ensure_ascii=False, indent=2)
        user_prompt = ChatPromptTemplate.from_messages([("human","创作大纲为：{outline}")])
        message = user_prompt.invoke({"outline": json_str})
        responses = writer.invoke(
            message,
            config = config
        )
        messages = responses["messages"]
        print(f"\n{'#'*70}")
        print(f"# 写作任务完成！")
        print(messages[-1].content)
        print(f"{'#'*70}\n")
