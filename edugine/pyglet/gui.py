import math
import pyglet

from .. import core
from ..core.gui import *

ui_group = pyglet.graphics.OrderedGroup(10)



class Label(LayoutItem):
  """
  A label class to print text
  """
  def __init__(self, text='', batch=None, group=ui_group, *args, **kwargs):
    self.label = pyglet.text.Label(text=text, batch=batch, group=group)
    super().__init__(*args, **kwargs)

  def setText(self, text):
    self.label.text = text

  def setGeometry(self, geometry:Geometry):
    self.label.update(*geometry[:2])
    self.label.width, self.label.height = geometry[2:]
    
    
