from ...core import Pos_t
import typing


MouseGridHandler = typing.Callable[[Pos_t], None]

class GridController(object):
  """
  A grid cell
  """
  def __init__(self):
    self.mouseDownListeners = set() # type: set[MouseGridHandler]
    self.mouseUpListeners = set() # type: set[MouseGridHandler]
  
  def remove(self, obj):
    obj.removeFromCell(None)
    
  def addMouseDownListener(self, cb:MouseGridHandler):
    self.mouseDownListeners.add(cb)
    return cb
    
  def removeMouseDownListener(self, cb:MouseGridHandler):
    self.mouseDownListeners.remove(cb)
    return cb

  def addMouseUpListener(self, cb:MouseGridHandler):
    self.mouseUpListeners.add(cb)
    return cb
    
  def removeMouseUpListener(self, cb:MouseGridHandler):
    self.mouseUpListeners.remove(cb)
    return cb

  def mouseDown(self, pos:Pos_t):
    for cb in self.mouseDownListeners :
      cb(pos)
      
  def mouseUp(self, pos:Pos_t):
    for cb in self.mouseUpListeners :
      cb(pos)

  onMouseDown = addMouseDownListener
  onMouseUp = addMouseUpListener


