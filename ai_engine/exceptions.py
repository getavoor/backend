class PromptBlockedError(Exception):
    """
    The AI system's safeguards blocked this prompt.
    """
    pass

class NoResultError(Exception):
    """
    The AI system didn't return a result.
    """
    pass