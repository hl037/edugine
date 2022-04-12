import sys
import imp
import math
import pyglet
import pyglet.window.key as K
import pyglet.window.mouse as M
sys.modules['edugine.keyboard'] = K
sys.modules['edugine.mouse'] = M
M.ALL = M.LEFT & M.MIDDLE & M.RIGHT



from .. import core
from ..core.gui import LayoutItem




class Window(pyglet.window.Window):
  """
  A window
  """
  def __init__(self, controller:core.Controller, size = (800,600), caption:str='Edugine', scene=None, layout:LayoutItem=None):
    self.controller = controller
    super().__init__(*size, caption=caption, resizable=True)
    self.layout = layout
    if scene is None :
      scene = pyglet.graphics.Batch()
    self.scene = scene
    self.keys = K.KeyStateHandler()
    self.push_handlers(self.keys)
    self.controller.isKeyDown = self.isKeyDown

  @property
  def size(self):
    return self.get_size()
  
  @size.setter
  def size(self, val):
    self.set_size(*val)

  def on_resize(self, width, height):
    if self.layout :
      self.layout.setGeometry((0, 0, width, height))

  def on_key_press(self, symbol, modifiers):
    self.controller.keyDown(symbol)

  def on_key_release(self, symbol, modifiers):
    self.controller.keyUp(symbol)

  def isKeyDown(self, symbol):
    return self.keys[symbol]

  def on_mouse_press(self, x, y, button, modifiers):
    self.controller.mouseDown(Pos(x, y), button)

  def on_mouse_release(self, x, y, button, modifiers):
    self.controller.mouseUp(Pos(x, y), button)
    
  def setScene(self, scene:pyglet.graphics.Batch):
    self.scene = scene

  def on_draw(self):
    self.clear()
    if self.scene :
      self.scene.draw()

  @property
  def layout(self) -> LayoutItem:
    return self._layout
  
  @layout.setter
  def layout(self, val:LayoutItem):
    self._layout = val
    if val :
      self.set_minimum_size(*( x if x != gui.Max else 536870912 for x in self._layout.size_min))
      self.set_maximum_size(*( x if x != gui.Max else 536870912 for x in self._layout.size_max))



class Controller(core.Controller):
  """
  The pyglet main loop and controller.
  """
  def tick(self, due_time):
    super().tick(due_time)
    pyglet.clock.tick()

  def render(self):
    for window in pyglet.app.windows:
      window.switch_to()
      window.dispatch_events()
      window.dispatch_event('on_draw')
      window.flip()
    
    
