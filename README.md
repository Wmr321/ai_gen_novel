# 玄幻小说生成系统

基于 LangChain + Qwen 大语言模型的自动化小说创作辅助系统。

## 系统概述

本系统通过结构化流程实现从主题输入到完整章节生成的全流程支持：

```
用户输入主题 → 大纲生成 → 数据库存储 → Agent章节写作 → 完成
```

## 系统架构

### 核心模块

| 模块/工具              | 功能 |
|--------------------|------|
| `OutlineGenerator` | 根据主题生成结构化大纲 |
| `WritingAgent`     | 核心写作智能体，协调各工具完成章节创作 |
| `gen_plot`         | 规划章节情节点 |
| `chapter_write`    | 将章节写入数据库 |

### 数据库结构

- **大纲表(Outline)**: id, title, word_count, global_settings, chapters, status
- **章节表(Chapter)**: id, outline_id, chapter_number, content, status
- **情节表(chapter_plots)**:id, chapter_id, plots, status, created_at,updated_at

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
#uv
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的通义千问 API Key
```

## 配置说明

编辑 `.env` 文件：

```env
# Qwen API 配置 (阿里云通义千问)
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=your_qwen_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///novel_system.db

# 模型配置
MODEL_NAME=qwen-max
TEMPERATURE=0.7
MAX_TOKENS=4096
```

**获取 API Key:**
- 访问 [阿里云百炼](https://dashscope.aliyun.com/)
- 注册并创建 API Key

## 使用方法

### 启动系统

```bash
python main.py
```

### 操作流程

1. **创建新小说**
   - 选择菜单项 `1`
   - 输入小说主题（如"九霄灵脉"）
   - 系统自动生成大纲
   - 保存到数据库
   - 可选择立即开始写作

2. **继续写作**
   - 选择菜单项 `2`
   - 选择已有大纲ID
   - 指定要写的章节范围
   - Agent开始自动生成章节

3. **查看大纲**
   - 选择菜单项 `3`
   - 查看所有已创建的大纲列表

4. **导出小说**
   - 选择菜单项 `4`
   - 选择要导出的小说ID
   - 生成文本文件

## 目录结构

```
my_ai_gen_novel/
├── agent/              # Agent模块
│   ├── __init__.py
│   └── writing_agent.py
├──llm/                 #大模型
│   ├── __init__.py
│   └── llm_config.py
├── models/             # 数据库模型
│   ├── __init__.py
│   ├── database.py
│   ├── outline.py
│   ├── chapter_plot.py
│   └── chapter.py
├── prompts/            # 提示词模块
│   ├── __init__.py
│   ├── outline_prompt.py
│   ├── plot_prompt.py
│   └── writer_prompt.py
├── tools/              # 工具模块
│   ├── __init__.py
│   ├── outline_generator.py
│   ├── plot_planner.py
│   └── chapter_writer.py
├── main.py             # 主入口
├── requirements.txt    # 依赖清单
├── pyproject.toml      # 依赖清单
├── .env.example        # 环境变量模板
└── README.md           # 说明文档
```

## 技术栈

- **框架**: LangChain
- **LLM**: 通义千问 (Qwen)
- **数据库**: SQLite (可更换为其他SQL数据库)
- **语言**: Python 3.12+


## 注意事项

1. API Key 需要妥善保管，不要提交到代码仓库
2. 生成内容消耗API额度，请合理使用
3. 生成结果可能存在随机性，可多次尝试获取更好效果
4. 建议先生成1-2章测试效果，满意后再批量生成


