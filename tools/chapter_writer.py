# -*- coding: utf-8 -*-
"""
章节写入/查询工具
将最终审核通过的章节内容持久化存入数据库
"""
from typing import Dict, Any
from langchain_core.tools import tool

from models.database import SessionLocal
from models.chapter import Chapter


@tool(description= "将章节内容持久化存入数据库，返回写入成功/失败状态")
def chapter_write(outline_id: int, chapter_number: int, content: str, status: str = "finished") -> Dict[str, Any]:
    """
    Args:
        outline_id: 关联大纲ID
        chapter_number: 章节序号
        content: 章节内容文本
        status: 状态

    Returns:
        Dict: 写入结果
    """
    db = SessionLocal()
    try:
        # 检查是否已存在该章节
        existing = db.query(Chapter).filter(
            Chapter.outline_id == outline_id,
            Chapter.chapter_number == chapter_number
        ).first()

        if existing:
            # 更新现有章节
            existing.content = content
            existing.status = status
            db.commit()
            db.refresh(existing)
            return {
                "success": True,
                "message": f"章节 {chapter_number} 已更新",
                "chapter_id": existing.id
            }
        else:
            # 创建新章节
            chapter = Chapter(
                outline_id=outline_id,
                chapter_number=chapter_number,
                content=content,
                status=status
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)
            return {
                "success": True,
                "message": f"章节 {chapter_number} 已创建",
                "chapter_id": chapter.id
            }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"写入失败: {str(e)}",
            "chapter_id": None
        }
    finally:
        db.close()

@tool(description="获取指定章节内容")
def get_chapter(outline_id: int, chapter_number: int) -> Dict[str, Any] | None:
    """
    Args:
        outline_id: 大纲ID
        chapter_number: 章节序号

    Returns:
        Dict: 章节数据或None
    """
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).filter(
            Chapter.outline_id == outline_id,
            Chapter.chapter_number == chapter_number
        ).first()

        if chapter:
            return chapter.to_dict()
        return None
    finally:
        db.close()

def get_chapters_by_outline(outline_id: int) -> list:
    """
    获取大纲下的所有章节

    Args:
        outline_id: 大纲ID

    Returns:
        list: 章节列表
    """
    db = SessionLocal()
    try:
        chapters = db.query(Chapter).filter(
            Chapter.outline_id == outline_id
        ).order_by(Chapter.chapter_number).all()

        return [c.to_dict() for c in chapters]
    finally:
        db.close()