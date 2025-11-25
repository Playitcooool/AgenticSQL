"""
AgenticSQL - Main entry point
An intelligent SQL agent that converts natural language to SQL queries and visualizes results.
"""
import os
import argparse
from agent import run_agent


def main():
    """Main function to run the AgenticSQL agent."""
    parser = argparse.ArgumentParser(
        description="AgenticSQL - Natural Language to SQL Agent"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="example.db",
        help="Path to SQLite database file (default: example.db)"
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Question to ask about the database"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Check if database exists
    if not os.path.exists(args.db):
        print(f"⚠️  Database file '{args.db}' not found.")
        print("Creating example database for demonstration...")
        from create_example_db import create_example_database
        create_example_database(args.db)
        print(f"✅ Example database created at '{args.db}'\n")

    # Interactive mode
    if args.interactive:
        print("\n🤖 AgenticSQL - Interactive Mode")
        print("=" * 60)
        print("Ask questions about your database in natural language.")
        print("Type 'quit' or 'exit' to stop.\n")

        while True:
            try:
                question = input("You: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋\n")
                    break

                if not question:
                    continue

                run_agent(args.db, question)

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

    # Single question mode
    elif args.question:
        run_agent(args.db, args.question)

    # Default: show example questions
    else:
        print("\n🤖 AgenticSQL - Natural Language to SQL Agent")
        print("=" * 60)
        print(f"\nUsing database: {args.db}\n")

        example_questions = [
            "What tables are in the database?",
            "Show me all customers",
            "How many orders do we have?",
        ]

        print("Example questions:")
        for i, q in enumerate(example_questions, 1):
            print(f"  {i}. {q}")

        print("\nUsage:")
        print(f"  python main.py --question 'Your question here'")
        print(f"  python main.py --interactive")
        print(f"  python main.py --db path/to/your.db --interactive\n")


if __name__ == "__main__":
    main()
