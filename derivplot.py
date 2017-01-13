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
import calc
        
class DerivPlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("Derivative of Raw Data")
        self.xdata=[]
        self.ydata=[]
        self.background=[]
        self.E0=0
        self.knot1=None
        layout=QHBoxLayout()
        self.textLabel1 = QLabel(self)
        self.textLabel1.setText("Window Size:")
        layout.addWidget(self.textLabel1)
        self.spinBox=QSpinBox(self)
        self.spinBox.setMaximumSize(QSize(50,25))
        self.spinBox.setValue(5)
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(20)
        layout.addWidget(self.spinBox)
        spacer=QSpacerItem(100,10,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout.addItem(spacer)
        self.textLabel2 = QLabel(self)
        self.textLabel2.setText("Smoothing Method:")
        layout.addWidget(self.textLabel2)
        self.smoothComboBox=QComboBox(self)
        self.smoothComboBox.setEditable(0)

        for window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                self.smoothComboBox.addItem(window)
        layout.addWidget(self.smoothComboBox)
        
        self.textLabel3 = QLabel(self)
        self.textLabel3.setText("E0")
        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setEnabled(0)
        
        self.textLabel4 = QLabel(self)
        self.textLabel4.setText("Energy Offset")
        
        
        spacer=QSpacerItem(100,10,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.red))
        self.plot.canvas().setMouseTracking(True)

        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.plot.replot()
        
        self.rawCurve=self.plot.insertCurve("raw data")
        self.plot.setCurvePen(self.rawCurve,QPen(QColor(Qt.black),2))
        
        
        normDataLayout = QGridLayout()
        normDataLayout.addLayout(layout,0,0)
        normDataLayout.addWidget(self.plot,1,0)
        self.setLayout(normDataLayout)
        
        self.connect(self.plot,SIGNAL('signalUpdate'),self.updatePlot)
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
        
        order=self.getSpinBoxValue()+1 #need constant!
        
        temp=self.plot.knots[0].getPosition()
        xmin=calc.getClosest(temp,self.xdata)
        lindex=self.xdata.index(xmin)
        
        temp=self.plot.knots[1].getPosition()
        xmax=calc.getClosest(temp,self.xdata)
        hindex=self.xdata.index(xmax)
        
        self.background=calc.calcBackground(self.xdata,self.ydata,lindex,hindex,order,self.E0)
        
        self.plot.setCurveData(self.backCurve,self.xdata,self.background)
        ymax=max([max(self.ydata),max(self.background)])
        ymin=min([min(self.ydata),min(self.background)])
        self.plot.setAxisScale(QwtPlot.yLeft,ymin,ymax)
        self.plot.replot()
         
        self.emit(SIGNAL('signalPlotChanged'),())
        

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
    
