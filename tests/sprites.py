#!/bin/python
from functools import wraps
from edugine.pyglet import *
from edugine.core.gui import *
from edugine.gridgame.core.models import *
from edugine.gridgame.pyglet import *


from icecream import ic

ctrl = Controller()

# class Window2(Window):
#   """
#   Mock Window without resize
#   """
#   def resze(self):
#     pass
# 
#   def on_draw(self):
#     pass
#     


def dbg(f):
  @wraps(f)
  def f_():
    try :
      return f()
    except :
      import pdb; pdb.xpm()
  return f


ref_holder = []


tests = []

  
@tests.append
def test1():
  window = pyglet.window.Window(800, 600, 'Test')
  l = pyglet.resource.Loader(['@PyAGame01.res'])
  t = l.image('Albert2.png')
  sprite = pyglet.sprite.Sprite(t)
  
  @window.event
  def on_draw():
    window.clear()
    sprite.draw()  

@tests.append
def test2():
  window = pyglet.window.Window(800, 600, 'Test')
  vp = VisualProvider(['@PyAGame01.res'])

  vis = Visual()
  vp.associateVisual('Albert2.png', vis)

  b = pyglet.graphics.Batch()

  sprite = vp.getSprite(vis, b)
  sprite.setGeometry((0,0,200,200))
  
  @window.event
  def on_draw():
    window.clear()
    b.draw()  

@tests.append
def test3():
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  vis = Visual()
  vp.associateVisual('Albert2.png', vis)


  ic(window.scene)
  sprite = vp.getSprite(vis, window.scene)
  sprite.setGeometry((0,0,200,200))
  
  ref_holder.append(sprite)

  sprite.x = 0
  sprite.y = 0
  pass
  
@tests.append
def test4():
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  vis = Visual()
  vp.associateVisual('Albert.png', vis)


  ic(window.scene)
  sprite = vp.getSprite(vis, window.scene)
  sprite.setGeometry((0,0,200,200))
  
  pass

@tests.append
def test5():
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis = Visual()
  at.associateVisual(2, 4, vis)
  sprite = vp.getSprite(vis, window.scene)
  sprite.setGeometry((0,0,200,200))

@tests.append
def test6():
  """
  GridCell
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis = Visual()
  at.associateVisual(2, 4, vis)

  gc = GridCellView(1., (32,32), (16,16), (Max, Max))

  gc.replaceSprites([vp.getSprite(vis, window.scene)])

  window.layout = gc


@tests.append
def test7():
  """
  GridCell
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  at.associateVisual(2, 4, vis1)
  at.associateVisual(0, 4, vis2)

  gc = GridCellView(1., (32,32), (16,16), (Max, Max))

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    gc.replaceSprites([vp.getSprite(vis1, window.scene)])
    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    gc.replaceSprites([vp.getSprite(vis2, window.scene)])

  window.layout = gc




@tests.append
def test8():
  """
  GridView and Grid(Model)
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  at.associateVisual(2, 4, vis1)
  at.associateVisual(0, 4, vis2)

  gm = Grid((2,1))
  gv = GridView(gm, vp, window.scene, 1., (32,32), (16,16), (Max, Max))

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    c = gm.cell(Pos(0,0))
    c.visuals = [vis1]
    c.update()
    c2 = c + Pos(1,0)
    c2.visuals = []
    c2.update()

    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    c = gm.cell(Pos(1,0))
    c.visuals = [vis2]
    c.update()
    c2 = c + Pos(-1,0)
    c2.visuals = []
    c2.update()

  window.layout = gv


@tests.append
def test9():
  """
  GridView and Grid(Model)
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  at.associateVisual(2, 4, vis1)
  at.associateVisual(0, 4, vis2)

  e = Entity()
  e.visuals = [vis1]

  gm = Grid((2,1))
  gv = GridView(gm, vp, window.scene, 1., (32,32), (16,16), (Max, Max))

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    e.cell = gm.cell(Pos(0,0))
    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    e.cell = gm.cell(Pos(1,0))

  window.layout = gv


@tests.append
def test10():
  """
  GridView and Grid(Model) and Entity
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  bg = Visual()
  fg = Visual()
  at.associateVisual(2, 4, vis1, z=2)
  at.associateVisual(0, 4, vis2, z=2)
  vp.associateVisual('grass.png', bg, z=0)
  vp.associateVisual('grass.png', fg, z=3)

  e = Entity()
  e.visuals = [vis1]

  gm = Grid((2,1))
  gv = GridView(gm, vp, window.scene, 1., (32,32), (16,16), (Max, Max))

  gm.cell(Pos(0,0)).visuals = [bg]
  gm.cell(Pos(1,0)).visuals = [fg]

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    e.cell = gm.cell(Pos(0,0))
    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    e.cell = gm.cell(Pos(1,0))

  window.layout = gv


@tests.append
def test11():
  """
  GridGame
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  bg = Visual()
  fg = Visual()
  at.associateVisual(2, 4, vis1, z=2)
  at.associateVisual(0, 4, vis2, z=2)
  vp.associateVisual('grass.png', bg, z=0)
  vp.associateVisual('grass.png', fg, z=3)

  e = Entity()
  e.visuals = [vis1]

  gm = Grid((2,1))
  gg = GridGame(
    gm,
    vp,
    window,
    1.,
    (32,32),
    (16,16),
    (Max, Max)
  )

  gm.cell(Pos(0,0)).visuals = [bg]
  gm.cell(Pos(1,0)).visuals = [fg]

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    e.cell = gm.cell(Pos(0,0))
    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    e.cell = gm.cell(Pos(1,0))

@tests.append
def test12():
  """
  GridGame
  """
  window = Window(ctrl)
  vp = VisualProvider(['@PyAGame01.res'])

  at = vp.loadAtlas('Albert.png', 4, 5)

  vis1 = Visual()
  vis2 = Visual()
  bg = Visual()
  fg = Visual()
  at.associateVisual(2, 4, vis1, z=2)
  at.associateVisual(0, 4, vis2, z=2)
  vp.associateVisual('grass.png', bg, z=0)
  vp.associateVisual('grass.png', fg, z=3)

  e = Entity()
  e.visuals = [vis1]

  gm = Grid((2,1))
  gg = GridGame(
    gm,
    vp,
    window,
    1.,
    (32,32),
    (16,16),
    (Max, Max)
  )

  gm.cell(Pos(0,0)).visuals = [bg]
  gm.cell(Pos(1,0)).visuals = [fg]

  gm.cell(Pos(0,0)).update()
  gm.cell(Pos(1,0)).update()

  @ctrl.onKeyDown(K.LEFT)
  def ev1(key):
    e.cell = gm.cell(Pos(0,0))
    
  @ctrl.onKeyDown(K.RIGHT)
  def ev2(key):
    e.cell = gm.cell(Pos(1,0))

  gg.infoL.setText('LEFT')
  gg.infoM.setText('MID')
  gg.infoR.setText('RIGHT')


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
    ctrl.runInThread()
  else :
    ctrl.run()
except :
  import pdb; pdb.xpm()
