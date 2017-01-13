#!/usr/bin/env python

# kplot.py -- the KPlot class used for the kspace (xafs) window
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#from qt import *
#from qwt import *
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

from dataplot import *
        
class KPlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("XAFS Data")
    
        self.kdata=[]
        self.xafsdata=[]
        self.fixedknots=[]
        
        #spacer-plot-spacer
        layout=QHBoxLayout()
        
        self.textLabel1 = QLabel(self)
        self.textLabel1.setText("K-weight:")
        layout.addWidget(self.textLabel1)
        self.spinBox=QSpinBox(self)
        self.spinBox.setMaximumSize(QSize(50,25))
        self.spinBox.setValue(3)
        self.spinBox.setMinimum(0)
        self.spinBox.setMaximum(3)
        layout.addWidget(self.spinBox)

       
        spacer=QSpacerItem(100,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        
        
#        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
#        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.blue))
        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.plot.canvas().setMouseTracking(True)

        self.xafsCurve=self.plot.insertCurve("exafs")
        self.plot.setCurvePen(self.xafsCurve,QPen(QColor(Qt.black),2))

        rawLayout = QGridLayout()
        rawLayout.addLayout(layout,0,0)
        rawLayout.addWidget(self.plot,1,0)
        self.setLayout(rawLayout)
        self.status=QStatusBar(self)
        rawLayout.addWidget(self.status,3,0)
        self.connect(self.spinBox,SIGNAL('valueChanged(int)'),self.slotKWeightUpdate)

        
        #layout.addWidget(self.plot)
        
        #layout.addItem(spacer)
        
        #add everything to grid layout
        #spacer-spinboxes-plots-statusbar
        #normDataLayout = QGridLayout()
        #normDataLayout.addItem(spacer,0,0)
        #normDataLayout.addLayout(layout,2,0)
        #self.setLayout(normDataLayout)
        
        #self.connect(self.plot,SIGNAL('positionMessage()'),self.status.showMessage)
        
        self.setWindowTitle("EXAFS")

    def setXAFSData(self,kdata,xafsdata):
        
        self.plot.setAxisScale(QwtPlot.xBottom,0,kdata[-1]+0.5)
        self.plot.setCurveData(self.xafsCurve,kdata,xafsdata)
        self.kdata=kdata
        self.xafsdata=xafsdata
        DataPlot.setData(self.plot,kdata)
        
        self.plot.replot()
        
    def setXAFSData2(self,ydata,splinedata,kdata):
        kweight=self.spinBox.value()
        xafsdata1,xafsdata2=calc.calcXAFS2(ydata,splinedata,kdata,kweight)
        self.plot.setAxisScale(QwtPlot.xBottom,0,kdata[-1]+0.5)
        self.plot.setCurveData(self.xafsCurve,kdata,xafsdata2)
        self.kdata=kdata
        self.xafsdata=xafsdata1
        DataPlot.setData(self.plot,kdata)
        
        self.plot.replot()
        
        
    def slotKWeightUpdate(self):
        self.emit(SIGNAL('signalPlotChanged()'))        
        
    def clearFixedKnots(self):
        
        for knot in self.fixedknots:
            knot.detach()
            #self.plot.removeMarker(knot)
            
        self.fixedknots=[]
        
    def addFixedKnot(self,pos):
        
        kmarker=QwtPlotMarker()
        kmarker.setLineStyle(QwtPlotMarker.VLine)
        kmarker.setLinePen(QPen(QColor(Qt.darkGreen),2))
        kmarker.setXValue(pos)
        kmarker.setYValue(1.0)
        kmarker.attach(self.plot)
        self.fixedknots.append(kmarker)
    
    def closeEvent(self,e):
        self.hide()
        self.emit(SIGNAL("closed()"))

    def setShown(self,bool):
        if(bool):
            self.show()
        else:
            self.hide()
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=KPlot()
    
    xdata=[]
    ydata=[]
    file=open(sys.argv[1])
    
    line=file.readline()
    while(line):
        info=line.split()
        xdata.append(float(info[0]))
        ydata.append(float(info[1]))
        line=file.readline()
        
    file.close()
    
    plot.setXAFSData(xdata,ydata)
    plot.addFixedKnot(xdata[0]-0.01)
    plot.addFixedKnot(xdata[-1]+0.01)
    plot.plot.addKnot(xdata[0])
    plot.plot.addKnot(xdata[-1])
    
    plot.show()
    app.exec_()
    
