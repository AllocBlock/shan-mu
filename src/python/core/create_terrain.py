from .node import CNode
from .terrain import CTerrain

class CNodeCreateTerrain(CNode):
    def __init__(self) -> None:
        name = 'Create Terrain'
        inputs = []
        params = [
            "width", "height", "initialHeight"
        ]
        super().__init__(name, inputs, params)
    
    def run(self, inputs : dict) -> CTerrain:
        width = inputs["width"]
        height = inputs["height"]
        initialHeight = inputs["initialHeight"]
        return CTerrain(width, height, initialHeight)
    
