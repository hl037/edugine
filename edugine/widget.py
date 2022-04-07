
class MouseArea(object):
  """
  Class that handles mouse events
  """
  def __init__(self, parent:'MouseArea'):
    self._mask = None
    self._parent = None
    self._geometry = None
    self._trackMouse = False

  def recomputeMask(self):
    """
    Recompute the mask relative to parent bounding box (Called on geometry change and as needed)
    """
    pass

  def render(self):
    """
    Render the widget image (called once a frame)
    """
    pass

  def mousePressEvent(self):
    """
    Called when a button is pressed in the widget
    """
    pass

  def mouseMoveEvent(self):
    """
    Called when a mousePressEvent has been receive until its correspounding mouseReleaseEvent is called
    """
    pass

  def mouseReleaseEvent(self):
    """
    Always called in pair with mousePressEvent
    """
    pass


