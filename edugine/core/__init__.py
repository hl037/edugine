
import time
import typing
from collections import defaultdict
from threading import Thread
import numpy as np

import edugine.mouse as M
import edugine.keyboard as K

class Pos_t(np.ndarray):
  """
  A position class that supports arithmetic operations
  """
  
  def __new__(
      subtype, shape=(2,), dtype=int, buffer=None, offset=0,
      strides=None, order=None
  ):
    assert dtype == int
    assert shape == (2,)
    return super().__new__(
      subtype, shape, dtype,
      buffer, offset, strides, order
    )
    
  @property
  def x(self):
    return self[0]
  
  @x.setter
  def x(self, val):
    self[0] = val

  @property
  def y(self):
    return self[1]
  
  @y.setter
  def y(self, val):
    self[1] = val

def Pos(x, y):
  p = Pos_t()
  p[:] = (x, y)
  return p

KeyboardHandler = typing.Callable[[int], None]
MouseHandler = typing.Callable[[Pos_t, int], None]
MouseMoveHandler = typing.Callable[[Pos_t, Pos_t, int], None] # Here for future

class Controller(object):
  """
  Class To handle all the inputs and the game loop
  """
  def __init__(self):
    self.tread = None
    self.fps = 60
    self.running = True
    self.keyDownListeners = defaultdict(default_factory=lambda : [])
    self.keyUpListeners = defaultdict(default_factory=lambda : [])
    self.tickListener = []
    self.mouseDownListeners = defaultdict(default_factory=lambda : [])
    self.mouseUpListeners = defaultdict(default_factory=lambda : [])
    self.cur_time = None
    
  
  @property
  def fps(self):
    return self._fps
  
  @fps.setter
  def fps(self, val):
    self._fps = val
    self._spf = 1 / val

  @property
  def spf(self):
    return self._spf
  
  @spf.setter
  def spf(self, val):
    self._spf = val
    self._fps = 1 / val

  def quit(self):
    self.running = False

  def loop(self):
    self.game_time = 0
    base = time.perf_counter()
    cur_time = base
    due_time = base + self._spf

    while self.running :
      self.tick(due_time - base)
      self.render()
      if cur_time < due_time :
        self.render()
        # else : lag
      cur = time.perf_counter()
      d = due_time - cur
      if d > 0 :
        time.sleep(d)
      due_time += self._spf
      self.game_time += self._spf

  def isKeyDown(self, key:int):
    raise NotImplementedError()

  # KeyDown
  def addKeyDownListener(self, key:int|None, cb:KeyboardHandler):
    self.keyDownListeners[key].append(cb)
    
  def removeKeyDownListener(self, key:int|None, cb:KeyboardHandler):
    self.keyDownListeners[key].remove(cb)

  def onKeyDown(self, key:int):
    return lambda f: self.addKeyDownListener(key, f)

  def keyDown(self, key:int):
    for cb in self.keyDownListeners[None] :
      cb(key)
    for cb in self.keyDownListeners[key] :
      cb(key)
  
  #KeyUp
  def addKeyUpListener(self, key:int, cb:KeyboardHandler):
    self.keyUpListeners[key].append(cb)
    
  def removeKeyUpListener(self, key:int, cb:KeyboardHandler):
    self.keyUpListeners[key].remove(cb)

  def onKeyUp(self, key:int):
    return lambda f: self.addKeyUpListener(key, f)
  
  def keyUp(self, key:int):
    for cb in self.keyUpListeners[None] :
      cb(key)
    for cb in self.keyUpListeners[key] :
      cb(key)
  
  # MouseDown
  def addMouseDownListener(self, buttons:int|None, cb:MouseboardHandler):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseDownListeners[b].append(cb)
    
  def removeMouseDownListener(self, buttons:int|None, cb:MouseboardHandler):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseDownListeners[b].discard(cb)

  def onMouseDown(self, buttons:int):
    return lambda f: self.addMouseDownListener(buttons, f)

  def mouseDown(self, button:int):
    for cb in self.mouseDownListeners[button] :
      cb(button)
  
  #MouseUp
  def addMouseUpListener(self, buttons:int, cb:MouseboardHandler):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseUpListeners[b].append(cb)
    
  def removeMouseUpListener(self, buttons:int, cb:MouseboardHandler):
    if buttons is None :
      buttons = M.ALL
    for b in (M.LEFT, M.RIGHT, M.LEFT) :
      if buttons & b :
        self.mouseUpListeners[b].discard(cb)

  def onMouseUp(self, buttons:int):
    return lambda f: self.addMouseUpListener(buttons, f)
  
  def mouseUp(self, buttons:int):
    for cb in self.mouseUpListeners[button] :
      cb(button)
  
  #Tick
  def addTickListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeTickListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def onTick(self):
    return lambda f: self.addTickListener(f)

  def tick(self, due_time:float):
    self.cur_time = due_time
    for t in self.tickListener :
      t(due_time)
      
  def dispatchEvents(self):
    raise NotImplementedError()
  
  def runInThread(self):
    self.thread = Thread(target=self.loop)
    self.thread.start()

  



