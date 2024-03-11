from abc import ABC, abstractmethod

# TODO: input/output type limitation
class CNode(ABC):
    def __init__(self, name : str, inputs : list[str], parameters : dict) -> None:
        self.name = name
        self.inputs = inputs
        self.parameters : dict = parameters
    
    @abstractmethod
    def run(self, inputs : dict):
        pass
    
