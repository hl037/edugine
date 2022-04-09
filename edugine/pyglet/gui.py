import math
import pyglet

from .. import core
from ..core.gui import LayoutItem, Geometry

ui_group = pyglet.graphics.OrderedGroup(10)



class Window(pyglet.window.Window, LayoutItem):
  """
  A window...
  """
  def __init__(self, size, resizable, caption='Edugine', min_size=None, max_size=None):
    super().__init__(*size, caption=caption, resizable=resizable)
    self.layout = None # type: LayoutItem
    self.scene = None # type: pyglet.graphics.Batch
    if min_size :
      self.set_minimum_size(*min_size)
    else :
      min_size = (0,0)
    if max_size :
      self.set_maximum_size(*max_size)
    else :
      max_size = (math.inf, math.inf)
    LayoutItem.__init__(self, size_preferred=size, size_min=min_size, size_max=max_size)
    self.setGeometry((*self.get_location(), *self.get_size()))

  def setGeometry(self, geometry:Geometry):
    self.set_location(*geometry[:2])
    self.set_size(*geometry[2:])
    if self.layout :
      self.layout.setGeometry((0, 0, *geometry[2:]))

  def setScene(self, scene:pyglet.graphics.Batch):
    self.scene = scene

  def on_draw(self):
    self.clear()
    self.scene.draw()

  def on_resize(self, width, height):
    self.layout.setGeometry((0, 0, width, height))

  

class Label(pyglet.text.Label, LayoutItem):
  """
  A label class to print text
  """
  def __init__(self, text='', batch=None, *args, **kwargs):
    super().__init__(text=text, batch=batch, group=ui_group)
    LayoutItem.__init__(self, *args, **kwargs)

  def setText(self, text):
    self.text = text

  def setGeometry(self, geometry:Geometry):
    self.set_location(*geometry[:2])
    self.set_size(*geometry[2:])
    
    
