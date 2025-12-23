from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, List
from pydantic import BaseModel

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT")

class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    All Ukkie-Trader agents must implement this.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name (e.g., 'Proposer')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Agent version (e.g., '1.0.0')"""
        pass

    @abstractmethod
    async def validate_input(self, input_data: InputT) -> Tuple[bool, List[str]]:
        """Validate input data before running"""
        pass

    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """Execute the agent's logic"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if external dependencies (LLM, DB, API) are available"""
        pass
