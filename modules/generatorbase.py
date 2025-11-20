from abc import ABC, abstractmethod
from numpy import ndarray

class GeneratorBase(ABC):
    @abstractmethod
    def generate(self) -> ndarray:
        """Generate the 2D map of the generators output

        Returns:
            ndarray: Output 2D array
        """
        pass