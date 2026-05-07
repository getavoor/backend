from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

class TimeBlock(TypedDict):
    """A block in a user's time plan."""

    # The date to start from. Tuple in the format (day, month, year).
    from_date = tuple[int]

    # The date to end at. Tuple in the format (day, month, year).
    to_date = tuple[int]

    # The time to start from. Tuple in the format (hour, minute) in 24 hour time.
    from_time = tuple[int]

    # The time to end at. Tuple in the format (hour, minute) in 24 hour time.
    to_time = tuple[int]

    # What this time block is for.
    purpose = str

    def build(fromD, toD, fromT, toT, purpose):
        block = TimeBlock({})
        block["from_date"] = fromD
        block["to_date"] = toD
        block["from_time"] = fromT
        block["to_time"] = toT
        block["purpose"] = purpose
        return block

class PlanState(TypedDict):
    """State representing the customer's plan conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's current time plan.
    plan: dict

    finished: bool

# the following functions generate string variants of the above classes

def format_timeblock(block):
    fr = f'{int(block["from_time"][0])}:{int(block["from_time"][1])}' if len(block["from_time"]) == 2 else "unknown"
    t = f'{int(block["to_time"][0])}:{int(block["to_time"][1])}' if len(block["from_time"]) == 2 else "unknown"
    return f'{fr}-{t} {block["purpose"]}'

def format_plan(plan, forAI = False):
    ret = ""
    for blockID in plan:
        ret += format_timeblock(plan[blockID])
        if forAI:
            ret += "(id=" + blockID + ")"
        ret += "\n"
    return ret

def format_state_plan(state, forAI = False):
    return format_plan(state["plan"], forAI)
