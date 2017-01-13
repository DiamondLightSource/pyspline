# knot.py -- a subclass of QwtPlotMarker that allows it to have 
#             boundaries and other useful attributes while dragging
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

#from qt import *
#from qwt import *

class Knot(QwtPlotMarker):
    def __init__(self,pos,color,*args):
        QwtPlotMarker.__init__(self)
        self.setLineStyle(QwtPlotMarker.VLine)
        self.setLinePen(QPen(QColor(color),2))
        self.setXValue(pos)
        self.setYValue(1.0)
        self.range=[pos-1,pos+1]
        self.lock=False

    def setColor(self,color):
        self.setLinePen(QPen(QColor(color),2))
        
    def setPosition(self,pos):
        self.setXValue(pos)
        
    def getPosition(self):
        return self.xValue()
        
    def setBoundary(self,min,max):
        self.range[0]=min
        self.range[1]=max
    
    def getBoundary(self):
        return self.range
    
    def setLock(self,state):
        self.lock=state
        
    def isLocked(self):
        return self.lock
        
