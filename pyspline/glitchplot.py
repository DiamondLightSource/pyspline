
#!/usr/bin/env python

# rawplot.py -- the raw plot class used for displaying raw data and
# the background. Has controls to adjust order of the background
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

from dataplot import *
#from QtBlissGraph import *
import calc
from time import time
        
class GlitchPlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.setWindowTitle("Glitch points")
        self.xdata=[]
        self.ydata=[]
        self.E0=0
        self.knot1=None
        self.knot2=None
        
        layout=QHBoxLayout()
        
        self.textLabel1 = QLabel(self)
        self.textLabel1.setText("Order of Background:")
        layout.addWidget(self.textLabel1)
        
        self.spinBox=QSpinBox(self)
        self.spinBox.setMaximumSize(QSize(50,25))
        self.spinBox.setValue(2)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(2)
        layout.addWidget(self.spinBox)

       
        spacer=QSpacerItem(100,10,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.red))
        self.plot.canvas().setMouseTracking(True)

        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.plot.replot()
        
        self.rawCurve=self.plot.insertCurve("raw data")
        self.plot.setCurvePen(self.rawCurve,QPen(QColor(Qt.black),2))
        
        self.backCurve=self.plot.insertCurve("background")
        self.plot.setCurvePen(self.backCurve,QPen(QColor(Qt.red),2))
        
        normDataLayout = QGridLayout()
        
        normDataLayout.addLayout(layout,0,0)
        normDataLayout.addWidget(self.plot,1,0)
        self.setLayout(normDataLayout)
        #QToolTip.add(self.spinBox,QString("Change Order of Background"))
        
        self.connect(self.plot,SIGNAL('signalUpdate()'),self.updatePlot)
        self.connect(self.spinBox,SIGNAL('valueChanged(int)'),self.updatePlot)
        
    def getSpinBoxValue(self):
            return self.spinBox.value()
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)
    
    def setRawData(self,xdata,ydata,E0):
        self.plot.setAxisScale(QwtPlot.xBottom,xdata[0],xdata[-1])
        self.plot.replot()
       
        self.plot.setCurveData(self.rawCurve,xdata,ydata)
        self.xdata=xdata
        self.ydata=ydata
        self.E0=E0
        DataPlot.setData(self.plot,xdata)
        self.plot.replot()
        

    def updatePlot(self,*args):
#    def calcBackground(self,xmin,xmax):
        print 't1',time()        
        order=self.getSpinBoxValue()+1 #need constant!
        
        temp=self.plot.knots[0].getPosition()
        xmin=calc.getClosest(temp,self.xdata)
        lindex=self.xdata.index(xmin)
        
        temp=self.plot.knots[1].getPosition()
        xmax=calc.getClosest(temp,self.xdata)
        hindex=self.xdata.index(xmax)
        print 't2',time()
        self.background=calc.calcBackground(self.xdata,self.ydata,lindex,hindex,order,self.E0)
        print 't3',time()        
        self.plot.setCurveData(self.backCurve,self.xdata,self.background)
        print 't3a',time()                
        ymax=max([max(self.ydata),max(self.background)])
        ymin=min([min(self.ydata),min(self.background)])
        print 't3b',time()                
        self.plot.setAxisScale(QwtPlot.yLeft,ymin,ymax)
        print 't3c',time()                
        self.plot.replot()        
        print 't3d',time()                         
        self.emit(SIGNAL('signalPlotChanged()'))
        print 't4',time()                

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=RawPlot()
    
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
    
    plot.setRawData(xdata,ydata,9200)
    #plot.plot.insertx1marker(xdata[1], 0.0, 'knot = 0')
    #plot.plot.insertx1marker(xdata[-1], 0.0, 'knot = 1')

    plot.plot.addKnot(xdata[0])
    plot.plot.addKnot(xdata[-1])
    
    #plot.updatePlot()
    plot.plot.canvas().setMouseTracking(True)
    plot.plot.replot() 
    
    plot.show()
    app.exec_()
    
