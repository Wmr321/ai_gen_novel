# -*- coding: utf-8 -*-
"""
大纲数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from models.database import Base
import json


class Outline(Base):
    """大纲表"""
    __tablename__ = "outlines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="小说标题")
    word_count = Column(Integer, default=0, comment="预估总字数")
    global_settings = Column(Text, nullable=False, comment="全局设定(JSON格式)")
    chapters = Column(Text, nullable=False, comment="章节大纲(JSON格式)")
    status = Column(String(20), default="created", comment="状态: created/writing/completed")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def get_global_settings(self):
        """获取全局设定对象"""
        return json.loads(self.global_settings)

    def get_chapters(self):
        """获取章节大纲列表"""
        return json.loads(self.chapters)

    def set_global_settings(self, data: dict):
        """设置全局设定"""
        self.global_settings = json.dumps(data, ensure_ascii=False)

    def set_chapters(self, data: list):
        """设置章节大纲"""
        self.chapters = json.dumps(data, ensure_ascii=False)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "word_count": self.word_count,
            "global_settings": self.get_global_settings(),
            "chapters": self.get_chapters(),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }