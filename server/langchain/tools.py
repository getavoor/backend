from collections.abc import Iterable
from random import randint

from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import tool

# this part defines the tool signatures
@tool
def add_to_plan(from_hour: int, from_minute: int, to_hour: int, to_minute: int, purpose: str) -> str:
    """Adds the specified block to the user's day plan. The values should be exact amounts in 24-hour time. 'From' time might not be before 'to' time.

    Returns:
      The updated plan. Note that UUIDs will also be returned; keep them in your memory but don't show them to the user.
    """


@tool
def get_plan() -> str:
    """Returns the user's plan so far. Note that UUIDs will also be returned; keep them in your memory but don't show them to the user."""


@tool
def show_plan():
    """Displays the plan to the user."""


@tool
def clear_plan():
    """Removes all items from the user's plan."""


@tool
def remove_from_plan(uuid: str):
    """Removes the item with the specified UUID from the user's plan."""


@tool
def add_to_calendar(title: str, offset: float, post_creation_message: str):
    """
    Show the user a link to download an ICS file with the finished plan.
    Arguments:
    - title - the title of the file.
    - offset - the offset from UTC of the user's timezone, in hours (e.g. GMT+5:30 -> 5.5, GMT+1 -> 1, GMT-3 -> -3)
    - post_creation_message - the message that will be shown after the search is performed.
    """
