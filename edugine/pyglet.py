import pyglet

from . import core
from .core.gui import LayoutItem



# class Window(core.View):
#   """
#   A window
#   """
#   def __init__(self, size = (800,600)):
#     super().__init__()
#     self.layout = None
#     self.size = size
# 
# 
    
    
class Controller(core.Controller):
  """
  The pyglet main loop and controller.
  """
  def tick(self):
    pyglet.clock.tick()

  def render(self):
    for window in pyglet.app.windows:
      window.switch_to()
      window.dispatch_events()
      window.dispatch_event('on_draw')
      window.flip()
    
    
