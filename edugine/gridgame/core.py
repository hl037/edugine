import time
from pathlib import Path
from dataclasses import dataclass
import numpy as np


class Cell(object):
  """
  A grid cell
  """
  def __init__(self, grid: Grid, pos:np.ndarray):
    self.grid = grid
    self.pos = pos
    self.visuals = set() # type: list[Visual]
    self.features = set() #type: list[Feature]
    self.entities = set() #type: set[Entity]
    self.mouseDownListeners = []
    self.mouseUpListeners = []
    self.dirty = False
  
  def __add__(self, pos:np.ndarray):
    return self.grid[self.pos + pos]

  def add(self, obj):
    obj.addToCell(self)
  
  def remove(self, obj):
    obj.removeFromCell(None)
    
  def addMouseDownListener(self, cb):
    self.mouseDownListeners.append(cb)
    
  def removeMouseDownListener(self, cb):
    self.mouseDownListeners.remove(cb)

  def addMouseUpListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeMouseUpListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def mouseDown(self):
    for cb in self.mouseDownListeners :
      cb(self)
      
  def mouseUp(self):
    for cb in self.mouseUpListeners :
      cb(self)



class GridMethod(object):
  """
  
  """
  class Partial(object):
    """
    
    """
    def __init__(self, g, f):
      self.g = g
      self.m = m
      
    def __call__(self, *args, **kwargs):
      for x in np.nditer(self.g) :
        self.m(x, *args, **kwargs)
      
  def __init__(self, m):
    self.m = m
    
  def __get__(self, obj, objtype=None):
    return GridMethod.Partial(obj, self.m)

  def __set__(self, *args, **kwargs):
    raise AttributeError()
    

class Grid(np.ndarray):
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
  def create(cls, w, h):
    return Grid((w, h))

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

  add = GridMethod(Cell.add)
  remove = GridMethod(Cell.remove)
  
  addMouseDownListener = GridMethod(Cell.addMouseDownListener)
  removeMouseDownListener = GridMethod(Cell.removeMouseDownListener)
  addMouseUpListener = GridMethod(Cell.addMouseUpListener)
  removeMouseUpListener = GridMethod(Cell.removeMouseUpListener)
  
  mouseDown = GridMethod(Cell.mouseDown)
  mouseUp = GridMethod(Cell.mouseUp)



class CellItem(object):
  """
  (Just to avoid code duplication) An object that can be added to one cell at a time
  """

  def __init__(self):
    self._id = self.__class__._id_count
    self.__class__._id_count += 1
    self._cell = None

  def __init_subclass__(cls):
    cls.id = int
    cls._id_count = 0
  
  def addToCell(self, cell:Cell):
    self._cell_list.add(cell)

  def removeFromCell(self, cell:Cell):
    self._cell_list.discard(self)

  @property
  def _cell_list(self) -> set[Cell]:
    raise NotImplementedError()

class Visual(CellItem):
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


class Feature(CellItem):
  """
  Class to generate unique integers to be used as Feature
  """
  
  @property
  def _cell_list(self):
    return self._cell.features

class Entity(CellItem):
  """
  Class to represent an object, a character etc.
  Note : it is important to flag the cell as dirty when changing features or visuals
  """

  def __init__(self, cell:Cell = None):
    if not hasattr(self, 'visuals') :
      self.visuals = []
    if not hasattr(self, 'features') :
      self.features = []
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
      self.self._cell.entities.discard(self)
      self._cell.dirty = True
    self._cell = new_cell
    if self._cell :
      self.self._cell.entities.add(self)
      self._cell.dirty = True

  def removeFromCell(self, cell:Cell):
    if cell is not self._cell :
      return
    self._cell = None
    cell.entities.discard(self)
    cell.dirty = True
    

class View(object):
  """
  Class that represent what the user sees
  """
  def __init__(self):
    self.grid = None

class Controller(object):
  """
  Class To handle all the game
  """
  def __init__(self, view:View):
    self.view = view
    self.fps = 60
    self.running = True
    self.keyDownListeners = defaultdict(default_factory=lambda : [])
    self.keyUpListeners = defaultdict(default_factory=lambda : [])
    self.tickListener = []
    self.mouseDownListeners = []
    self.mouseUpListeners = []
    
  
  @property
  def fps(self):
    return self._fps
  
  @fps.setter
  def fps(self, val):
    self._fps = val
    self._spf = 1 / val

  @property
  def spf(self):
    return self._spf
  
  @spf.setter
  def spf(self, val):
    self._spf = val
    self._fps = 1 / val

  def quit(self):
    self.running = False

  def loop(self):
    self.game_time = 0
    base = time.perf_counter()
    cur_time = base
    due_time = base + self._spf

    while self.running :
      self.tick()
      if cur_time < due_time :
        self.render()
        # else : lag
      cur = time.perf_counter()
      d = due_time - cur
      if d > 0 :
        time.sleep(d)
      due_time += self._spf
      self.game_time += self._spf

  def isKeyDown(self, key:int):
    raise NotImplementedError()

  def isClicked(self, pos:Pos_t = None):
    raise NotImplementedError()

  def addKeyDownListener(self, key:int|None, cb):
    self.keyDownListeners[key].append(cb)
    
  def removeKeyDownListener(self, key:int|None, cb):
    self.keyDownListeners[key].remove(cb)

  def onKeyDown(self, key:int):
    return lambda f: self.addKeyDownListener(key, f)
  
  def addKeyUpListener(self, key:int, cb):
    self.keyUpListeners[key].append(cb)
    
  def removeKeyUpListener(self, key:int, cb):
    self.keyUpListeners[key].remove(cb)

  def onKeyUp(self, key:int):
    return lambda f: self.addKeyUpListener(key, f)
  
  def addMouseDownListener(self, cb):
    self.mouseDownListeners.append(cb)
    
  def removeMouseDownListener(self, cb):
    self.mouseDownListeners.remove(cb)

  def onMouseDown(self):
    return lambda f: self.addMouseDownListener(f)
  
  def addMouseUpListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeMouseUpListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def onMouseUp(self):
    return lambda f: self.addMouseUpListener(f)
  
  def addTickListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeTickListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def onTick(self):
    return lambda f: self.addTickListener(f)

  def tick(self):
    self.dispatchEvents()
    for t in self.tickListener :
      t()
      
  def dispatchEvents(self):
    raise NotImplementedError()








