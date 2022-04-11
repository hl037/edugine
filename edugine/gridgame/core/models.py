import time
from pathlib import Path
from dataclasses import dataclass
import numpy as np

from .. import core

CellHandler = typing.Callable[[Pos_t], None]

class Cell(object):
  """
  A cell model for a grid
  """
  def __init__(self, grid:Grid, pos:core.Pos_t):
    self.grid = grid
    self.pos = pos
    self.visuals = set() # type: list[Visual]
    self.entities = set() #type: set[Entity]

  def __getattr__(self, k):
    return None

  def update(self):
    grid.cellUpdate(pos)


class Grid(object):
  """
  A Grid model
  """
  def __init__(self, shape:tuple[int, int]):
    self.g = CellGrid.create(shape)
    self.cellUpdateListeners = set() # type: set[CellUpdateHandler]

    
  def addCellUpdateListener(self, cb:CellHandler):
    self.cellUpdateListeners.add(cb)
    
  def removeCellUpdateListener(self, cb:CellHandler):
    self.cellUpdateListeners.remove(cb)
    
  def cellUpdate(self, pos:Pos_t):
    for cb in self.cellUpdateListeners :
      cb(pos)

  onCellUpdate = addCellUpdateListener


class CellGrid(np.ndarray):
  """
  Hold a game grid
  """

  def __new__(
      subtype, shape, dtype=Cell, buffer=None, offset=0,
      strides=None, order=None
  ):
    if len(shape) != 2 :
      raise RuntimeError('A grid cannot be other than 2-dimensionnal')
    if not issubclass(dtype, Cell) :
      raise RuntimeError('A grid can only hold Cells')
    obj = super().__new__(
      subtype, shape, dtype,
      buffer, offset, strides, order
    )
    self[:] = [ [ Cell(self, Pos(x, y)) for y in range(h) ] for x in range(w) ]
    return obj

  @classmethod
  def create(cls, shape):
    return cls(shape)

  @property
  def w(self):
    return self.g.shape[0]

  @property
  def h(self):
    return self.g.shape[1]
  
  def __getitem__(self, k):
    if isinstance(k, _Pos) :
      return super().__getitem__((k[0], k[1]))
    else :
      return super().__getitem__(k)

  def __setitem__(self, k, v):
    if isinstance(k, _Pos) :
      return super().__setitem__((k[0], k[1]), v)
    else :
      return super().__setitem__(k, v)

  @property
  def dirty(self):
    return ( c.dirty for c in np.nditer(self) )

  def __getattr__(self, k):
    return np.vectorize(lambda x: getattr(x, k), object)(self)

  def __setattr__(self, k, v):
    if k not in self.__dict__ :
      np.frompyfunc(lambda x: setattr(x, k, v), nin=1, nout=0)(self)
    

class Visual(object):
  #TODO
  """
  Class permitting to load images
  """
  def __init__(self, path, z=0):
    super().__init__()
    self.path = path
    self.z = z

  def load(self, path):
    raise NotImplementedError()

  @property
  def _cell_list(self):
    return self._cell.visuals


class Entity(CellItem):
  """
  Class to represent an object, a character etc.
  Note : it is important to flag the cell as dirty when changing features or visuals
  """

  _id_count = 0

  def __init__(self, cell:Cell = None):
    if not hasattr(self, 'visuals') :
      self.visuals = []
    self._cell = None
    self._id = self.__class__._id_count
    self.__class__._id_count += 1

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
      self._cell.update

  def removeFromCell(self, cell:Cell):
    self.addToCell(None)
    

class View(object):
  """
  Class that represent what the user sees
  """
  def __init__(self):
    self.grid = None

