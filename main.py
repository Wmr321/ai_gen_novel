# -*- coding: utf-8 -*-
"""
小说生成系统主入口
玄幻网文自动化写作辅助系统

使用流程：
1. 用户输入主题
2. 生成大纲 (Outline)
3. 存入数据库
4. 启动写作Agent，逐章生成内容
"""
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from models.database import init_db, SessionLocal
from models.outline import Outline
from tools.outline_generator import OutlineGenerator, save_to_db
from agent.writing_agent import WritingAgent


def display_banner():
    """显示系统横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              📚 玄幻小说生成系统 📚                             ║
    ║                                                               ║
    ║           基于 LangChain + Qwen 的AI写作助手                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def create_outline_interactive():
    """交互式创建大纲"""
    print("\n【步骤1】创建小说大纲")
    print("-" * 50)

    # 获取用户输入
    theme = input("请输入小说主题（如'九霄灵脉'）：").strip()

    if not theme:
        print("错误：主题不能为空")
        return None

    print(f"\n正在为主题 '{theme}' 生成大纲，请稍候...\n")

    # 生成大纲
    generator = OutlineGenerator()
    try:
        outline_data = generator.xuanhuan_generate(theme)
        print(f"✓ 大纲生成成功！")
        print(f"  标题: {outline_data.get('小说标题', '未命名')}")
        print(f"  预估字数: {outline_data.get('预估总字数', 0)}")
        print(f"  章节数: {len(outline_data.get('章节计划', []))}")
        return outline_data
    except Exception as e:
        print(f"✗ 大纲生成失败: {e}")
        return None


def save_outline_to_db(outline_data: dict) -> int | None:
    """将大纲保存到数据库"""
    print("\n【步骤3】保存大纲到数据库")
    print("-" * 50)

    db = SessionLocal()
    try:
        outline_id = save_to_db(outline_data, db)
        print(f"✓ 大纲已保存，ID: {outline_id}")
        return outline_id
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def start_writing_agent(outline_id: int):
    """启动写作Agent"""
    print("\n【步骤4】启动写作Agent")
    print("-" * 50)

    try: # 创建并运行写作Agent
        agent = WritingAgent(outline_id)
        agent.run()
    except Exception as e:
        print(f"写作Agent运行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    display_banner()

    # 初始化数据库
    print("正在初始化数据库...")
    init_db()
    print("✓ 数据库初始化完成\n")

    # 主菜单
    while True:
        print("\n【主菜单】")
        print("-" * 50)
        print("1. 创建新小说（生成大纲并写作）")
        print("2. 基于现有大纲继续写作")
        print("3. 查看已创建的小说大纲")
        print("4. 导出小说为文本文件")
        print("0. 退出系统")
        print("-" * 50)

        choice = input("请选择操作（0-4）：").strip()

        if choice == "1":
            # 创建新小说流程
            outline_data = create_outline_interactive()
            if not outline_data:
                continue
            outline_id = save_outline_to_db(outline_data)

            if outline_id:
                # 询问是否立即开始写作
                if input("\n是否立即开始写作？(y/n)：").lower() == 'y':
                    start_writing_agent(outline_id)

        elif choice == "2":
            # 基于现有大纲写作
            db = SessionLocal()
            try:
                outlines = db.query(Outline).all()
                if not outlines:
                    print("\n暂无已创建的大纲，请先创建新小说。")
                    continue

                print("\n已创建的大纲列表：")
                for o in outlines:
                    print(f"  ID: {o.id} | {o.title} | 状态: {o.status}")

                try:
                    outline_id = int(input("\n请输入要写作的大纲ID："))
                    start_writing_agent(outline_id)
                except ValueError:
                    print("请输入有效的数字ID")
            finally:
                db.close()

        elif choice == "3":
            # 查看大纲
            db = SessionLocal()
            try:
                outlines = db.query(Outline).all()
                if not outlines:
                    print("\n暂无已创建的大纲")
                    continue

                print("\n已创建的大纲列表：")
                for o in outlines:
                    chapters_count = len(o.get_chapters())
                    print(f"\n  ID: {o.id}")
                    print(f"  标题: {o.title}")
                    print(f"  字数: {o.word_count}")
                    print(f"  章节数: {chapters_count}")
                    print(f"  状态: {o.status}")
                    print(f"  创建时间: {o.created_at}")
                    print("-" * 40)
            finally:
                db.close()

        elif choice == "4":
            # 导出小说
            db = SessionLocal()
            try:
                outlines = db.query(Outline).all()
                if not outlines:
                    print("\n暂无已创建的大纲")
                    continue

                print("\n可导出的小说：")
                for o in outlines:
                    print(f"  ID: {o.id} | {o.title}")

                try:
                    outline_id = int(input("\n请输入要导出的大纲ID：").strip())
                    outline = db.query(Outline).filter(Outline.id == outline_id).first()

                    if not outline:
                        print("大纲不存在")
                        continue

                    # 获取所有章节
                    from tools.chapter_writer import get_chapters_by_outline
                    chapters = get_chapters_by_outline(outline_id)

                    if not chapters:
                        print("该大纲暂无章节内容")
                        continue

                    # 生成文件名
                    filename = f"{outline.title}_导出.txt"
                    filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"《{outline.title}》\n")
                        f.write(f"总字数预估: {outline.word_count}\n")
                        f.write("=" * 60 + "\n\n")

                        for ch in chapters:
                            if ch.get('content'):
                                f.write(ch['content'])
                                f.write("\n\n")

                    print(f"\n✓ 小说已导出到: {filename}")

                except ValueError:
                    print("请输入有效的数字ID")
            finally:
                db.close()

        elif choice == "0":
            print("\n感谢使用，再见！")
            break

        else:
            print("无效的选择，请重新输入")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作，系统退出。")
        sys.exit(0)
