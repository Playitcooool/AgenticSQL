# AgenticSQL

一个智能SQL Agent,能够将自然语言转换为SQL查询并可视化结果。基于LangGraph和Ollama构建。

## 功能特性

- 🤖 **智能规划**: Agent在执行任务前会先制定计划
- 🗣️ **自然语言转SQL**: 使用本地Ollama模型将问题转换为SQL查询
- 🗄️ **数据库探索**: 自动查询数据库表结构和schema
- 📊 **数据可视化**: 自动生成图表(柱状图、折线图、饼图等)
- 🔄 **交互式模式**: 支持命令行交互式问答

## 系统架构

```
AgenticSQL/
├── main.py                    # 主入口
├── agent.py                   # LangGraph Agent实现
├── database_tools.py          # 数据库查询工具
├── nl_to_sql_tool.py         # 自然语言转SQL工具
├── visualization_tool.py      # 数据可视化工具
├── create_example_db.py      # 示例数据库生成器
└── requirements.txt          # 依赖包
```

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装并启动Ollama

访问 [Ollama官网](https://ollama.ai) 下载安装,然后拉取qwen2.5模型:

```bash
ollama pull qwen2.5:1.5b
```

### 3. 创建示例数据库

```bash
python create_example_db.py
```

## 使用方法

### 交互式模式

```bash
python main.py --interactive
```

### 单次问答模式

```bash
python main.py --question "有多少客户?"
```

### 使用自定义数据库

```bash
python main.py --db path/to/your.db --interactive
```

## 示例问题

- "数据库里有哪些表?"
- "显示所有客户"
- "我们有多少订单?"
- "销量前5的产品是什么?"
- "每个国家有多少客户?"
- "上个月的总销售额是多少?"

## Agent工作流程

1. **Planning阶段**: Agent分析用户问题,制定执行计划
2. **执行阶段**: 按计划顺序使用工具:
   - 使用`list_tables`查看数据库结构
   - 使用`nl_to_sql`将问题转换为SQL
   - 使用`execute_sql`执行查询
   - 使用`visualize_data`创建可视化(如需要)
3. **结果返回**: 返回查询结果和可视化图表

## 可用工具

- **list_tables**: 列出数据库所有表及其schema
- **execute_sql**: 执行SQL查询并返回结果
- **nl_to_sql**: 将自然语言问题转换为SQL语句
- **visualize_data**: 对查询结果创建可视化图表

## 技术栈

- **LangGraph**: 构建有状态的Agent工作流
- **LangChain**: 工具调用和LLM集成
- **Ollama**: 本地运行qwen2.5:1.5b模型
- **SQLite**: 数据库引擎
- **Matplotlib/Seaborn**: 数据可视化

## 配置说明

默认使用Ollama的`qwen2.5:1.5b`模型。如需更改模型,修改以下文件:

- `agent.py` 中的 `ChatOllama(model="qwen2.5:1.5b")`
- `nl_to_sql_tool.py` 中的 `ChatOllama(model="qwen2.5:1.5b")`

## 注意事项

1. 确保Ollama服务正在运行
2. 首次使用会自动创建示例数据库
3. 可视化图表保存在`visualizations/`目录
4. 模型使用temperature=0以提高SQL生成的准确性

## 故障排查

**问题**: 连接Ollama失败
- 检查Ollama是否正在运行: `ollama list`
- 确认模型已下载: `ollama pull qwen2.5:1.5b`

**问题**: SQL生成不准确
- 尝试更详细地描述问题
- 先询问"有哪些表"了解数据库结构

**问题**: 可视化失败
- 确保查询返回了适合可视化的数据
- 检查`visualizations/`目录是否可写

## License

MIT
