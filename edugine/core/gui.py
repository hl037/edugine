import math
import dataclasses
from dataclasses import dataclass, fields
from enum import Enum, IntEnum
from contextlib import contextmanager

import scipy.optimize as optim
import numpy as np

from icecream import ic

Max = math.inf
Min = 0

def div(a, b):
  if b == 0 :
    return Max if a >= 0 else Min
  else :
    return a / b

Geometry = tuple[int, int, int, int]

@dataclass
class _LayoutItem(object):
  """
  Base class to provide init
  """
  ratio_min: float = Min
  ratio_max: float = Max
  ratio_preferred: float = None
  size_min : tuple[int, int] = (Min,Min)
  size_max : tuple[int, int] = (Max,Max)
  size_preferred : tuple[int, int] = (200,100)
  collapse : tuple[int, int] = (1,1)
  expand : tuple[int, int] = (1,1)
  geometry : Geometry = (0,0,0,0)


class Alignment(IntEnum):
  """
  Alignment in a container
  """
  BEGIN = 0
  MIDDLE = 1
  END = 2
  LEFT = BEGIN
  RIGHT = END
  BOTTOM = BEGIN
  TOP = END
    
  
class LayoutItem(_LayoutItem):
  """
  A Layout item that has properties to tell the layout its preferred geometry
  """
  def __init__(self, *args, **kwargs):
    self._update = 0
    super().__init__(*args, **kwargs)
    self._parent = None # type: LayoutItem
    if self.ratio_preferred is None :
      self.ratio_preferred = div(*self.size_preferred)

  def setGeometry(self, geometry:Geometry):
    """
    Sets the geometry of this item, and of its children
    """
    self.geometry = geometry

  @contextmanager
  def batchUpdate(self):
    self._update += 1
    yield
    self._update -= 1
    self.update()

  def updateLayout(self):
    pass

  def update(self):
    if self._update :
      return
    self.updateLayout()
    if self.parent :
      self.parent.update()
    elif self.geometry != (0,0,0,0) :
      self.setGeometry(self.geometry) # Recompute the layout if it has a geometry...

  @property
  def parent(self) -> 'LayoutItem':
    return self._parent
  
  @parent.setter
  def parent(self, n_parent:'LayoutItem'):
    if self._parent :
      self._parent.removeItem(self)
    self._parent = n_parent

  def removeItem(self, it:'LayoutItem'):
    assert it._parent == self
    it._parent = None




class BoxLayout(LayoutItem):
  #TODO changer les coefficients pour 1/x
  #TODO inverser l'ordre en vertical...
  """
  A box layout that tries to best match the constraint for a row or a column of items
  """

  a0 = 0
  a1 = 1

  def __init__(self):
    super().__init__()
    self.items = [] # type: list[LayoutItem]

  def __init_subclass__(cls):
    super().__init_subclass__()
    if cls.a0 == 0 :
      cls._s1_for_s0 = cls._s1_for_s0_h
      cls._s0_for_s1 = cls._s1_for_s0_v
      cls._get_ratio_min = cls._get_ratio_min_h
      cls._get_ratio_max = cls._get_ratio_min_v
      cls._set_ratio_preferred = cls._set_ratio_preferred_h
      cls._ratio_min = cls._ratio_min_h
      cls._ratio_max = cls._ratio_max_h
    else :
      cls._s1_for_s0 = cls._s1_for_s0_v
      cls._s0_for_s1 = cls._s1_for_s0_h
      cls._get_ratio_min = cls._get_ratio_min_v
      cls._get_ratio_max = cls._get_ratio_min_h
      cls._set_ratio_preferred = cls._set_ratio_preferred_v
      cls._ratio_min = cls._ratio_min_v
      cls._ratio_max = cls._ratio_max_v

  def __getitem__(self, k):
    return self.items.__getitem__(k)

  def __setitem__(self, k, v:LayoutItem):
    v.parent = self
    self.items.__setitem__(k, v)
    self._update()

  def __delitem__(self, k):
    self.items.__delitem__(k)

  def addItem(self, it:LayoutItem, pos=None, update=True):
    if pos is None :
      self.items.append(it)
    else :
      self.items.insert(pos, it)
    if update :
      self.update()

  def removeItem(self, it:LayoutItem, update=True):
    super().removeItem(it)
    pos = self.items.remove(it)
    if update :
      self.update()

  def _update_size_min_max(self):
    a0, a1 = self.a0, self.a1
    min_size = sum( x.size_min[a0] for x in self.items ), max( x.size_min[a1] for x in self.items )
    max_size = sum( x.size_max[a0] for x in self.items ), min( x.size_max[a1] for x in self.items )
    if min_size[0] > max_size[0] :
      min_size = (0  , min_size[1])
      max_size = (Max, max_size[1])
    if min_size[1] > max_size[1] :
      min_size = (min_size[0], 0  )
      max_size = (max_size[0], Max)
    self.min_size = min_size[a0], min_size[a1]
    self.max_size = max_size[a0], max_size[a1]


  def _update_ratio_min_max(self):
    a0, a1 = self.a0, self.a1
    s1_max_for_s0_min = min(self.size_max[a1], min( self._s1_for_s0(it.size_min[a0], self._get_ratio_min(it)) for it in self.items ))
    s0_max_for_s1_min = sum( min(it.size_max[a0], self._s0_for_s1(it.size_min[a1], self._get_ratio_max(it))) for it in self.items )
    self._ratio_min = self.min_size[a0], s1_max_for_s0_min
    self._ratio_max = s0_max_for_s1_min, self.min_size[a1]

  def _compute_size_preferred_0(self):
    a0, a1 = self.a0, self.a1
    N = len(self.items)
    coefs = np.concatenate(([0], [ it.expand[a1] for it in self.items ], [ it.collapse[a1] for it in self.items ]), dtype=float)
    C1 = np.divide(1, coefs, out=np.zeros_like(coefs), where=coefs!=0)
    C1[coefs == 0] = 1000000
    C1[0] = 0
    A1_eq = np.zeros((N, coefs.shape[0]), dtype=float)
    B1_eq = np.array([ it.size_preferred[a1] for it in self.items ])
    for i in range(N) :
      A1_eq[i, 0] = 1
      A1_eq[i, i + 1] = -1
      A1_eq[i, N + i + 1] = 1
    bounds1 = [(0, None)] + [
      (0, it.size_max[a1] - it.size_preferred[a1] if not math.isfinite(it.size_max[a1]) else None)
      for it in self.items
    ] + [
      (0, it.size_preferred[a1] - it.size_min[a1])
      for it in self.items
    ]
    res = optim.linprog(C1, A_eq=A1_eq, b_eq=B1_eq, bounds=bounds1, method='simplex')
    if res.status != 0 :
      res = optim.linprog(C1, A_eq=A1_eq, b_eq=B1_eq, method='simplex') #Retry without bound...
      assert res.status != 0
    return round(res.x[0])
  
  def _update_size_preferred(self, p1):
    a0, a1 = self.a0, self.a1
    p = sum(
      (
        v if p <= (v := self.size_min[a0]) else
        v if p >= (v := self.size_max[a0]) else
        v if p <= (v := (self._s0_for_s1(p1, self._get_ratio_min(it)))) else
        v if p >= (v := (self._s0_for_s1(p1, self._get_ratio_max(it)))) else
        p
      )
      for p, it in ( (self._s0_for_s1(p1, it.ratio_preferred), it) for it in self.items )
    ), p1
    self.size_preferred = p[a0], p[a1]
    self._set_ratio_preferred(*p)


  def updateLayout(self):
    self._update_size_min_max()
    self._update_ratio_min_max()
    self._update_size_preferred(self._compute_size_preferred_0())

  def _share_space(self, space, X, A, B, C):
    #ic(space, X, A, B, C)
    Cnorm = C[A] * X[A]
    Cnorm /= np.sum(Cnorm, axis=0)
    X[A] += space * Cnorm
    if space < 0 :
      Bmask = X < B
    else :
      Bmask = X > B
    r = np.sum(X[Bmask] - B[Bmask])
    X[Bmask] = B[Bmask]
    A &= ~Bmask
    return A, r

  def _round_maintain_sum(self, X:np.ndarray):
    s = int(round(np.sum(X)))
    nX = np.round(X)
    ns = int(round(np.sum(nX)))
    wrong = ns - s
    if wrong != 0 :
      Ind = np.argsort(nX - X)
      if wrong < 0 :
        nX[Ind[wrong:]] += 1
      else :
        nX[Ind[:wrong]] += 1
    return nX.astype(int)

  def setGeometry(self, geometry:Geometry):
    """
    Actually perform the layout
    """
    #ic('Set geometry')
    #ic(geometry)
    a0, a1 = self.a0, self.a1
    N = len(self.items)
    s0, s1, l0, l1 = geometry[a0], geometry[a1], geometry[2 + a0], geometry[2 + a1]
    super().setGeometry(geometry)
    #coefs = np.concatenate(([0] * len(self.items), [ it.expand[a0] for it in self.items ], [ it.collapse[a0] for it in self.items ]), dtype=float)
    X = np.array([ self._s0_for_s1(l1, it.ratio_preferred) for it in self.items ])
    wanted = np.sum(X)
    space = l0 - wanted
    if space < 0 :
      C = np.array([ it.collapse[a0] for it in self.items ], dtype=float)
      B = np.array([ it.size_min[a0] for it in self.items ], dtype=float)
    else :
      C = np.array([ it.expand[a0] for it in self.items ], dtype=float)
      B = np.array([ it.size_max[a0] for it in self.items ], dtype=float)
    A = np.ones_like(C, dtype=bool)

    while not math.isclose(space, 0) :
      if not A.any() :
        if space < 0 :
          B = np.full_like(B, .0)
        else :
          B = np.full_like(B, Max)
      A, space = self._share_space(space, X, A, B, C)
    # ic('Layed out')
    # ic(X)
    X = self._round_maintain_sum(X)
    # ic(X)

    # C0 = np.divide(1, coefs, out=np.zeros_like(coefs), where=coefs!=0)
    # C0[coefs == 0] = 1000000
    # C0[:len(self.items)] = 0
    # A0_eq = np.zeros((len(self.items) + 1, coefs.shape[0]), dtype=float)
    # B0_eq = np.array([
    #   (
    #     v if p <= (v := it.size_min[a0]) else
    #     v if p >= (v := it.size_max[a0]) else
    #     p
    #   )
    #   for p, it in ( (self._s0_for_s1(l1, it.ratio_preferred), it) for it in self.items )
    # ] + [l0])
    # for i in range(len(self.items)) :
    #   A0_eq[i, i] = 1
    #   A0_eq[i, N + i] = 1
    #   A0_eq[i, 2 * N + i] = -1
    # A0_eq[-1, :N] = 1
    # bounds0 = [
    #   (
    #     it.size_min[a0], v if (v := it.size_max[a0]) != Max else None
    #   )
    #   for it in self.items
    # ] + [ (0, None) ] * (2 * N)
    # res = optim.linprog(C0, A_eq=A0_eq, b_eq=B0_eq, bounds=bounds0, method='simplex')
    # if res.status != 0 :
    #   res = optim.linprog(C0, A_eq=A0_eq, b_eq=B0_eq, method='simplex') #Retry without bound...
    #   assert res.status != 0
    base_geo = [0, 0, 0, 0]
    base_geo[a1] = s1
    base_geo[2 + a1] = l1
    for it, x in zip(self.items, X) :
      base_geo[2 + a0] = x
      it.setGeometry(tuple(base_geo))
      base_geo[a0] += x

  def _s1_for_s0(self, s0, r) -> float:
    raise NotImplementedError()
  
  def _s0_for_s1(self, s1, r) -> float:
    raise NotImplementedError()

  def _get_ratio_min(self, it):
    raise NotImplementedError()
  
  def _get_ratio_max(self, it):
    raise NotImplementedError()

  def _s1_for_s0_h(self, s0, r):
    return div(s0, r)
  
  def _s1_for_s0_v(self, s0, r):
    return s0 * r
  
  def _get_ratio_min_h(self, it):
    return it.ratio_min
  
  def _get_ratio_min_v(self, it):
    return it.ratio_max

  def _set_ratio_preferred(self, p0, p1):
    raise NotImplementedError()
  
  def _set_ratio_preferred_h(self, p0, p1):
    self.ratio_preferred = div(p0, p1)
  
  def _set_ratio_preferred_v(self, p0, p1):
    self.ratio_preferred = div(p1, p0)

  @property
  def _ratio_min(self):
    raise NotImplementedError()
  
  @property
  def _ratio_max(self):
    raise NotImplementedError()
  
  @property
  def _ratio_min_h(self):
    return self.ratio_min
  
  @_ratio_min_h.setter
  def _ratio_min_h(self, val):
    self.ratio_min = div(val[0], val[1])
    
  @property
  def _ratio_max_h(self):
    return self.ratio_max
  
  @_ratio_min_h.setter
  def _ratio_max_h(self, val):
    self.ratio_max = div(val[0], val[1])

  @property
  def _ratio_min_v(self):
    self.ratio_max = val
  
  @_ratio_min_v.setter
  def _ratio_min_v(self, val):
    self.ratio_max = div(val[1], val[0])
    
  @property
  def _ratio_max_v(self):
    self.ratio_min = val
  
  @_ratio_min_v.setter
  def _ratio_max_v(self, val):
    self.ratio_min = div(val[1], val[0])



class HBoxLayout(BoxLayout):
  a0 = 0
  a1 = 1


class VBoxLayout(BoxLayout):
  a0 = 1
  a1 = 0


class ConstRatioContainer(LayoutItem):
  """
  A layout item that can safely handle an item with a constant w/h ratio.
  """
  def __init__(self, item:LayoutItem, alignment=(Alignment, Alignment)):
    self.item = item
    item.parent = self
    self._alignment = alignment
    self.updateLayout()

  def updateLayout(self):
    d = dataclasses.asdict(self.item)
    d['ratio_min'] = 0
    d['ratio_max'] = Max
    d['geometry'] = self.geometry
    LayoutItem.__init__(self, **d)

  def _align(self, direction, size):
    """
    direction = 0 -> horizontal
    direction = 1 - vertival
    """
    if self.alignment[direction] == Alignment.BEGIN :
      return self.geometry[direction]
    elif self.alignment[direction] == Alignment.END :
      return self.geometry[direction] + self.geometry[2+direction] - size
    else :
      return self.geometry[direction] + (self.geometry[2+direction] - size) // 2

  def setGeometry(self, geometry:Geometry):
    super().setGeometry(geometry)
    self_ratio = div(*self.geometry[2:])
    if self_ratio < self.item.ratio_min :
      # bound by width, extra height
      if self.geometry[2] > self.item.size_max[0] :
        # extra width too...
        w = self.item.size_max[0]
      else :
        w = self.geometry[2]
      h = min(w / self.item.ratio_min, self.item.size_max[1])
    elif self_ratio > self.item.ratio_max :
      # bound by height, extra width
      if self.geometry[3] > self.item.size_max[1] :
        # extra height too...
        h = self.item.size_max[1]
      else :
        h = self.geometry[3]
      w = min(h * self.item.ratio_min, self.item.size_max[0])
    else :
      w = min(geometry[2], self.item.size_max[0])
      h = min(geometry[3], self.item.size_max[1])
    w = round(w)
    h = round(h)
    self.item.setGeometry(( self._align(0, w), self._align(1, h), w, h))
  
  @property
  def alignment(self):
    return self._alignment

  @alignment.setter
  def alignment(self, val):
    self._alignment = val
    self.update()
    



