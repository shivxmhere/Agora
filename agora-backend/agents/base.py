from abc import ABC, abstractmethod
from typing import Callable, Any

class BaseAgent(ABC):
    @abstractmethod
    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        """
        Runs the agent synchronously (could be blocking locally, but runner will use to_thread).
        Stream callback should be called with chunks of data.
        Returns the final output string.
        """
        pass
