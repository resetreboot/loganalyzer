# Python imports
from typing import Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LogTypeInfo:
    string: int = 1
    integer: int = 2
    timestamp: int = 3


class Formatter(ABC):
    """
    Abstract class for a formatter, this class is made to
    implement the functions needed by the formatter
    """
    @abstractmethod
    def write_report(self, data: Dict[str, Any], output_file: str):
        pass


class Operation(ABC):
    """
    Abstract class for an Operation, that will get the
    processed lines in a dict and will consume the data
    """
    @abstractmethod
    def process(self, processed: Dict[str, Any]):
        """
        Gets the dictionary generated and consumes the data
        """
        pass

    @abstractmethod
    def generate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets a dictionary with results and returns the dictionary updated
        with the data this Operation generates
        """
        pass
