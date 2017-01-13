#!/usr/bin/env python
# normplot.py -- the NormPlot class used for displaying normalized data
#    and the spline. Has widgets to control number of knots and order of segments
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004
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
from time import time
from dataplot import *
import calc

class NormSpin(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        
        self.orders=[]
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.textLabel1 = QLabel(self)
        self.layout.addWidget(self.textLabel1)

        #set up spin box that controls number of knots
        self.spinBox1 = QSpinBox(self)
        self.spinBox1.setMaximumSize(QSize(50,25))
        self.spinBox1.setMaximum(10)
        self.spinBox1.setMinimum(2)
        self.spinBox1.setValue(3)
        self.layout.addWidget(self.spinBox1)
        
        #QToolTip.add(self.spinBox1,QString("Change the number of spline points"))
        
        #spacer between knots and orders
        self.spacer = QSpacerItem(21,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.layout.addItem(self.spacer)
        
        self.textLabel2 = QLabel(self)
        self.layout.addWidget(self.textLabel2)
        
        #QToolTip.add(self.textLabel2,QString("Adjust the orders of the polynomial\nsegments of the spline"))

        #set up spin boxes that control orders, and set default value
        spinBox2 = QSpinBox(self)
        spinBox2.setMaximumSize(QSize(50,25))
        spinBox2.setMaximum(3)
        spinBox2.setMinimum(2)
        spinBox2.setValue(3)
        self.layout.addWidget(spinBox2)
        self.orders.append(spinBox2)
        self.connect(spinBox2,SIGNAL('valueChanged(int)'),self.slotKnotUpdate)
        
        #connect slots
        self.connect(self.spinBox1,SIGNAL('valueChanged(int)'),self.slotNumKnotsChanged)
        
        self.languageChange()
        
    def slotNumKnotsChanged(self,val):
        val=val-1 #segments = knots -1
        if(val==len(self.orders)+1):
            spinBox2 = QSpinBox(self)
            spinBox2.setMaximumSize(QSize(50,25))
            spinBox2.setMaximum(3)
            spinBox2.setMinimum(2)
            spinBox2.setValue(3)
            self.layout.addWidget(spinBox2)
            spinBox2.show()
            self.orders.append(spinBox2)
            self.connect(spinBox2,SIGNAL('valueChanged(int)'),self.slotKnotUpdate)
            
            
        elif(val==len(self.orders)-1):
            spinBox=self.orders.pop()
            spinBox.hide()
        self.emit(SIGNAL('signalNumKnotsUpdate()'))
        
        #should only happen at start
        #else:
        #    print "number not expected"
    def initializeSlots(self):
        
        for spinBox in self.orders:
            self.connect(spinBox,SIGNAL('valueChanged(int)'),self.slotKnotUpdate)
            
    def slotKnotUpdate(self,*args):
        
        self.emit(SIGNAL('signalKnotsUpdate()'))
        
    def getOrders(self):
        return self.orders
    
    def setNumKnots(self,value):
    
        while(len(self.orders)>0):
            spinBox=self.orders.pop()
            spinBox.hide()
            
        for i in range(value-1):
            spinBox=QSpinBox(self)
            spinBox.setMaximumSize(QSize(50,25))
            spinBox.setMaximum(3)
            spinBox.setMinimum(2)
            spinBox.setValue(3)
            self.layout.addWidget(spinBox)
            spinBox.show()
            self.orders.append(spinBox)
            
        self.spinBox1.setValue(value)
            
    def setOrders(self,orders):
    
        for i in range(len(self.orders)):
            self.orders[i].setValue(orders[i])
            
    
    def languageChange(self):
        self.textLabel1.setText(self.__tr("# of Knots:"))
        self.textLabel2.setText(self.__tr("Order of Segments:"))

    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)
        
class NormPlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("Normalized Data")
        
        self.xdata=[]
        self.ydata=[]
        self.spline=[]
        
        #spacer-spinboxes-spacer
        layout=QHBoxLayout()
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
            
        self.spinBoxes=NormSpin(self)
        layout.addWidget(self.spinBoxes)
        
        layout.addItem(spacer)
    
        #spacer-plot-spacer
        layout2=QHBoxLayout()
        
        layout2.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.darkGreen))
        
        self.plot.setAxisScale(QwtPlot.xBottom,0,100)
        layout2.addWidget(self.plot)
        
        self.normCurve=self.plot.insertCurve("norm")
        self.plot.setCurvePen(self.normCurve,QPen(QColor(Qt.black),2))
        
        self.splineCurve=self.plot.insertCurve("spline")
        self.plot.setCurvePen(self.splineCurve,QPen(QColor(Qt.darkGreen),2))
        
        layout2.addItem(spacer)
        self.plot.canvas().setMouseTracking(True)
        #add everything to grid layout
        #spacer-spinboxes-plots-statusbar
        normDataLayout = QGridLayout()
        normDataLayout.addItem(spacer,0,0)
        normDataLayout.addLayout(layout,1,0)
        normDataLayout.addLayout(layout2,2,0)
        self.setLayout(normDataLayout)
        self.status=QStatusBar(self)
        normDataLayout.addWidget(self.status,3,0)
        self.connect(self.plot,SIGNAL('signalUpdate()'),self.updatePlot)


        #self.clearWState(Qt.WState_Polished)
    def initializeSlots(self):
        
        #self.connect(self.plot,SIGNAL('positionMessage'),self.status.message)
        self.connect(self.plot,SIGNAL('signalUpdate()'),self.updatePlot)
        self.connect(self.spinBoxes,SIGNAL('signalKnotsUpdate()'),self.updatePlot)
        self.connect(self.spinBoxes,SIGNAL('signalNumKnotsUpdate()'),self.updateKnots)
        self.spinBoxes.initializeSlots()
        
    def updateKnots(self):
        
        min=self.plot.knots[0].getPosition()
        max=self.plot.knots[-1].getPosition()
        
        kmin=calc.toKSpace(min,self.E0)
        kmax=calc.toKSpace(max,self.E0)
        
        self.plot.resetPlot()
        size=self.spinBoxes.spinBox1.value()
        
        div=(kmax-kmin)/(size-1)
        
        self.plot.addKnot(min)
        self.plot.addBoundsExceptions(0,0,self.E0)
        
        for i in range(1,size-1):
            temp=calc.fromKSpace(kmin+i*div,self.E0)
            temp2=calc.getClosest(temp,self.xdata)
            self.plot.addKnot(temp2)
            
        self.plot.addKnot(max)
        
        #self.normCurve=self.plot.insertCurve("norm")
        self.plot.setCurvePen(self.normCurve,QPen(QColor(Qt.black),2))
        
        #self.splineCurve=self.plot.insertCurve("spline")
        self.plot.setCurvePen(self.splineCurve,QPen(QColor(Qt.darkGreen),2))
        
        self.updatePlot()
        
    def getOrders(self):
        return self.spinBoxes.getOrders()
    
    def setOrders(self,orders):
        self.spinBoxes.setOrders(orders)
        
    def setE0(self,E0):
        self.E0=E0
        
    def setNumKnots(self,value):
        self.spinBoxes.setNumKnots(value)
        
    def getNumKnotsBox(self):
        return self.spinBoxes.spinBox1
        
    def setNormData(self,xdata,ydata,E0):
        #self.plot.setCurveData(self.normCurve,xdata,ydata)
        self.xdata=xdata
        self.ydata=ydata
        self.E0=E0
        DataPlot.setData(self.plot,xdata)
        self.plot.setAxisScale(QwtPlot.xBottom,xdata[0],xdata[-1])
        self.plot.replot()
        
    def updatePlot(self,*args):
        segs=self.getSegs()
        if(len(segs)==0):
            return
        segs=self.getSegs()
        tempspline,sp_E0=calc.calcSpline(self.xdata,self.ydata,self.E0,segs)
        self.normdata=[]
        self.splinedata=[]
        for i in range(len(self.ydata)):
            self.normdata.append(self.ydata[i]/sp_E0)
            self.splinedata.append(tempspline[i]/sp_E0)
        self.plot.setCurveData(self.normCurve,self.xdata,self.normdata)
        self.plot.setCurveData(self.splineCurve,self.xdata,self.splinedata)
        self.plot.replot()
        self.emit(SIGNAL('signalPlotChanged()'))
        
    def getSegs(self):
        
        knots=self.plot.knots
        segs=[]
        orders=self.getOrders()
        
        for i in range(len(knots)-1):
            #get position from knots
            temp=knots[i].getPosition()
            xlow=calc.getClosest(temp,self.xdata)
            
            temp=knots[i+1].getPosition()
            xhigh=calc.getClosest(temp,self.xdata)
            
            #generate segments (order, xlow, xhigh) and arrays
            seg=(orders[i].value()+1,xlow,xhigh)
            segs.append(seg)
             
        return segs
        
    def closeEvent(self,e):
        e.accept()
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
    plot=NormPlot()
    
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

    plot.setNormData(xdata,ydata,7700)
    plot.plot.addKnot(7700)
    plot.plot.addKnot(xdata[-1])
    plot.setNumKnots(2)
    plot.setOrders([2,2])
    plot.initializeSlots()
    
    
    plot.updatePlot()
    
    plot.show()
    app.exec_()
    
