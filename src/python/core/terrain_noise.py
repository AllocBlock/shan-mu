from .node import CNode
from .terrain import CTerrain
import numpy as np

class CNodeTerrainNoise(CNode):
    def __init__(self) -> None:
        name = 'Terrain Noise'
        inputs = ["terrain"]
        params = []
        super().__init__(name, inputs, params)
    
    def run(self, inputs : dict) -> CTerrain:
        terrain : CTerrain = inputs['terrain']
        shape = terrain.layers["height"].datas.shape
        terrain.layers["height"].datas = np.random.random(shape)
        return terrain
    
