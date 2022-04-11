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
  def __init__(self, controller:core.Controller, size = (800,600), caption:str=None, layout:LayoutItem=None):
    self.controller = controller
    controller.isKeyDown
    self.layout = layout
    super().__init__(*size, caption=caption, resizable=True)
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

  def on_mouse_press(self, x, y, buttons, modifiers):
    self.mou
    



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
    
    
