"""
Avoor - LangChain Time Management AI
(c) 2024-2025 githubcatw & Claude
"""
from datetime import datetime
from typing import Literal
from uuid import uuid4
from langgraph.prebuilt import ToolNode
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langchain_google_genai import ChatGoogleGenerativeAI
from ics import Calendar, Event as ICSEvent
from pytz import timezone as pytz_timezone

from .tools import *
from .types import *

# Initialize the LLM (using Google Gemini via langchain)
from ..env_vars import GEMINI_API_KEY
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# For now, we'll use simple print statements for display
# In a web context, these could be replaced with websocket emissions
def display(content):
    """Display content to the user."""
    if hasattr(content, 'data'):
        # It's a markdown object or similar
        print(content.data)
    else:
        print(content)

class Markdown:
    """Simple markdown wrapper for display."""
    def __init__(self, content):
        self.data = content

def plan_to_ics_calendar(plan: dict, title: str, timezone_offset: float):
    """
    Converts a plan to an ICS calendar file and saves it.

    Args:
        plan: Dictionary of time blocks
        title: Title for the calendar
        timezone_offset: Timezone offset from UTC in hours
    """
    cal = Calendar()

    for block_id, block in plan.items():
        event = ICSEvent()
        event.name = block['purpose']

        # Create datetime objects for the event
        from_date = block['from_date']
        from_time = block['from_time']
        to_date = block['to_date']
        to_time = block['to_time']

        # Construct datetime (year, month, day, hour, minute)
        start_dt = datetime(from_date[2], from_date[1], from_date[0], from_time[0], from_time[1])
        end_dt = datetime(to_date[2], to_date[1], to_date[0], to_time[0], to_time[1])

        event.begin = start_dt
        event.end = end_dt

        cal.events.add(event)

    # Save the calendar to a file
    filename = f"{title.replace(' ', '_')}.ics"
    with open(filename, 'w') as f:
        f.writelines(cal.serialize_iter())

    print(f"Calendar saved as: {filename}")
    return filename

# Note: GenAITool for Google Search grounding
# This is a placeholder - implement if needed
class GenAITool:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "you're a time management expert AI within the app Avoor. you write schedules according to the constraints of a user. "
    "don't forget to plan breaks and mind deadlines, if any are specified. if in doubt about something, "
    "ask for clarification before starting to plan. you can only plan one day. ask for anything the "
    "user wants to accomplish and any constraints (e.g. time at university or sleep). it's preferable not "
    "to add any extra tasks and not to plan time considered a constraint (e.g. don't plan what the user "
    "does at university). suggest time first instead of asking the user how long they want to do anything. "
    "ask the user one or two questions at a time. keep in mind that the user might want to rename the tasks - "
    "use your text generation abilities."
    "\n\n"
    "to search the user's calendar for events, call find_events, passing in a search query. do this before asking the user."
    "add items to the user's plan with add_to_plan, and reset the plan with clear_plan. "
    "add_to_plan automatically asks the user to add the item, so there is no need for asking the user. "
    "to see the contents of the time plan so far, call get_plan() (this is shown to you, not the user). "
    "if you want to show the contents of the plan to the user, always call show_plan(). "
    "to remove something from the plan, call remove_from_plan with the uuid of the block that you want to remove."
    "once the user has finished, call add_to_calendar to show the user "
    "your plan as an ICS file, passing in a title and the user's timezone based on the city."
    "\n\n"
    # few-shot prompting improves the quality and seems to prevent it from essentially offloading the task
    # of planning the day to the user through excessive questions
    "good examples include:\n\n"
    "user: i'm at university from 11:00-18:00 and need to study probability theory and mathematical analysis in the meantime\n"
    "tool calls: add university to plan\n"
    "model: Alright, I've added university, do you like studying before classes?\n"
    "user: not really\n"
    "tool calls: none\n"
    "model: OK, should we start with probability theory once you're back, at 18:00 to 19:30?\n"
    "user: alright\n"
    "tool calls: add probability theory to plan\n(continued)"
    "\n\n"
    "user: help me plan a day of content creation around the new drop that i will receive today\n"
    "tool calls: search 'new drop' in events, tool returns an event at 15:30\n"
    "model: Alright, I see that there is a drop at 15:30. Do you want to prepare for it before receiving it?\n"
    "user: yeah, leave some time for makeup and to set up instagram live\n"
    "tool calls: none\n"
    "model: Would 30 minutes before be enough?\n(continued)"
)

def human_node(state: PlanState) -> PlanState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    display(Markdown(last_msg.content))

    user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


def chatbot_with_tools(state: PlanState) -> dict[str, object] | PlanState:
    """The chatbot with tools. A simple wrapper around the model's own chat interface."""
    defaults = {"plan": {}, "finished": False}

    if state["messages"]:
        new_output = llm_with_tools.invoke([SYSINT] + state["messages"])

    # Set up some defaults if not already set, then pass through the provided state,
    # overriding only the "messages" field.
    return defaults | state | {"messages": [new_output]}

def plan_manager_node(state: PlanState) -> PlanState:
    """The plan manager node. This is where the plan state is manipulated."""
    tool_msg = state.get("messages", [])[-1]
    plan = state.get("plan", [])
    outbound_msgs = []

    ##print("planmgr called!")
    #print("state:", state)
    ####print("")
    #print("tool_msg", tool_msg)

    finished = False

    for tool_call in tool_msg.tool_calls:

        if tool_call["name"] == "add_to_plan":
            fromTime = (int(tool_call["args"]["from_hour"]), int(tool_call["args"]["from_minute"]))
            toTime = (int(tool_call["args"]["to_hour"]), int(tool_call["args"]["to_minute"]))
            purpose = tool_call["args"]["purpose"]
            #datesF = (int(tool_call["args"]["from_year"]), int(tool_call["args"]["from_month"]), int(tool_call["args"]["from_day"]))
            #datesT = (int(tool_call["args"]["to_year"]), int(tool_call["args"]["to_month"]), int(tool_call["args"]["to_day"]))
            #print("[PlMgr] add block:", tool_call["args"])

            display(Markdown(f"> _Added block: {purpose}_"))

            now = datetime.now()
            dates = (now.day, now.month, now.year)
            plan[str(uuid4())] = TimeBlock.build(dates, dates, fromTime, toTime, purpose)
            response = format_plan(plan, True)

        elif tool_call["name"] == "get_plan":
            #print("[PlMgr] getting plan")
            #print("[PlMgr] plan is", plan)
            response = format_plan(plan, True) if plan else "(none)"
            
        elif tool_call["name"] == "show_plan":
            display(Markdown(format_plan(plan) if plan else "(none)"))

        elif tool_call["name"] == "clear_plan":
            #print("[PlMgr] clearing plan")
            plan.clear()
            response = None

        elif tool_call["name"] == "remove_from_plan":
            #print("[PlMgr] starting remove func")
            uuid = tool_call["args"]["uuid"]
            #print("[PlMgr]", uuid)
            if not uuid in plan:
                #print("[PlMgr] unknown")
                raise ValueError("unknown UUID")
            #print("[PlMgr] deleting " + uuid)
            display(Markdown(f"> _Removed block: {plan[uuid]['purpose']}_"))
            del plan[uuid]
            response = None

        elif tool_call["name"] == "add_to_calendar":
            plan_to_ics_calendar(plan, tool_call["args"]["title"], float(tool_call["args"]["offset"]))
            display(Markdown(tool_call["args"]["post_creation_message"]))
            finished = True
            response = None

        else:
            raise NotImplementedError(f'Unknown tool call: {tool_call["name"]}')

        # Record the tool results as tool messages.
        outbound_msgs.append(
            ToolMessage(
                content=response,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": outbound_msgs, "plan": plan, "finished": finished}

def maybe_route_to_tools(state: PlanState) -> str:
    """Route between chat and tool nodes if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    msg = msgs[-1]

    if state.get("finished", False):
        # When a plan is created, exit the app. The system instruction indicates
        # that the chatbot should say thanks and goodbye at this point, so we can exit
        # cleanly.
        return END

    elif hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Route to `tools` node for any automated tool calls first.
        if any(
            tool["name"] in tool_node.tools_by_name.keys() for tool in msg.tool_calls
        ):
            return "tools"
        else:
            return "planmgr"

    else:
        return "human"

def maybe_exit_human_node(state: PlanState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"


# Auto-tools will be invoked automatically by the ToolNode.
auto_tools = [get_plan, show_plan]
tool_node = ToolNode(auto_tools)

# Plan manipulation tools will be handled by the plan manager node.
plan_tools = [add_to_plan, get_plan, clear_plan, add_to_calendar, remove_from_plan]

# The LLM needs to know about all of the tools, so specify everything here.
# The last one adds Google Search grounding.
llm_with_tools = llm.bind_tools(auto_tools + plan_tools + [GenAITool(google_search={})])

graph_builder = StateGraph(PlanState)

# Nodes
graph_builder.add_node("chatbot", chatbot_with_tools)
graph_builder.add_node("human", human_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("planmgr", plan_manager_node)

# Chatbot -> {plan manager, tools, human, END}
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
# Human -> {chatbot, END}
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

# Tools (both kinds) always route back to chat afterwards.
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("planmgr", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()