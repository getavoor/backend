from . import AIEngine, AIChatSession
from .exceptions import *
from google import genai
from google.genai.types import Content, FinishReason, Part

class GeminiAIChatSession(AIChatSession):
    """
    A chat session with a Google AI model.
    """
    def __init__(self, chat):
        self.chat = chat

    async def send_message(self, message: str) -> str:
        """
        Sends a message to the model and returns the response.
        """
        response = await self.chat.send_message(message)
        return response.text

class GeminiAIEngine(AIEngine):
    """
    Perform tasks related to generative AI with Google's Gemini models.
    """

    def __init__(self, key: str, model: str = 'gemini-2.5-flash'):
        self.name = "Gemini"
        # Initialize Google GenAI
        self.client = genai.Client(api_key=key).aio
        self.model_id = model

    async def exec_prompt(self, prompt: str) -> str:
        """
        Run a prompt and return the response.
        """
        response = await self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )

        # check if the ai returned a response
        if response.candidates is None or response.text is None or len(response.candidates) == 0:
            raise NoResultError()
        # check if the latest response was banned by gemini's safeguards
        if response.candidates[0].finish_reason == FinishReason.SAFETY:
            raise PromptBlockedError()

        # if the response seems ok, return it
        return response.text

    async def start_session(self, start_message: str | None = None) -> GeminiAIChatSession:
        """
        Start a chat session.
        """
        history = None
        if start_message is not None:
            history = [
                Content(role="user", parts=[Part.from_text(text=start_message)])
            ]
        chat = self.client.chats.create(model=self.model_id, history=history)
        return GeminiAIChatSession(chat)
