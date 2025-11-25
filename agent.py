"""
AgenticSQL - LangGraph agent with planning capability
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from database_tools import list_tables, execute_sql
from nl_to_sql_tool import nl_to_sql
from visualization_tool import visualize_data


# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    db_path: str
    plan: str
    current_step: int
    total_steps: int
    final_answer: str


# Initialize the model
llm = ChatOllama(model="qwen3:1.7b", temperature=0, base_url='http://localhost:11434')


def create_agent(db_path: str):
    """Create the AgenticSQL agent with planning capability."""

    # Bind tools to the model
    tools = [list_tables, execute_sql, nl_to_sql, visualize_data]
    llm_with_tools = llm.bind_tools(tools)

    # Planning node
    def planning_node(state: AgentState):
        """Create a plan based on user's question."""
        messages = state["messages"]
        user_question = messages[0].content  # Get original question

        planning_prompt = f"""You are a SQL assistant. Analyze the user's question and create a step-by-step plan.

User Question: {user_question}

Create a clear, numbered plan with 2-5 steps. Common steps include:
1. List database tables to understand schema
2. Convert natural language to SQL
3. Execute the SQL query
4. Visualize the results (if appropriate)

Respond with ONLY the numbered plan, nothing else.

Plan:"""

        response = llm.invoke([HumanMessage(content=planning_prompt)])

        plan = response.content
        steps = [s.strip() for s in plan.split('\n') if s.strip() and s.strip()[0].isdigit()]

        return {
            "messages": [
                AIMessage(content=f"Plan created:\n{plan}"),
                HumanMessage(content=f"Now execute this plan to answer: {user_question}")
            ],
            "plan": plan,
            "current_step": 0,
            "total_steps": len(steps)
        }

    # Agent node - executes the plan
    def agent_node(state: AgentState):
        """Execute actions based on the plan."""
        messages = state["messages"]
        user_question = messages[0].content  # Original user question

        # Add system message with context
        system_msg = SystemMessage(content=f"""You are a helpful SQL assistant with access to tools.

Database path: {state['db_path']}

Original Question: {user_question}

Execution Plan:
{state.get('plan', 'No plan yet')}

Follow the plan step by step:
1. First, use list_tables tool to see database structure
2. Then use nl_to_sql tool to convert the question to SQL
3. Use execute_sql tool to run the query
4. If visualization would help, use visualize_data tool

Start executing now by calling the appropriate tool.""")

        messages_with_system = [system_msg] + list(messages[-3:])  # Keep recent context

        response = llm_with_tools.invoke(messages_with_system)

        return {"messages": [response]}

    # Decision node - determines next action
    def should_continue(state: AgentState):
        """Determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"

        # If we have tool results and query was executed, we can end
        # Check if execute_sql was called
        tool_names = []
        for msg in messages:
            if hasattr(msg, 'name') and msg.name:
                tool_names.append(msg.name)

        # If we've executed SQL or listed tables, and no more tool calls, end
        if 'execute_sql' in tool_names or len(messages) > 10:
            return "end"

        # Otherwise continue - agent needs to call more tools
        return "agent"

    # Tool execution node
    tool_node = ToolNode(tools)

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planning_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("planner")

    # Add edges
    workflow.add_edge("planner", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "agent": "agent",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")

    # Compile the graph
    app = workflow.compile()

    return app


def run_agent(db_path: str, question: str):
    """Run the agent with a user question."""
    agent = create_agent(db_path)

    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "db_path": db_path,
        "plan": "",
        "current_step": 0,
        "total_steps": 0,
        "final_answer": ""
    }

    # Stream the agent's execution
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    for output in agent.stream(initial_state):
        for key, value in output.items():
            if key == "planner":
                plan_msg = value["messages"][-1]
                print(f"\n📋 Planning:\n{plan_msg.content}\n")

            elif key == "agent":
                agent_msg = value["messages"][-1]
                if hasattr(agent_msg, 'tool_calls') and agent_msg.tool_calls:
                    print(f"\n🔧 Executing tools:")
                    for tool_call in agent_msg.tool_calls:
                        print(f"  - {tool_call['name']}")
                elif agent_msg.content:
                    print(f"\n💬 Agent: {agent_msg.content}")

            elif key == "tools":
                tool_msgs = value["messages"]
                for msg in tool_msgs:
                    print(f"\n📊 Tool Result:\n{msg.content[:500]}...")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Example usage
    DB_PATH = "example.db"

    # Example questions
    questions = [
        "Show me all the tables in the database",
        "How many customers do we have?",
        "What are the top 5 products by sales?",
    ]

    for q in questions:
        run_agent(DB_PATH, q)
        print("\n" + "="*80 + "\n")
