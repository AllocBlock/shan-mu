from .node import CNode

class CGraph:
    def __init__(self) -> None:
        self.nodes : list[CNode] = []
        self.links = []

    def get_node_by_name(self, name : str) -> CNode:
        for node in self.nodes:
            if node.name == name:
                return node
        raise RuntimeError(f"Node ({name}) not found")

    def get_output(self, node):
        return None