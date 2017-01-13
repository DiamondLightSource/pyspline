#!/usr/bin/env python

# data.py -- the DataPlot class used as a parent class to handle 
#   the plots and tracking/marker mouse movements
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
import math
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

#from qt import *
#from qwt import *

from knot import *
import calc
from MyPicker import *



class DataPlot(QwtPlot):

    def __init__(self,color,*args):
        QwtPlot.__init__(self,*args)
        
        self.mode='NONE'
        
        self.knots=[]
        self.color=color
        self.excepts=[]
        self.data=[]
        self.setMouseTracking(True)
        self.__oldcursor = self.canvas().cursor().shape()
        self.picker = MyPicker(self.canvas())
        self.picker.setSelectionFlags(Qwt.QwtPicker.DragSelection  |
                                     Qwt.QwtPicker.RectSelection)
        #self.picker.setAxis(Qwt.QwtPlot.xBottom,Qwt.QwtPlot.yLeft)
        self.zooming = 0
        self.selecting = 0
        self.zoomback   = 1
        self.xAutoScale = True
        self.yAutoScale = True
        self.panningMode = False
        self.zoomStack  = []
        self.zoomState    = []
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.xTop)
        self.picker.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        self.picker.setRubberBandPen(QPen(Qt.green))
        self.picker.setEnabled(1)
        self.connect(self.picker,SIGNAL('MouseMoved(const QMouseEvent&)'),self.onMouseMoved)
        self.connect(self.picker,SIGNAL('MousePressed(const QMouseEvent&)'),self.onMousePressed)
        self.connect(self.picker,SIGNAL('MouseReleased(const QMouseEvent&)'),self.onMouseReleased)

    def addKnot(self,pos,lock=False):
        
        #if no other knots, just add and set boundary to be max and min
        if(len(self.knots)==0):
            knot=Knot(pos,self.color,self)
            dmax=self.canvasMap(QwtPlot.xBottom).s2()
            dmin=self.canvasMap(QwtPlot.xBottom).s1()
            knot.setBoundary(dmin,dmax)
            
            knot.attach(self)
            self.knots.append(knot)
            
            knot.setLock(lock)
        
            return
            
        #make sure new position is reasonable
        
        last=self.knots[-1]
        lastpos=last.getPosition()
        #print 'pos and lastpos',pos,lastpos
        if(pos<lastpos):
            print "New knot position is lower than previous knots"
            return
        
        xmax=self.canvasMap(QwtPlot.xBottom).s2()
        if(pos>xmax):
            #print "New knot position is too high"
            pos=xmax
        
        xmin=self.canvasMap(QwtPlot.xBottom).s1()
        if(pos<xmin):
            pos=xmin
        #create and add knot, adding boundary of previous knot
        knot=Knot(pos,self.color,self)
        knot.setLock(lock)
        knot.setBoundary(lastpos+0.01,xmax)
        knot.attach(self)
        self.knots.append(knot)
        
        #also fix boundary of last knot
        bndy=last.getBoundary() 
        bndy[1]=pos-0.01
        last.setBoundary(bndy[0],bndy[1])

        self.fixKnotsBounds()
        self.replot()

    
    def removeKnot(self):
        keys=self.knots
        keys[-1].detach()
        self.knots.pop()
        self.fixKnotsBounds()
        self.emit(SIGNAL('signalChangedPlot()'))
        self.replot()
    
    def resetPlot(self):
            for key in self.knots:
                key.detach()
            self.knots=[]
            
    def addBoundsExceptions(self,knot,bnd,value):
        bounds=self.knots[knot].getBoundary()
        bounds[bnd]=value
        self.knots[knot].setBoundary(bounds[0],bounds[1])
        
        self.excepts.append((knot,bnd,value))

    def insertCurve(self, key):
        curve = QwtPlotCurve(key)
        curve.attach(self)
        return curve

    def setCurvePen(self, curve, pen):
        symbol = curve.symbol()
        symbol.setPen(pen)
        brush = symbol.brush()
        brush.setColor(pen.color())
        curve.symbol().setBrush(brush)
        curve.setPen(pen)

    def setCurveData(self, curve, x, y):
        curve.setData(x, y)

    def onMousePressed(self,event):
        #print "enter slotMouse pressed"
        xpixel = event.pos().x()
        ypixel = event.pos().y()
        self.oldx=self.invTransform(QwtPlot.xBottom,xpixel)
        self.oldy=self.invTransform(QwtPlot.yLeft,ypixel)
        self.oldxpos=xpixel
        self.oldypos=ypixel

        marker,dist=self.closestMarker(xpixel)
        if dist < 4:
                self.movingMarker=marker
                #does it exist?
                if(self.movingMarker==None):
                    return
                #is it in the list of knots?
                if not self.knots.__contains__(marker):
                    return
            
                if not self.movingMarker.isLocked():
                    self.mode='MOVING_MARKER'
                    self.picker.setRubberBand(QwtPicker.NoRubberBand)
        else:
            self.picker.setRubberBand(QwtPicker.RectRubberBand)
            if self.zoomStack == []:
                self.zoomState = (
                        self.canvasMap(QwtPlot.xBottom).s1(),
                        self.canvasMap(QwtPlot.xBottom).s2(),
                        self.canvasMap(QwtPlot.yLeft).s2(),
                        self.canvasMap(QwtPlot.yLeft).s1())
            self.mode='ZOOMING'
            #status=QString("Trying to move an unmovable marker")
            #self.emit(SIGNAL('positionMessage()'),(status))
        
    def onMouseMoved(self,event):
        #print "enter slotMouseMoved",self.mode
        xpixel=event.x()
        ypixel=event.y()
        self.newx=self.invTransform(QwtPlot.xBottom,event.x())
        self.newy=self.invTransform(QwtPlot.yLeft,event.y())
        if (self.mode=='MOVING_MARKER'):
            xpos=self.movingMarker.xValue()
            diffx=self.newx-self.oldx
            newxpos=xpos+diffx
            bounds=self.movingMarker.getBoundary()
            #print xpos,self.oldx,self.newx,diffx,newxpos,bounds[0],bounds[1]
            if(newxpos < bounds[0]):
                temp="Moving marker can't move any farther"
                #find data point closest to self.newx that is above lowest boundary
                #newxpos=self.findPointAbove(bounds[0])
                newxpos=bounds[0]
                self.oldx=newxpos
                
            elif(newxpos > bounds[1]):
                temp="Moving marker can't move any farther"
                
                #find data point closest to self.newx that is below highest boundary
                newxpos=bounds[1]
                self.oldx=newxpos
                
            else:
                
                self.oldx=self.newx
                temp="Moving marker at %.3f" % newxpos
                
            #newpos=self.getClosest(newxpos)
            #print 'newxpos',newxpos
            self.movingMarker.setPosition(newxpos)
            
            self.fixKnotsBounds()
            
            self.replot()
            self.emit(SIGNAL('signalUpdate()'))
        #elif(self.mode=='ZOOMING'):
        #    continue
        elif(self.mode!='ZOOMING'):                
            # Just moving the mouse around....as you come close to a marker change mouse shape
            (marker,distance)=self.closestMarker(xpixel)
            if distance < 4:
                if marker is None:
                    pass
                else:
                    if (self.canvas().cursor().shape() != Qt.SizeHorCursor) and \
                        (self.canvas().cursor().shape() != Qt.SizeVerCursor):
                        self.__oldcursor = self.canvas().cursor().shape()
                        self.canvas().setCursor(QCursor(Qt.SizeHorCursor))
                    else:
                        #the marker is selectable because we are in markermode
                        if (self.canvas().cursor().shape() != Qt.SizeHorCursor) and \
                           (self.canvas().cursor().shape() != Qt.SizeVerCursor) and \
                           (self.canvas().cursor().shape() != Qt.PointingHandCursor):
                            self.__oldcursor = self.canvas().cursor().shape()
                            self.canvas().setCursor(QCursor(Qt.PointingHandCursor))
            else:
                self.canvas().setCursor(QCursor(self.__oldcursor))

    def onMouseReleased(self,event):
        
        xpos=self.invTransform(QwtPlot.xBottom,event.x())
        ypos=self.invTransform(QwtPlot.xBottom,event.y())
        temp="x: %.3f" % self.newx+", y: %.3f" %self.newy 
        if Qt.LeftButton == event.button():        
                if(self.mode=='ZOOMING'):
                        #print 'here1',self.oldxpos, event.pos().x()
                        #print 'here2',self.oldypos, event.pos().y()
                        xmin0 = min(self.oldxpos, event.pos().x())
                        xmax0 = max(self.oldxpos, event.pos().x())
                        ymin0 = min(self.oldypos, event.pos().y())
                        ymax0 = max(self.oldypos, event.pos().y())
                        self.picker.setRubberBand(QwtPicker.NoRubberBand)
                        xmin = self.invTransform(QwtPlot.xBottom, xmin0)
                        xmax = self.invTransform(QwtPlot.xBottom, xmax0)
                        ymin = self.invTransform(QwtPlot.yLeft, ymin0)
                        ymax = self.invTransform(QwtPlot.yLeft, ymax0)
                        if xmin == xmax or ymin == ymax:
                            return
                        self.zoomStack.append(self.zoomState)
                        self.zoomState = (xmin, xmax, ymin, ymax)
                        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
                        self.setAxisScale(QwtPlot.yLeft, ymax, ymin)
                if(len(self.knots)>0):
                    temp+="; [ "
                    for knot in self.knots[:-1]:
                        #tempnum=knot.getPosition()
                        #print 'knot position',knot.getPosition(),self.data
                        tempnum=calc.getClosest(knot.getPosition(),self.data)
                        knot.setPosition(tempnum)
                        temp+="%.3f, "%(tempnum,)
                    
                    #temp+=str(self.knots[-1].getPosition())
                    tempnum=calc.getClosest(self.knots[-1].getPosition(),self.data)
                    self.knots[-1].setPosition(tempnum)
                    temp+="%.3f ]"%(tempnum,)
        elif Qt.RightButton == event.button():
                if len(self.zoomStack):
                    xmin, xmax, ymin, ymax = self.zoomStack.pop()
                    self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
                    self.setAxisScale(QwtPlot.yLeft, ymax, ymin)
                else:
                    self.setAxisAutoScale(QwtPlot.yLeft) 
                    self.setAxisAutoScale(QwtPlot.xBottom)

        self.mode='NONE'
        status=QString(temp)
        #self.emit(SIGNAL('positionMessage()'),(status,))
        self.emit(SIGNAL('signalUpdate()'))
        self.replot()
        
    def setData(self,data):
        self.data=data
    
    def fixKnotsBounds(self):
        
        if len(self.knots)==0 or len(self.knots)==1:
            return
            
        min=self.canvasMap(QwtPlot.xBottom).s1()
        max=self.knots[1].xValue()-0.01
        
        self.knots[0].setBoundary(min,max)
        
        for i in range(1,len(self.knots)-1):
            self.knots[i].setBoundary(self.knots[i-1].xValue()+0.01,
                                        self.knots[i+1].xValue()-0.01)
    
        min=self.knots[-2].xValue()+0.01
        max=self.canvasMap(QwtPlot.xBottom).s2()
        
        self.knots[-1].setBoundary(min,max)
        
        for ex in self.excepts:
            bnd=self.knots[ex[0]].getBoundary()
            bnd[ex[1]]=ex[2]
            self.knots[ex[0]].setBoundary(bnd[0],bnd[1])
    
    def closestKnot(self,x):
        dist=0.0
        mindist=1.0e10
        key=None
        for knot in self.knots:
            dist=(x-knot.xValue())**2.0
            #print x,knot.xValue(),dist
            if(dist<mindist):
                key=knot
                mindist=dist
        return key,math.sqrt(mindist)

    def getClosest(self,val): #replace by bisecting sort later?
        
        keys=self.curveKeys()
        
        if(len(keys)==0):
            return val
        
        curve=self.curve(keys[0])
        size=curve.dataSize()
        
        xmin=0
        xmax=0
        
        for i in range(size):
            if(curve.x(i) <= val and val <= curve.x(i+1)):
                xmin=curve.x(i)
                xmax=curve.x(i+1)
                
        if(xmin==0 and xmax==0):
            if( val-curve.x(size-1) < val-curve.x(0)):
                return curve.x(size-1)
            else:
                return curve.x(0)
        
        if(val-xmin < xmax-val):
            return xmin
        else:
            return xmax

    def closestMarker(self, xpixel):
        x = self.invTransform(QwtPlot.xBottom, xpixel)
        (marker, distance) = (None, 1.0E24)
        for knot in self.knots:
            distancew = abs(x - knot.xValue())
            if distancew < distance:
                distance = distancew
                marker   = knot
            #this distance is in x coordenates
            #but I decide on distance in pixels 
        if distance is not None:
            x1pixel = abs(self.invTransform(QwtPlot.xBottom, xpixel+4)-x)/4.0
            distance = distance / x1pixel
        return (marker, distance)


            
    def findPointAbove(self,pos):
        
        keys=self.curveKeys()
        if(len(keys)==0):
            return pos
            
        curve=self.curve(1)
        
        size=curve.dataSize()
        
        for i in range(size):
        
            if(curve.x(i)>pos):
                return curve.x(i)
                
        return curve.x(size-1)
        
    def findPointBelow(self,pos):
        
        keys=self.curveKeys()
        if(len(keys)==0):
            return pos
        
        curve=self.curve(1)
        
        size=curve.dataSize()
        
        i=size-1
        while(i>=0):
        #for i in range(size).reverse():
        
            if(curve.x(i)<pos):
                return curve.x(i)
            i-=1
        
        return curve.x(0)


    def zoomReset(self):
        if self.yAutoScale:
            self.setAxisAutoScale(qwt.QwtPlot.yLeft) 
            self.setAxisAutoScale(qwt.QwtPlot.yRight)
        
        if self.xAutoScale:
            self.setAxisAutoScale(qwt.QwtPlot.xTop) 
            self.setAxisAutoScale(qwt.QwtPlot.xBottom)

        self.zoomStack =  []
        self.zoomStack2 = []
        self.replot()
            

    def enableZoom(self, flag=True):
        self.zoomEnabled = flag
        if flag:self.selecting = False

    def isZoomEnabled(self):
        if self.zoomEnabled:
            return True
        else:
            return False

    
if(__name__=="__main__"):
    app=QApplication(sys.argv)
    plot=DataPlot(QColor(Qt.red))
    plot.setAxisScale(QwtPlot.xBottom,0.0,1000.0)
    plot.setAxisScale(QwtPlot.yLeft,0.0,1000.0)
    plot.replot()
    #print plot.axisScaleDiv(QwtPlot.yLeft).hBound()
    #plot.addKnot(200)
    plot.show()
    plot.canvas().setMouseTracking(True)
    curve=QwtPlotCurve()
    step=10.0
    xdata=[]
    ydata=[]
    for i in range(100):
        xdata.append(i*step)
        ydata.append(i*step)
    curve.setData(xdata,ydata)
    curve.attach(plot)
    plot.setData(xdata)
    plot.addKnot(500)
    plot.addKnot(400)
    plot.addKnot(600)

    print plot.axisScaleDiv(QwtPlot.yLeft).hBound()
    
    app.exec_()
