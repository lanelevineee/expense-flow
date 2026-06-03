from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AIProvider(ABC):
    @abstractmethod
    def chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        ...
