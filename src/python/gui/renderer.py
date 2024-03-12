from __future__ import annotations # for hint enclose class, https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
import numpy as np
from enum import Enum
from abc import ABC, abstractmethod
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from ..core.terrain import CTerrain

class ActorRenderMode(Enum):
    Point = 0  # VTK_POINTS    == 0
    Wireframe = 1  # VTK_WIREFRAME == 1
    Surface = 2  # VTK_SURFACE   == 2

class ActorProxy(ABC):
    """proxy/wrapper for vtk actor to setup actor eazier"""

    def __init__(self, vActor: vtk.vtkActor, name: str = None) -> None:
        self.vActor = vActor  # vtk actor
        self.name: str = name

    @abstractmethod
    def get_property(self) -> vtk.vtkProperty:
        pass

    def get_visibility(self) -> bool:
        return self.vActor.GetVisibility()
    
    def get_actor_color(self) -> list[float]:
        return self.get_property().GetColor()
        
    def set_visibility(self, isVisible: bool):
        self.vActor.SetVisibility(isVisible)

    def show(self):
        self.set_visibility(True)

    def hide(self):
        self.set_visibility(False)

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str = None) -> ActorProxy:
        self.name = name
        return self

    def set_actor_color(self, color) -> ActorProxy:
        self.get_property().SetColor(color)
        return self
    
    def set_opacity(self, opacity : float) -> ActorProxy:
        self.get_property().SetOpacity(opacity)
        return self

    def set_point_size(self, size) -> ActorProxy:
        self.get_property().SetPointSize(size)
        return self

    def set_line_width(self, size) -> ActorProxy:
        self.get_property().SetLineWidth(size)
        return self

    def set_render_mode(self, mode: ActorRenderMode) -> ActorProxy:
        self.get_property().SetRepresentation(mode.value)
        return self

    def as_points(self) -> ActorProxy:
        self.set_render_mode(ActorRenderMode.Point)
        return self

    def as_wireframe(self) -> ActorProxy:
        self.set_render_mode(ActorRenderMode.Wireframe)
        return self

    def as_surface(self) -> ActorProxy:
        self.set_render_mode(ActorRenderMode.Surface)
        return self
    
    def render_point_as_sphere(self, state = True) -> ActorProxy:
        self.get_property().SetRenderPointsAsSpheres(state)
        return self
    
    def render_line_as_tube(self, state = True) -> ActorProxy:
        self.get_property().SetRenderLinesAsTubes(state)
        return self

class ActorProxy3D(ActorProxy):
    def get_property(self):
        return self.vActor.GetProperty()
    
    def disable_shading(self):
        prop = self.get_property()
        prop.SetAmbient(1.0)
        prop.SetDiffuse(0.0)
        prop.SetSpecular(0.0)

class ActorProxyText(ActorProxy):
    def get_property(self):
        return self.vActor.GetTextProperty()

    def set_position(self, start, end):
        self.vActor.SetPosition(start, end)

    def set_font_size(self, size):
        self.get_property().SetFontSize(size)

    def set_text_color(self, color):
        self.get_property().SetColor(color)

class TimerCallback():
    def __init__(self, customCallback):
        self.customCallback = customCallback

    def execute(self, iren, event):
        self.customCallback()
        iren.GetRenderWindow().Render()

class Renderer:
    def __init__(self , vName : str = "Renderer") -> None:
        self.actorProxies: list[ActorProxy] = []
        self.vRenderer = vtk.vtkRenderer()
        self.name = vName

    def get_camera(self) -> vtk.vtkCamera:
        return self.vRenderer.GetActiveCamera()

    def use_parallel_projection(self):
        self.get_camera().ParallelProjectionOn()
    def use_perspective_projection(self):
        self.get_camera().ParallelProjectionOff()

    def reset_camera(self):
        self.vRenderer.ResetCamera()

    def start(self, title="Visualize", width=1024, height=1024, resetCamera = True):
        window = vtk.vtkRenderWindow()
        window.SetSize(width, height)
        window.SetWindowName(title)
        window.AddRenderer(self.vRenderer)
        window.SetMultiSamples(8)

        if resetCamera:
            self.vRenderer.ResetCamera()

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(window)
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.Initialize()
        interactor.Start()

    def get_camera_pos(self):
        return self.vRenderer.GetActiveCamera().GetPosition()
    def set_camera_pos(self, pos):
        self.vRenderer.GetActiveCamera().SetPosition(pos)

    def get_camera_focal_pos(self):
        return self.vRenderer.GetActiveCamera().GetFocalPoint()
    def set_camera_focal_pos(self, pos):
        self.vRenderer.GetActiveCamera().SetFocalPoint(pos)

    def set_camera_distance(self, distance):
        self.vRenderer.GetActiveCamera().SetDistance(distance)
    
    def _create_color_array(self, colors):
        colors = np.array(colors) * 255
        vColors = vtk.vtkUnsignedCharArray()
        vColors.SetNumberOfComponents(3)
        vColors.SetName("Colors")
        vColors.SetNumberOfTuples(len(colors))
        for i, color in enumerate(colors):
            vColors.SetTuple3(i, color[0], color[1], color[2])
        return vColors

    def _add_actor_by_poly_data(self, vPolyData: vtk.vtkPolyData, color=None, name = None) -> ActorProxy3D:
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vPolyData)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actorProxy = ActorProxy3D(actor, name)
        if color is not None:
            if (
                not np.isscalar(color) and len(color) == 3 and np.isscalar(color[0])
            ):  # [r, g, b]
                actorProxy.set_actor_color(color)
            else:  # color array
                pointNum = vPolyData.GetPoints().GetNumberOfPoints()
                assert (
                    len(color) == pointNum
                ), "if want to set color for each vertex, vertex num should be same with color num"
                colorArray = self._create_color_array(color)
                vPolyData.GetPointData().SetScalars(colorArray)

        self.vRenderer.AddActor(actor)
        self.actorProxies.append(actorProxy)
        return actorProxy

    def _create_poly_with_points(self, points):
        pointNum = len(points)
        vPoints = vtk.vtkPoints()
        vPoints.SetNumberOfPoints(len(points))
        for i in range(pointNum):
            vPoints.SetPoint(i, points[i])

        vPoly = vtk.vtkPolyData()
        vPoly.SetPoints(vPoints)

        return vPoly

    def add_point_cloud(self, points, color=None, name = None) -> ActorProxy3D:
        pointNum = len(points)
        vCells = vtk.vtkCellArray()
        for i in range(pointNum):
            vCells.InsertNextCell(1)
            vCells.InsertCellPoint(i)

        vPoly = self._create_poly_with_points(points)
        vPoly.SetVerts(vCells)

        return self._add_actor_by_poly_data(vPoly, color, name)
    
    def add_terrain(self, terrain : CTerrain, color=None, name = None):
        x = list(range(0, terrain.width))
        z = list(range(0, terrain.height))
        px, pz = np.meshgrid(x, z)
        px = px.reshape(-1)
        pz = pz.reshape(-1)
        points = np.stack([px, terrain.layers['height'].datas.reshape(-1) * 100, pz], axis=-1)
        return self.add_point_cloud(points).set_point_size(5)
    
    def add_text(self, text, position=None, color=None, fontSize = 24, name = None) -> ActorProxyText:
        textActor = vtk.vtkTextActor()
        textActor.SetInput(text)

        actorProxy = ActorProxyText(textActor, name)
        if color is not None:
            actorProxy.set_text_color(color)
        if position is not None:
            actorProxy.set_position(position[0], position[1])
        actorProxy.set_font_size(fontSize)

        self.vRenderer.AddActor(textActor)
        self.actorProxies.append(actorProxy)
        return actorProxy

    def clear(self):
        self.actorProxies.clear()
        self.vRenderer.RemoveAllViewProps()