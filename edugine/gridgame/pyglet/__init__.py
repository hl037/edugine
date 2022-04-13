import typing
from itertools import accumulate
from pathlib import Path
from operator import __add__

from ... import pyglet as backend
from ...pyglet import gui

from ... import core as grid_core
from ..core import models as grid_models
from ..core import controllers as grid_controllers
from ... import core as core

import numpy as np
import pyglet
from pyglet import gl

from icecream import ic

Grid = grid_models.Grid

Cell = grid_models.Cell

Entity = grid_models.Entity

Pos_t = core.Pos_t
Pos = core.Pos

Geometry = gui.Geometry

K = pyglet.window.key
M = pyglet.window.mouse


class Sprite(object):
  """
  Sprite object
  """
  def __init__(self, texture:pyglet.image.Texture, batch:pyglet.graphics.Batch, group:pyglet.graphics.Group):
    self.sprite = pyglet.sprite.Sprite(texture, batch=batch, group=group)
    self.size = texture.width, texture.height

  def setGeometry(self, geometry:Geometry):
    x, y, w, h = geometry
    self.sprite.update(x, y, None, None, w / self.size[0], h / self.size[1])

  def destroy(self):
    self.sprite.delete()


class Atlas(object):
  """
  A texture that is splitted in an atlas
  """
  def __init__(self, parent: 'VisualProvider', texture:pyglet.image.Texture, shape:tuple[int, int]):
    self.parent = parent
    self.texture = texture
    self.shape = shape
    self.subsize = (texture.width // shape[0], texture.height // shape[1])

  def associateVisual(self, x, y, visual:grid_models.Visual, z=0):
    self.parent.associateTextureVisual(
      self.texture.get_region(self.subsize[0] * x, self.subsize[1] * y, *self.subsize),
      visual,
      z
    )


class RetroOrderedGroup(pyglet.graphics.OrderedGroup):
  def set_state(self):
    super().set_state()
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    

class VisualProvider(object):
  """
  Provide sprites for displaying visuals
  """
  def __init__(self, paths:typing.Sequence[Path]):
    self.loader = pyglet.resource.Loader(list(paths))
    self.associated = dict()
    self.groups = [ RetroOrderedGroup(i) for i in range(6) ]

  def associateVisual(self, name:str, visual:int, z=0):
    self.associateTextureVisual(self.loader.image(name), visual, z)

  def associateTextureVisual(self, texture:pyglet.image.Texture, visual:int, z=0):
    self.associated[visual] = (texture, z)

  def loadAtlas(self, name:str, x_count:int, y_count:int):
    return Atlas(self, self.loader.image(name), (x_count, y_count))

  def getSprite(self, visual:int, batch:pyglet.graphics.Batch):
    tex, z = self.associated[visual]
    return Sprite(tex, batch, self.groups[z])
  

class GridCellView(gui.LayoutItem):
  """
  Handle the sprites
  """
  def __init__(self, ratio, size_preferred, size_min, size_max):
    super().__init__(
      ratio_preferred=ratio,
      ratio_min=ratio,
      ratio_max=ratio,
      size_preferred=size_preferred,
      size_min=size_min,
      size_max=size_max,
    )
    self.sprites = [] # type: list[Sprite]
  
  def replaceSprites(self, sprites:typing.Sequence[Sprite]):
    for s in self.sprites :
      s.destroy()
    self.sprites[:] = sprites
    self._updateGeometry()
  
  def _updateGeometry(self):
    for s in self.sprites :
      s.setGeometry(self.geometry)

  def setGeometry(self, geometry:Geometry):
    super().setGeometry(geometry)
    self._updateGeometry()
  
    
class GridView(gui.LayoutItem):
  """
  The grid view, that displays the sprite at the position of each cell...
  """
  def __init__(self,
    model:grid_models.Grid,
    visualProvider:VisualProvider,
    batch:pyglet.graphics.Batch,
    cell_ratio:float=1.0,
    cell_size_preferred=(32,32),
    cell_size_min=None,
    cell_size_max=None,
    *margin
  ):
    self.model = model
    self.model.addCellUpdateListener(self.cellUpdate)
    self.visualProvider = visualProvider
    self.batch = batch
    if not margin :
      margin = .02
    self.cellSize = (0,0)
    self.margin = margin
    self.grid = np.array([
      [
        gui.PaddingFracContainer(GridCellView(cell_ratio, cell_size_preferred, cell_size_min, cell_size_max), margin)
        for j in range(model.g.shape[1])
      ]
      for i in range(model.g.shape[0])
    ])
    
    base = self.grid[0,0] # type: PaddingFracContainer
    y_count, x_count = self.grid.shape
    ratio_f = x_count / y_count
    super().__init__(
      ratio_min = base.ratio_min * ratio_f,
      ratio_max = base.ratio_max * ratio_f,
      ratio_preferred = base.ratio_preferred * ratio_f,
      size_min = (base.size_min[0] * x_count, base.size_min[1] * y_count),
      size_max = (base.size_max[0] * x_count, base.size_max[1] * y_count),
      size_preferred = (base.size_preferred[0] * x_count, base.size_preferred[1] * y_count),
    )

  def cellUpdate(self, pos:Pos_t):
    self.grid[pos[0],pos[1]].item.replaceSprites( self.visualProvider.getSprite(v, self.batch) for v in self.model.g[pos[0], pos[1]].all_visuals )
  
  def setGeometry(self, geometry:Geometry):
    super().setGeometry(geometry)
    x_count, y_count = self.grid.shape
    x, y, w, h = geometry
    cw, ch = w // x_count, h // y_count
    rw, rh = w % x_count, h % y_count
    w_sizes = [ cw ] * (x_count - rw) + [ cw + 1 ] * rw
    h_sizes = [ ch ] * (y_count - rh) + [ ch + 1 ] * rh
    it = accumulate(w_sizes, __add__, initial=x)
    next(it)
    self.offsets_x = list(it)
    it = accumulate(h_sizes, __add__, initial=y)
    next(it)
    self.offsets_y = list(it)

    cx = x
    for R, cw in zip(self.grid, w_sizes) :
      cy = y
      for c, ch in zip(R, h_sizes) : # type: PaddingFracContainer, float
        c.setGeometry((cx, cy, cw, ch))
        cy += ch
      cx += cw

  def mapToCell(self, pos:Pos_t) -> Pos_t:
    px, py = pos
    x, y, w, h = self.geometry
    if x <= px < x + w and y <= py < y + h :
      return Pos(
        next( i for i, x in enumerate(self.offsets_x) if px < x ),
        next( i for i, y in enumerate(self.offsets_y) if py < y )
      )
    else :
      return None



class GridGame(object):
  """
  The Gridgame, which is composed of tiles (or Cells). It is design to accoupy the full window.

  Only the model and the visualProvider remain cusomizable.
  """
  def __init__(self,
    model:grid_models.Grid,
    visualProvider:VisualProvider,
    window:backend.Window,
    cell_ratio=1.,
    cell_size_preferred=(32, 32),
    cell_size_min=(16,16),
    cell_size_max=(gui.Max, gui.Max),
    *margin
  ):
    self.model = model
    self.visualProvider = visualProvider


    self.infoL = gui.Label(batch=window.scene,
      ratio_min=2,
      ratio_max=3,
      size_min=(100, 50),
      size_max=(500, 250),
      size_preferred=(300,100),
    )
    self.infoM = gui.Label(batch=window.scene,
      ratio_min=2,
      ratio_max=3,
      size_min=(100, 50),
      size_max=(500, 250),
      size_preferred=(300,100),
    )
    self.infoR = gui.Label(batch=window.scene,
      ratio_min=2,
      ratio_max=3,
      size_min=(100, 50),
      size_max=(500, 250),
      size_preferred=(300,100),
    )
    
    infoLayout = gui.HBoxLayout()
    with infoLayout.batchUpdate() :
      infoLayout.addItem(gui.ConstRatioContainer(self.infoL, (gui.Alignment.LEFT, gui.Alignment.MIDDLE)))
      infoLayout.addItem(gui.ConstRatioContainer(self.infoM, (gui.Alignment.MIDDLE, gui.Alignment.MIDDLE)))
      infoLayout.addItem(gui.ConstRatioContainer(self.infoR, (gui.Alignment.RIGHT, gui.Alignment.MIDDLE)))

    self.view = GridView(model, visualProvider, window.scene,
      cell_ratio=cell_ratio,
      cell_size_preferred=cell_size_preferred,
      cell_size_min=cell_size_min,
      cell_size_max=cell_size_max,
      *margin
    )
    
    self.mainLayout = gui.VBoxLayout()
    with self.mainLayout.batchUpdate() :
      self.mainLayout.addItem(infoLayout),
      self.mainLayout.addItem(gui.ConstRatioContainer(self.view))
    
    window.layout = self.mainLayout
    self.gridController = grid_controllers.GridController()
    
    self.controller = window.controller
    self.controller.addMouseDownListener(self.mouseDown)
    self.controller.addMouseUpListener(self.mouseUp)
    self.addGlobalMouseDownListener = self.controller.addMouseDownListener
    self.addGlobalMouseUpListener = self.controller.addMouseUpListener
    self.addMouseDownListener = self.gridController.addMouseDownListener
    self.addMouseUpListener = self.gridController.addMouseUpListener
    self.addKeyDownListener = self.controller.addKeyDownListener
    self.addKeyUpListener = self.controller.addKeyUpListener
    self.addTickListener = self.controller.addTickListener
    self.removeGlobalMouseDownListener = self.controller.removeMouseDownListener
    self.removeGlobalMouseUpListener = self.controller.removeMouseUpListener
    self.removeMouseDownListener = self.gridController.removeMouseDownListener
    self.removeMouseUpListener = self.gridController.removeMouseUpListener
    self.removeKeyDownListener = self.controller.removeKeyDownListener
    self.removeKeyUpListener = self.controller.removeKeyUpListener
    self.removeTickListener = self.controller.removeTickListener
    self.onGlobalMouseDown = self.controller.onMouseDown
    self.onGlobalMouseUp = self.controller.onMouseUp
    self.onMouseDown = self.gridController.onMouseDown
    self.onMouseUp = self.gridController.onMouseUp
    self.onKeyDown = self.controller.onKeyDown
    self.onKeyUp = self.controller.onKeyUp
    self.onTick = self.controller.onTick

  def mouseDown(self, pos:Pos_t, button):
    self.gridController.mouseDown(self.view.mapToCell(pos), button)
    
  def mouseUp(self, pos:Pos_t, button):
    self.gridController.mouseUp(self.view.mapToCell(pos), button)



    


