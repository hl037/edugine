from ...core import Pos_t
import typing
from collections import defaultdict

from icecream import ic

try :
  import edugine.mouse as M
  import edugine.keyboard as K
except :
  raise ImportError('Please import a backend before importing core modules')


MouseGridHandler = typing.Callable[[Pos_t, int], None]

class GridController(object):
  """
  A grid cell
  """
  def __init__(self):
    self.mouseDownListeners = defaultdict(lambda : [])
    self.mouseUpListeners = defaultdict(lambda : [])
  

  # MouseDown
  def addMouseDownListener(self, cb:MouseGridHandler, buttons:int|None=None):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseDownListeners[b].append(cb)
    return cb
    
  def removeMouseDownListener(self, cb:MouseGridHandler, buttons:int|None=None):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseDownListeners[b].discard(cb)
    return cb

  def onMouseDown(self, buttons:int):
    return lambda f: self.addMouseDownListener(f, buttons)

  def mouseDown(self, pos:Pos_t, button:int):
    for cb in self.mouseDownListeners[button] :
      cb(pos, button)
  
  #MouseUp
  def addMouseUpListener(self, cb:MouseGridHandler, buttons:int|None=None):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseUpListeners[b].append(cb)
    return cb
    
  def removeMouseUpListener(self, cb:MouseGridHandler, buttons:int|None=None):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseUpListeners[b].discard(cb)
    return cb

  def onMouseUp(self, buttons:int):
    return lambda f: self.addMouseUpListener(f, buttons)
  
  def mouseUp(self, pos:Pos_t, button:int):
    for cb in self.mouseUpListeners[button] :
      cb(pos, button)

