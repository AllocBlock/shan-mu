from .layer import CLayer
from . import log

class CTerrain:
    def __init__(self, width : int, height : int, initalHeight : float) -> None:
        self.width = width
        self.height = height
        self.layers : dict[str, CLayer] = dict()
        self.add_layer("height", CLayer.create(width, height, initalHeight))

    def add_layer(self, name : str, layer : CLayer):
        assert layer.width == self.width, f"The width of added layer ({layer.width}) must match the width of terrain ({self.width})"
        assert layer.height == self.height, f"The height of added layer ({layer.height}) must match the height of terrain ({self.height})"
        if name in self.layers:
            log.warn(f"Layer {name} already exists, will be replaced by new layer")
        self.layers[name] = layer