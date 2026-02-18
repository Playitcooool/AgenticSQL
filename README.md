# AgenticSQL

一个可工程化运行的 SQLite 自然语言查询助手。输入问题，系统会自动：
1. 读取数据库 schema
2. 生成只读 SQL
3. 执行查询并返回结果预览
4. 自动输出简要结论（可选生成图表）

## 为什么重构

旧版本存在这些问题：
- 文件命名混乱（带日期/空格），入口与 README 不一致
- 过度依赖多轮 tool calling，稳定性差
- 缺乏 SQL 安全边界（可写 SQL 风险）
- 没有标准包结构、CLI 子命令、测试基线

本版本已改为标准 Python 项目结构，具备可维护性和可扩展性。

## 项目结构

```text
agenticsql/
  __main__.py
  cli.py
  agent.py
  config.py
  db.py
  llm.py
  visualization.py
  sample_db.py
tests/
  test_sql_safety.py
  test_schema.py
pyproject.toml
requirements.txt
README.md
```

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如需可编辑安装：

```bash
pip install -e .
```

## 运行前准备

1. 启动 Ollama
2. 拉取模型（默认 `qwen3:1.7b`）

```bash
ollama pull qwen3:1.7b
```

## 用法

### 1) 初始化示例数据库

```bash
python -m agenticsql init-db --db example.db
```

### 2) 单次提问

```bash
python -m agenticsql ask "销量前5的产品是什么" --db example.db
```

### 3) 交互模式

```bash
python -m agenticsql chat --db example.db
```

## 环境变量

- `AGENTICSQL_MODEL`：模型名，默认 `qwen3:1.7b`
- `AGENTICSQL_OLLAMA_BASE_URL`：默认 `http://localhost:11434`
- `AGENTICSQL_TEMPERATURE`：默认 `0`
- `AGENTICSQL_MAX_ROWS`：查询结果最大保留行数，默认 `200`
- `AGENTICSQL_OUTPUT_DIR`：图表输出目录，默认 `outputs`

## 安全策略

`agenticsql.db.validate_read_only_sql` 默认仅允许：
- `SELECT`
- `WITH`
- `PRAGMA`

并阻止：
- `INSERT / UPDATE / DELETE / DROP / ALTER / CREATE / ATTACH / DETACH`
- 多语句执行

## 测试

```bash
pytest -q
```

## 后续扩展建议

- 接入 PostgreSQL/MySQL 抽象层
- 加入 SQL 语义校验与自动重试
- 结果缓存与会话记忆
- API 服务化（FastAPI）
