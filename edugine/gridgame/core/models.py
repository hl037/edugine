import time
from pathlib import Path
from dataclasses import dataclass
import typing
import numpy as np

from .. import core

from ...core import Pos, Pos_t

CellHandler = typing.Callable[[Pos_t], None]

from icecream import ic

class Cell(object):
  """
  A cell model for a grid
  """
  def __init__(self, grid:'Grid', pos:Pos_t):
    self.grid = grid
    self.pos = pos
    self.visuals = set() # type: list[Visual]
    self.entities = set() #type: set[Entity]

  def __getattr__(self, k:str):
    if k.startswith('__'):
      raise AttributeError(k)
    return None

  def update(self):
    self.grid.cellUpdate(self.pos)

  @property
  def all_visuals(self):
    return list(self.visuals) + [ v for e in self.entities for v in e.visuals ]

  def __add__(self, pos:Pos_t):
    if isinstance(pos, tuple) :
      pos = Pos(*pos)
    elif not isinstance(pos, Pos_t) :
      raise TypeError('not a position')
    return self.grid.cell(self.pos + pos)

      


class Grid(object):
  """
  A Grid model
  """
  def __init__(self, shape:tuple[int, int]):
    self.g = CellGrid.create(shape, self)
    self.cellUpdateListeners = set() # type: set[CellUpdateHandler]

    
  def addCellUpdateListener(self, cb:CellHandler):
    self.cellUpdateListeners.add(cb)
    
  def removeCellUpdateListener(self, cb:CellHandler):
    self.cellUpdateListeners.remove(cb)
    
  def cellUpdate(self, pos:Pos_t):
    for cb in self.cellUpdateListeners :
      cb(pos)

  onCellUpdate = addCellUpdateListener
  
  def cell(self, pos:Pos_t) -> Cell:
    x, y = pos
    x_count, y_count = self.g.shape
    if 0 <= x < x_count and 0 <= y < y_count:
      return self.g[x, y]
    else :
      return None

  def __getitem__(self, k):
    return self.g.__getitem__(k)



class CellGrid(np.ndarray):

  def __new__(
      subtype, shape, dtype=Cell, buffer=None, offset=0,
      strides=None, order=None, parent=None
  ):
    if len(shape) != 2 :
      raise RuntimeError('A grid cannot be other than 2-dimensionnal')
    if not issubclass(dtype, Cell) :
      raise RuntimeError('A grid can only hold Cells')
    obj = super().__new__(
      subtype, shape, dtype,
      buffer, offset, strides, order
    )
    if parent is not None :
      w, h = shape
      obj[...] = [ [ Cell(parent, Pos(x, y)) for y in range(h) ] for x in range(w) ]
    return obj

  @classmethod
  def create(cls, shape, parent):
    return cls(shape, parent=parent)

  def __getitem__(self, k):
    if isinstance(k, Pos_t) :
      return super().__getitem__((k[0], k[1]))
    else :
      return super().__getitem__(k)

  def __setitem__(self, k, v):
    if isinstance(k, Pos_t) :
      return super().__setitem__((k[0], k[1]), v)
    else :
      return super().__setitem__(k, v)

  def __getattr__(self, k):
    return np.frompyfunc(lambda x: getattr(x, k), nin=1, nout=1)(self)

  def __setattr__(self, k, v):
    if k not in self.__dict__ :
      np.frompyfunc(lambda x: setattr(x, k, v), nin=1, nout=0)(self)
    


_visual_count = 0

def Visual():
  global _visual_count
  rv = _visual_count
  _visual_count += 1
  return rv


class Entity(object):
  """
  Class to represent an object, a character etc.
  Note : it is important to flag the cell as dirty when changing features or visuals
  """

  def __init__(self, cell:Cell = None):
    if not hasattr(self.__class__, 'visuals') :
      self.visuals = []
    self._cell = None
    self.cell = cell
    
  @property
  def cell(self):
    return self._cell

  @cell.setter
  def cell(self, new_cell:Cell):
    self.addToCell(new_cell)

  def addToCell(self, new_cell:Cell):
    if self._cell is new_cell :
      return
    if self._cell :
      self._cell.entities.discard(self)
      self._cell.update()
    self._cell = new_cell
    if self._cell :
      self._cell.entities.add(self)
      self._cell.update()

  def removeFromCell(self, cell:Cell):
    self.addToCell(None)

  def __getattr__(self, k):
    return None

class View(object):
  """
  Class that represent what the user sees
  """
  def __init__(self):
    self.grid = None

