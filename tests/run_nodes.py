import test_common

from python.core.graph import CGraph
from python.core.terrain import CTerrain
from python.core.create_terrain import CNodeCreateTerrain
from python.core.terrain_noise import CNodeTerrainNoise
from PIL import Image
from python.gui.renderer import Renderer

if __name__ == "__main__":
    node = CNodeCreateTerrain()
    inputs = {
        "width": 512,
        "height": 512,
        "initialHeight": 0,
    }
    terrain : CTerrain = node.run(inputs)
    node = CNodeTerrainNoise()
    inputs = {
        "terrain": terrain,
    }
    terrain : CTerrain = node.run(inputs)
    
    # image = Image.fromarray(terrain.layers['height'].datas * 255)
    # image.show()

    r = Renderer()
    r.add_terrain(terrain)
    r.start()

    