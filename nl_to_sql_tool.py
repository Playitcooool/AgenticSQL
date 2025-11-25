"""
Natural Language to SQL conversion tool
"""
from langchain_core.tools import tool
from  langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


@tool
def nl_to_sql(question: str, db_schema: str, db_path: str) -> str:
    """
    Convert natural language question to SQL query.

    Args:
        question: The natural language question to convert
        db_schema: The database schema information
        db_path: Path to the database (included for context)

    Returns:
        Generated SQL query as a string
    """
    try:
        # Initialize Ollama model
        llm = ChatOllama(model="qwen3:1.7b", temperature=0,base_url='http://localhost:11434')

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL expert. Convert the user's natural language question into a valid SQL query.

Database Schema:
{schema}

Rules:
1. Generate ONLY the SQL query, no explanations
2. Use proper SQL syntax for SQLite
3. Return only SELECT statements
4. Do not include markdown code blocks or formatting
5. Ensure the query is safe and read-only

Example:
Question: "Show me all customers"
SQL: SELECT * FROM customers

Question: "How many orders were placed last month?"
SQL: SELECT COUNT(*) FROM orders WHERE created_at >= date('now', '-1 month')
"""),
            ("human", "{question}")
        ])

        # Create chain
        chain = prompt | llm

        # Generate SQL
        response = chain.invoke({
            "schema": db_schema,
            "question": question
        })

        # Extract SQL from response
        sql_query = response.content.strip()

        # Clean up response (remove markdown if present)
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].split("```")[0].strip()

        return sql_query

    except Exception as e:
        return f"Error converting NL to SQL: {str(e)}"
