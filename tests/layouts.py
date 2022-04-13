#!/bin/python
import pyglet
from pyglet import shapes
from pyglet import gl
import pyglet.window.key as K
from edugine.pyglet import Controller
from edugine.core.gui import *
import numpy as np

import sys
from icecream import ic

window = pyglet.window.Window(960, 540, resizable=True)
batch = pyglet.graphics.Batch()

np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=500)

class DummyLayoutItem(LayoutItem):
  """
  
  """
  def __init__(self, color, batch, **kwargs):
    super().__init__(**kwargs)
    self.shape = shapes.Rectangle(0, 0, 0, 0, color=color, batch=batch)

  def setGeometry(self, geometry:tuple[int, int, int, int]):
    super().setGeometry(geometry)
    self.shape.x, self.shape.y, self.shape.width, self.shape.height = geometry
    
    
colors = [
(255,59,59), (255,149,0), (133,77,0), (194,150,89), (212,255,0), (116,133,31), (108,255,59), (115,194,89), (117,255,244), (61,133,127), (89,141,194), (21,0,255), (11,0,133), (98,89,194), (144,45,194), (133,0,99), (194,89,168), (133,31,48), (255,117,140)
]

items = []

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

tests = []

@tests.append
def test1():
  global items
  items = [ DummyLayoutItem(color=c, batch=batch) for c in colors[:4] ]
  for i, it in enumerate(items) :
    it.setGeometry((i * 50, 0, 50, 100))

@tests.append
def test2():
  global items
  items = [ DummyLayoutItem(color=c, batch=batch) for c in colors[:4] ]
  try :
    with L.batchUpdate() :
      for it in items :
        L.addItem(it)
    
    @window.event
    def on_resize(width, height):
      L.setGeometry((0, 0, width, height))
  except :
    import pdb; pdb.xpm()
    
@tests.append
def test3():
  global items
  items = [ DummyLayoutItem(color=c, batch=batch) for c in colors[:4] ]
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

@tests.append
def test4():
  global items
  items = [ DummyLayoutItem(color=c, batch=batch) for c in colors[:4] ]
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
  
@tests.append
def test5():
  global items
  w = 300
  h = 150
  item = DummyLayoutItem(
      color=colors[0],
      batch=batch,
      size_preferred=(w,h),
      size_max=(w,h),
      ratio_preferred = w/h,
      ratio_min = w/h,
      ratio_max = w/h,
  )
  c = ConstRatioContainer(item, (Alignment.MIDDLE, Alignment.MIDDLE))
  try :
    @window.event
    def on_resize(width, height):
      c.setGeometry((0, 0, width, height))

    @window.event
    def on_key_press(symbol, modifiers):
      h, v = c.alignment
      if symbol == K.RIGHT :
        c.alignment = min(2, h + 1), v
      elif symbol == K.LEFT :
        c.alignment = max(0, h - 1), v
      elif symbol == K.UP :
        c.alignment = h, min(2, v + 1)
      elif symbol == K.DOWN :
        c.alignment = h, max(0, v - 1)

  except :
    import pdb; pdb.xpm()

@tests.append
def test6():
  global items
  w = 300
  h = 150
  item = DummyLayoutItem(
      color=colors[0],
      batch=batch,
      size_preferred=(w,h),
      size_max=(w,h),
      ratio_preferred = w/h,
      ratio_min = w/h,
      ratio_max = w/h,
  )
  c = PaddingContainer(item)
  try :
    @window.event
    def on_resize(width, height):
      c.setGeometry((0, 0, width, height))

    @window.event
    def on_key_press(symbol, modifiers):
      if symbol == K.RIGHT :
        c.margin = (*c.margin[1:], c.margin[0])
      elif symbol == K.LEFT :
        c.margin = (c.margin[-1], *c.margin[:-1])
      elif symbol == K.NUM_0 :
        c.css = None
      elif symbol == K.NUM_1 :
        c.css = 10
      elif symbol == K.NUM_2 :
        c.css = 10, 20
      elif symbol == K.NUM_3 :
        c.css = 10, 20, 40
      elif symbol == K.NUM_4 :
        c.css = 10, 20, 40, 80
      elif symbol == K.NUM_5 :
        c.margin = 80, 40, 20, 10

  except :
    import pdb; pdb.xpm()

@tests.append
def test7():
  global items
  w = 300
  h = 150
  item = DummyLayoutItem(
      color=colors[0],
      batch=batch,
      size_preferred=(w,h),
      size_max=(w,h),
      ratio_preferred = w/h,
      ratio_min = w/h,
      ratio_max = w/h,
  )
  c = PaddingFracContainer(item)
  try :
    @window.event
    def on_resize(width, height):
      c.setGeometry((0, 0, width, height))

    @window.event
    def on_key_press(symbol, modifiers):
      if symbol == K.RIGHT :
        c.margin = (*c.margin[1:], c.margin[0])
      elif symbol == K.LEFT :
        c.margin = (c.margin[-1], *c.margin[:-1])
      elif symbol == K.NUM_0 :
        c.css = None
      elif symbol == K.NUM_1 :
        c.css = .10
      elif symbol == K.NUM_2 :
        c.css = .10, .20
      elif symbol == K.NUM_3 :
        c.css = .10, .20, .40
      elif symbol == K.NUM_4 :
        c.css = .05, .10, .20, .40
      elif symbol == K.NUM_5 :
        c.margin = .40, .20, .10, .05

  except :
    import pdb; pdb.xpm()



ic(sys.argv)

if len(sys.argv) >= 2 :
  id = int(sys.argv[1]) - 1
  assert (0 <= id < len(tests)),  'id should be less than {len(tests)}'
  tests[id]()

if len(sys.argv) >= 3 :
  t = sys.argv[2]
  assert t in ('t', 'l', 'p')
  p = (t == 'p')
  t = (t == 't')
else :
  p = False
  t = False


try :
  if p :
    pyglet.app.run()
  elif t :
    c.runInThread()
  else :
    c.loop()
except :
  import pdb; pdb.xpm()
  





