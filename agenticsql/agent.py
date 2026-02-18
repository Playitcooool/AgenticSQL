"""Core orchestration for NL-to-SQL workflow."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .config import Settings
from .db import dataframe_preview, load_schema, run_query
from .llm import LLMClient
from .visualization import save_auto_chart, should_visualize


@dataclass(frozen=True)
class AgentResponse:
    question: str
    sql: str
    preview: str
    row_count: int
    summary: str
    visualization_path: str | None = None


class AgenticSQL:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.llm = LLMClient(self.settings)

    def ask(self, db_path: str, question: str) -> AgentResponse:
        schema = load_schema(db_path)
        sql = self._generate_sql(question, schema.render_for_prompt())
        result = run_query(db_path, sql, self.settings.max_rows)
        preview = dataframe_preview(result.dataframe)
        summary = self._summarize(question, sql, preview)

        visualization_path = None
        if should_visualize(question, result.dataframe):
            chart_path = save_auto_chart(result.dataframe, self.settings.output_dir)
            if chart_path is not None:
                visualization_path = str(chart_path)

        return AgentResponse(
            question=question,
            sql=sql,
            preview=preview,
            row_count=result.rows,
            summary=summary,
            visualization_path=visualization_path,
        )

    def _generate_sql(self, question: str, schema_text: str) -> str:
        prompt = f"""
You are an expert SQLite analyst.
Return exactly one read-only SQL query for the user question.

Rules:
- Output SQL only, no markdown, no explanation.
- Allowed statements: SELECT / WITH / PRAGMA.
- Use only tables and columns from schema.
- Prefer explicit columns over SELECT * when practical.

Schema:
{schema_text}

Question:
{question}
""".strip()
        response = self.llm.invoke_text(prompt)
        return self._extract_sql(response)

    def _summarize(self, question: str, sql: str, preview: str) -> str:
        prompt = f"""
你是数据分析助手。请用简洁中文总结查询结果。

用户问题:
{question}

执行SQL:
{sql}

结果预览:
{preview}

要求:
- 2-4句
- 不要编造未出现的数据
- 如结果为空，明确说明
""".strip()
        return self.llm.invoke_text(prompt)

    @staticmethod
    def _extract_sql(content: str) -> str:
        stripped = content.strip()
        fenced_match = re.search(r"```(?:sql)?\s*(.*?)```", stripped, flags=re.IGNORECASE | re.DOTALL)
        if fenced_match:
            stripped = fenced_match.group(1).strip()
        return stripped.rstrip(";")
