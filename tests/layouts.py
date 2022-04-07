import pyglet
from pyglet import shapes
from pyglet import gl
from edugine.core.gui import VBoxLayout, HBoxLayout, LayoutItem
from edugine.pyglet import Controller
import numpy as np

window = pyglet.window.Window(960, 540, resizable=True)
batch = pyglet.graphics.Batch()

np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=500)

class DummyLayoutItem(LayoutItem):
  """
  
  """
  def __init__(self, color, batch):
    super().__init__()
    self.shape = shapes.Rectangle(0, 0, 0, 0, color=color, batch=batch)

  def setGeometry(self, geometry:tuple[int, int, int, int]):
    super().setGeometry(geometry)
    self.shape.x, self.shape.y, self.shape.width, self.shape.height = geometry
    
    
colors = [
(255,59,59), (255,149,0), (133,77,0), (194,150,89), (212,255,0), (116,133,31), (108,255,59), (115,194,89), (117,255,244), (61,133,127), (89,141,194), (21,0,255), (11,0,133), (98,89,194), (144,45,194), (133,0,99), (194,89,168), (133,31,48), (255,117,140)
]

items = [ DummyLayoutItem(color=c, batch=batch) for c in colors[:4] ]

L = HBoxLayout()


c = Controller()


@window.event
def on_draw():
  window.clear()
  batch.draw()

def update():
  window.switch_to()
  window.dispatch_events()
  window.dispatch_event('on_draw')
  window.flip()

def test1():
  for i, it in enumerate(items) :
    it.setGeometry((i * 50, 0, 50, 100))

def test2():
  try :
    with L.batchUpdate() :
      for it in items :
        L.addItem(it)
    
    @window.event
    def on_resize(width, height):
      L.setGeometry((0, 0, width, height))
  except :
    import pdb; pdb.xpm()
    
def test3():
  try :
    with L.batchUpdate() :
      for i, it in enumerate(items) :
        i += 1
        it.collapse = (i, i)
        it.expand = (i, i)
        L.addItem(it)
    
    @window.event
    def on_resize(width, height):
      L.setGeometry((0, 0, width, height))
  except :
    import pdb; pdb.xpm()

def test4():
  try :
    L2 = VBoxLayout()
    spacer = LayoutItem(size_preferred=(600, 400), collapse=(1, 1), expand=(10000, 10000))
    with L2.batchUpdate() :
      L2.addItem(spacer)
      with L.batchUpdate() :
        for i, it in enumerate(items) :
          i += 1
          it.collapse = (i, i)
          it.expand = (i, i)
          L.addItem(it)
      L2.addItem(L)
    
    @window.event
    def on_resize(width, height):
      L2.setGeometry((0, 0, width, height))
  except :
    import pdb; pdb.xpm()
  

test4()

c.runInThread()
#c.loop()



