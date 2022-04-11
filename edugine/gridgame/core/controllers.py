from ...core import Pos_t
import typing


MouseGridHandler = typing.Callable[[Pos_t], None]

class GridController(object):
  """
  A grid cell
  """
  def __init__(self):
    self.mouseDownListeners = set() # type: set[MouseHandler]
    self.mouseUpListeners = set() # type: set[MouseHandler]
  
  def remove(self, obj):
    obj.removeFromCell(None)
    
  def addMouseDownListener(self, cb:MouseHandler):
    self.mouseDownListeners.add(cb)
    
  def removeMouseDownListener(self, cb:MouseHandler):
    self.mouseDownListeners.remove(cb)

  def addMouseUpListener(self, cb:MouseHandler):
    self.mouseUpListeners.add(cb)
    
  def removeMouseUpListener(self, cb:MouseHandler):
    self.mouseUpListeners.remove(cb)

  def mouseDown(self, pos:Pos_t):
    for cb in self.mouseDownListeners :
      cb(pos)
      
  def mouseUp(self):
    for cb in self.mouseUpListeners :
      cb(pos)

  onMouseDown = addMouseDownListener
  onMouseUp = addMouseUpListener


