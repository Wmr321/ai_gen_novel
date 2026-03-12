# -*- coding: utf-8 -*-
"""
章节情节数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.database import Base

class ChapterPlot(Base):
    """章节情节表"""
    __tablename__ = "chapter_plots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    outline_id = Column(Integer, ForeignKey("outlines.id"), nullable=False, comment="关联大纲ID")
    chapter_number = Column(Integer, nullable=False, comment="章节序号")
    plots = Column(Text, nullable=True, comment="情节(JSON格式)")
    status = Column(String(20), default="finished", comment="状态: draft/finished")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    outline = relationship("Outline", backref="chapter_plot_list")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "outline_id": self.outline_id,
            "chapter_id": self.chapter_number,
            "content": self.plots,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }