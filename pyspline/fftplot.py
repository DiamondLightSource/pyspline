#!/usr/bin/env python

# fftplot.py -- the fftPlot class used to display the Fourier transform
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
        
class fftPlot(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)

        self.setWindowTitle("Fourier Transform")
    
        #spacer-plot-spacer
        layout=QVBoxLayout()
        
        spacer=QSpacerItem(10,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout.addItem(spacer)
        
        self.plot = DataPlot(QColor(Qt.black))
        self.plot.setAxisScale(QwtPlot.xBottom,0,5)
        # Curves
        self.fftcurve=self.plot.insertCurve("fft")
        self.fftRcurve=QwtPlotCurve("fft-real")
        self.fftIcurve=QwtPlotCurve("fft-imag")
        
        self.plot.setCurvePen(self.fftcurve,QPen(QColor(Qt.black),2))
        self.plot.setCurvePen(self.fftRcurve,QPen(QColor(Qt.red),2))
        self.plot.setCurvePen(self.fftIcurve,QPen(QColor(Qt.green),2))
        cblayout=QHBoxLayout()
        self.realPart=QCheckBox(self)
        self.realPart.setText("Real part")
        self.realPart.setChecked(False)
        self.imagPart=QCheckBox(self)
        self.imagPart.setText("Imaginary part")
        self.imagPart.setChecked(False)
        self.windowLabel=QLabel(self)        
        self.windowLabel.setText("Window used:")
        self.windowList=QComboBox(self)
        #self.windowList.setText("Window")
        self.windowNames=['hanning', 'hamming', 'bartlett', 'blackman','flat']
        self.currentWindowName='hanning'
        for window in self.windowNames:
            self.windowList.addItem(window)

        #set up spin box that controls number of knots
        cblayout.addWidget(self.realPart)
        cblayout.addWidget(self.imagPart)
        cblayout.addWidget(self.windowLabel)
        cblayout.addWidget(self.windowList)
        layout.addLayout(cblayout)
        
        layout.addWidget(self.plot)
        
        layout.addItem(spacer)
        
        #spacer-wheel-spacer
        layout2=QHBoxLayout()
        
        spacer=QSpacerItem(240,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout2.addItem(spacer)
        
        self.wheel=QwtWheel(self)
        self.wheel.setTotalAngle(360.0)
        self.wheel.setRange( 0.0, 100.0 );
        self.wheel.setValue(50.0)
        self.wheel.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed))
        layout2.addWidget(self.wheel)
        
        spacer2=QSpacerItem(200,10,QSizePolicy.Fixed,QSizePolicy.Fixed)
        layout2.addItem(spacer2)
        self.plot.canvas().setMouseTracking(True)
        
        self.rdata=[]
        self.fftdata=[]
        self.fftRdata=[]
        self.fftIdata=[]
        #tool tip for wheel
        #QToolTip.add(self.wheel,QString("Adjust R scale"))
        
        #add plot and wheel to grid layout
        normDataLayout = QGridLayout()
        normDataLayout.addItem(spacer,0,0)
        normDataLayout.addLayout(layout,2,0)
        normDataLayout.addLayout(layout2,3,0)
        self.setLayout(normDataLayout)
        
        self.status=QStatusBar(self)
        normDataLayout.addWidget(self.status,4,0)
        
        #self.connect(self.plot,PYSIGNAL('positionMessage()'),self.status.message)
        self.connect(self.wheel,SIGNAL('valueChanged(double)'),self.wheelValueChanged)
        self.connect(self.realPart,SIGNAL('stateChanged(int)'),self.realPartChanged)
        self.connect(self.imagPart,SIGNAL('stateChanged(int)'),self.imagPartChanged)
        self.connect(self.windowList,SIGNAL('currentIndexChanged(int)'),self.updateFFTWindow)
        
        #self.setCaption("Fourier Transform")

        #self.clearWState(Qt.WState_Polished)
        
    def __tr(self,s,c = None):
        return qApp.translate("normData",s,c)
        
    def realPartChanged(self,state):
        if(state==0):
                self.fftRcurve.detach()
        else:
                self.fftRcurve.attach(self.plot)
        self.plot.replot()
        
    #
    # 
    #                 
    def imagPartChanged(self,state):
        if(state==0):
                self.fftIcurve.detach()
        else:
                self.fftIcurve.attach(self.plot)
        self.plot.replot()
                                        
    def closeEvent(self,e):
        self.hide()
        self.emit(SIGNAL("closed()"))
        
    def setShown(self,bool):
        if(bool):
            self.show()
        else:
            self.hide()
            
    def wheelValueChanged(self,value):
        
        self.plot.setAxisScale(QwtPlot.xBottom,0,value/10+1)
        self.plot.replot()
        
    def setfftData(self,rdata,fftdata,fftRdata,fftIdata):
        
        self.plot.setCurveData(self.fftcurve,rdata,fftdata)
        self.plot.setCurveData(self.fftRcurve,rdata,fftRdata)
        self.plot.setCurveData(self.fftIcurve,rdata,fftIdata)
        self.rdata=rdata
        self.fftdata=fftdata
        self.fftRdata=fftRdata
        self.fftIdata=fftIdata
        
        self.plot.replot()
        
    def updateFFTWindow(self,value):
        self.currentWindowName=self.windowNames[value]
        self.emit(SIGNAL('signalPlotChanged()'))
        
        
if(__name__=='__main__'):
    app=QApplication(sys.argv)
    plot=fftPlot()
    plot.show()
    app.exec_()
    
