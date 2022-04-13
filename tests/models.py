#!/bin/python

from edugine.pyglet import *
from edugine.gridgame.pyglet import *
from edugine.gridgame.core.models import *

from icecream import ic

tests = []

@tests.append
def test1():
  cg = CellGrid.create((2,2), 3)
  ic(cg)
  pass

@tests.append
def test2():
  cg = CellGrid.create((2,2), 3)
  cg.TEST = 5
  ic(cg)
  ic(cg.TEST)
  ic(cg[0,0].TEST)
  pass


@tests.append
def test3():
  cg = CellGrid.create((2,2), 3)
  cg.TEST = 5
  ic(cg)
  ic(cg.TEST)
  ic(cg[0,0].TEST)
  pass

ic(sys.argv)

if len(sys.argv) >= 2 :
  id = int(sys.argv[1]) - 1
  assert (0 <= id < len(tests)),  'id should be less than {len(tests)}'
  tests[id]()
