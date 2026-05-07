"""
Avoor - AI Engine Base
(c) 2024-2025 githubcatw & Claude
"""
from .exceptions import *

class AIEngine:
    """
    Perform tasks related to generative AI.
    Note: This is a base class. Use langchain for time management AI features.
    """

    def __init__(self):
        self.name = "BaseAI"

    async def exec_prompt(self, prompt: str) -> str:
        """
        Run a prompt and return the response.
        """
        # check if the prompt wants to raise an exception
        if prompt.startswith("@raise"):
            cmds = prompt.split(" ")
            # if there is no exception passed, give a simple response
            if len(cmds) < 2:
                return "I didn't understand that."
            # check what kind of exception was requested and raise it
            if cmds[1] == "no_result":
                print("Raising a NoResultError as it was requested with the prompt")
                raise NoResultError()
            elif cmds[1] == "blocked":
                print("Raising a PromptBlockedError as it was requested with the prompt")
                raise PromptBlockedError()
        return "GenAI response for " + prompt

    async def start_session(self, start_message: str = None):
        """
        Start a chat session.
        """
        return AIChatSession(self, start_message)

class AIChatSession:
    """
    A chat session with an AI model.
    """
    def __init__(self, model: AIEngine, start_message: str = None):
        self.model = model

    async def send_message(self, message: str) -> str:
        """
        Sends a message to the model and returns the response.
        """
        return "GenAI chat response to " + message
