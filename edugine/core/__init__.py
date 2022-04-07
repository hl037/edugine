
import time
from collections import defaultdict
from threading import Thread
import numpy as np

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
    self.mouseDownListeners = []
    self.mouseUpListeners = []
    
  
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
      self.tick()
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

  def isClicked(self, pos:Pos_t = None):
    raise NotImplementedError()

  def addKeyDownListener(self, key:int|None, cb):
    self.keyDownListeners[key].append(cb)
    
  def removeKeyDownListener(self, key:int|None, cb):
    self.keyDownListeners[key].remove(cb)

  def onKeyDown(self, key:int):
    return lambda f: self.addKeyDownListener(key, f)
  
  def addKeyUpListener(self, key:int, cb):
    self.keyUpListeners[key].append(cb)
    
  def removeKeyUpListener(self, key:int, cb):
    self.keyUpListeners[key].remove(cb)

  def onKeyUp(self, key:int):
    return lambda f: self.addKeyUpListener(key, f)
  
  def addMouseDownListener(self, cb):
    self.mouseDownListeners.append(cb)
    
  def removeMouseDownListener(self, cb):
    self.mouseDownListeners.remove(cb)

  def onMouseDown(self):
    return lambda f: self.addMouseDownListener(f)
  
  def addMouseUpListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeMouseUpListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def onMouseUp(self):
    return lambda f: self.addMouseUpListener(f)
  
  def addTickListener(self, cb):
    self.mouseUpListeners.append(cb)
    
  def removeTickListener(self, cb):
    self.mouseUpListeners.remove(cb)

  def onTick(self):
    return lambda f: self.addTickListener(f)

  def tick(self):
    self.dispatchEvents()
    for t in self.tickListener :
      t()
      
  def dispatchEvents(self):
    raise NotImplementedError()
  
  def runInThread(self):
    self.thread = Thread(target=self.loop)
    self.thread.start()

  



