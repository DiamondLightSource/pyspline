#!/usr/bin/env python

# i0plot.py -- the I0Plot class used for displaying I0 data
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
from dataplot import *
        
class I0Plot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("I0 Data")
    
        #spacer-plot-spacer
        layout=QHBoxLayout()
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.black))
        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        layout.addWidget(self.plot)
        
        layout.addItem(spacer)
        
        #add everything to grid layout
        #spacer-spinboxes-plots-statusbar
        normDataLayout = QGridLayout()
        normDataLayout.addItem(spacer,0,0)
        normDataLayout.addLayout(layout,2,0)
        self.setLayout(normDataLayout)
        self.status=QStatusBar(self)
        normDataLayout.addWidget(self.status,3,0)
        
        #self.connect(self.plot,SIGNAL('positionMessage()'),self.status.showMessage())
        self.curve=self.plot.insertCurve("i0data")
        self.plot.setCurvePen(self.curve,QPen(QColor(Qt.black),2))
        

    def setI0Data(self,xdata,ydata):
        
        self.xdata=xdata
        self.ydata=ydata
        
        self.plot.setCurveData(self.curve,xdata,ydata)
        self.plot.setAxisScale(QwtPlot.xBottom,min(xdata),max(xdata))
        self.plot.replot()
        
    def closeEvent(self,e):
        self.hide()
        self.emit(SIGNAL("closed()"),())

    def setShown(self,bool):
        if(bool):
            self.show()
        else:
            self.hide()
        
    def __tr(self,s,c = None):
        return qApp.translate("IOData",s,c)

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=I0Plot()
    plot.show()
    app.exec_()
    
