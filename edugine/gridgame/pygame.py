from pathlib import Path
from . import core
import pygame

pygame.init()

Cell = core.Cell

Feature = core.Feature

Entity = core.Entity

Pos = core.Pos

Grid = core.Grid

class Visual(core.Visual):
  """
  Visual implementation as pygame surface
  """
  def load(self, path:Path):
    self._cache = {}
    self._original = pygame.image.load(path)
    m = max(*self._original.get_size())
    self._size = m, m
    self._cache[m] = self._original

  def _get(self, size:int):
    if (im := self._cahce.get(size)) is not None :
      return im
    im = pygame.transform.smoothscale(self._original, (size, size))
    self._cache[size] = im
    return im
    

class View(core.View):
  """
  A Pygame implementation of a game
  """
  def __init__(self, win_w, win_h):
    self.screen = pygame.display.set_mode((win_w, win_h))
    


class Controller(core.Controller):
  """
  A pygame implementation of the controller
  """

  def __init__(self, view:View):
    super().__init__(view)
    self.keys_down = None
  
  def isKeyDown(self, key:int):
    if not self._keys_down :
      return False
    return self._keys_down[key]

  def isClicked(self, pos:Pos_t = None):
    raise NotImplementedError() #TODO

  def _dispatchKEYDOWN(self, event):
    k = event.key
    for cb in self.keyDownListeners[None]:
      cb(key)
    for cb in self.keyDownListeners[k]:
      cb(key)
      
  def _dispatchKEYUP(self, event):
    k = event.key
    for cb in self.keyUpListeners[None]:
      cb(key)
    for cb in self.keyUpListeners[k]:
      cb(key)

  def _dispatchMOUSEBUTTONDOWN(self, event):
    pass
    

  def dispatchEvents(self):
    self._keys_down = pygame.key.get_pressed()
      
    



    
