import sys
import math
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

class MyPicker(Qwt.QwtPicker):
    def __init__(self, parent):
        Qwt.QwtPicker.__init__(self, parent)

    def widgetMousePressEvent(self, event):
        self.emit(SIGNAL("MousePressed(const QMouseEvent&)"), event)
        Qwt.QwtPicker.widgetMousePressEvent(self, event)

    def widgetMouseReleaseEvent(self, event):
        self.emit(SIGNAL("MouseReleased(const QMouseEvent&)"), event)
        Qwt.QwtPicker.widgetMouseReleaseEvent(self, event)

    def widgetMouseDoubleClickEvent(self, event):
        self.emit(SIGNAL("MouseDoubleClicked(const QMouseEvent&)"), event)
        Qwt.QwtPicker.widgetMouseDoubleClickEvent(self, event)

    def widgetMouseMoveEvent(self, event):
        self.emit(SIGNAL("MouseMoved(const QMouseEvent&)"), event)
        Qwt.QwtPicker.widgetMouseMoveEvent(self, event)