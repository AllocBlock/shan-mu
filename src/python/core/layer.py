import numpy as np

class CLayer:
    def __init__(self, width : int, height : int, datas) -> None:
        self.width = width
        self.height = height
        self.datas : list[list] = datas

    @staticmethod
    def create(width : int, height : int, defaultValue : any):
        datas = np.full((width, height), defaultValue)
        return CLayer(width, height, datas)