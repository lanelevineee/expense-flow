from abc import ABC, abstractmethod


class BaseScreen(ABC):
    @abstractmethod
    def show(self) -> None:
        ...
