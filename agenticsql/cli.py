"""Command line interface for AgenticSQL."""
from __future__ import annotations

import argparse
import sys

from .agent import AgenticSQL
from .errors import AgenticSQLError
from .sample_db import create_example_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AgenticSQL - productionized NL2SQL assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="Ask one natural-language question")
    ask.add_argument("question", type=str, help="Natural language question")
    ask.add_argument("--db", type=str, default="example.db", help="Path to SQLite database")

    chat = sub.add_parser("chat", help="Interactive chat mode")
    chat.add_argument("--db", type=str, default="example.db", help="Path to SQLite database")

    init_db = sub.add_parser("init-db", help="Create local example database")
    init_db.add_argument("--db", type=str, default="example.db", help="Output SQLite path")

    return parser


def run_once(db_path: str, question: str) -> int:
    agent = AgenticSQL()
    try:
        response = agent.ask(db_path, question)
    except AgenticSQLError as exc:
        print(f"[AgenticSQL Error] {exc}")
        return 2
    except FileNotFoundError:
        print(f"Database not found: {db_path}")
        print("Run `python -m agenticsql init-db --db example.db` to create a local sample database.")
        return 2

    print("\n=== SQL ===")
    print(response.sql)
    print("\n=== Rows ===")
    print(response.row_count)
    print("\n=== Preview ===")
    print(response.preview)
    print("\n=== Summary ===")
    print(response.summary)
    if response.visualization_path:
        print("\n=== Visualization ===")
        print(response.visualization_path)
    return 0


def run_chat(db_path: str) -> int:
    print("AgenticSQL interactive mode. type `exit` to quit.\n")
    while True:
        try:
            question = input("You> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("bye")
            return 0

        code = run_once(db_path=db_path, question=question)
        if code != 0:
            return code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        path = create_example_database(args.db)
        print(f"Example database created at: {path}")
        return 0
    if args.command == "ask":
        return run_once(db_path=args.db, question=args.question)
    if args.command == "chat":
        return run_chat(db_path=args.db)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
