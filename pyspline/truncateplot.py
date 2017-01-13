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
        
class TruncatePlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("Truncate Raw Data")
        self.xdata=[]
        self.ydata=[]
        self.background=[]
        self.E0=0
        self.knot1=None
        self.knot2=None        
        layout=QHBoxLayout()
        self.textLabel1 = QLabel(self)
        self.textLabel1.setText("Lower Limit:")
        layout.addWidget(self.textLabel1)
        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setEnabled(0)
        layout.addWidget(self.lineEdit1)                
        spacer=QSpacerItem(100,10,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout.addItem(spacer)
        self.textLabel2 = QLabel(self)
        self.textLabel2.setText("Upper Limit:")
        layout.addWidget(self.textLabel2)
        self.lineEdit2 = QLineEdit(self)
        self.lineEdit2.setEnabled(0)
        layout.addWidget(self.lineEdit2)        
        
        self.plot = DataPlot(QColor(Qt.red))
        self.plot.canvas().setMouseTracking(True)

        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.plot.replot()
        
        self.rawCurve=self.plot.insertCurve("raw data")
        self.plot.setCurvePen(self.rawCurve,QPen(QColor(Qt.black),2))
        
        normDataLayout = QGridLayout()
        normDataLayout.addLayout(layout,0,0)
        normDataLayout.addWidget(self.plot)
        self.setLayout(normDataLayout)
        #QToolTip.add(self.spinBox,QString("Change Order of Background"))
        
        self.connect(self.plot,SIGNAL('signalUpdate()'),self.updatePlot)
        
        
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
        myknots=self.plot.knots
        self.lineEdit1.setText(str(myknots[0].getPosition()))
        self.lineEdit2.setText(str(myknots[1].getPosition()))

        self.plot.replot()
        
        
    def updatePlot(self,*args):
        self.plot.replot()        
        self.emit(SIGNAL('signalPlotChanged()'))
        myknots=self.plot.knots
        if(len(myknots)>0):
                print myknots[0].getPosition(),myknots[1].getPosition()
        self.lineEdit1.setText(str(myknots[0].getPosition()))
        self.lineEdit2.setText(str(myknots[1].getPosition()))

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=TruncatePlot()
    
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
    
