# main.py -- the main PySpline class used for the program
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
#generated with the help of Qt Designer

#os specific things
import os

from os.path import exists
from time import localtime,asctime


from PyQt4.Qt import *
from PyQt4.Qwt5 import *

#program files
from rawplot import *
from dataplot import *
from DataImporter import *
from normplot import *
from fftplot import *
from kplot import *
from i0plot import *
from bounds import *
from edge import *
from poly import *
from aboutbox import *
from comments import *
from icons import *
import calc

#math libraries
from math import sqrt,pi
from numpy import *
from numpy import linalg
from numpy import fft

import string

KEV=0.5123143 #conversion between eV and k
HC=12398.5471 #conversion between eV and lambda

#Canvas class is for printing
class Canvas(QWidget):
    #def __init__(self,windows,filename,E0,title="",comments="",parent = None, name = None,fl = 0):
    def __init__(self,parent,name=None,fl= 0):
        QWidget.__init__(self,None,name,fl)
        
        self.resize(640,480)
        #self.windows=windows
        
        time=localtime()
        text=asctime(time)
        
        #self.header=QString(title+": "+filename+" -- E0: "+str(E0)+" eV -- "+text)
        #self.footer=comments
        
        self.parent=parent
        
        try:
            self.setBackgroundColor(Qt.white)
        except AttributeError:
            try:
                self.setPaletteBackgroundColor(Qt.white)
            except AttributeError:
                print "Error setting background color to white"
                
        self.show()
        
    def paintEvent(self,e):
        
        painter=QPainter(self)
        self.parent.printPlot(painter)
        painter.end()
        
        return
        width=self.geometry().width()
        height=self.geometry().height()
        
        fm=QFontMetrics(self.font())
        
        fontheight=fm.height()
        fontleading=fm.leading()
        lines=len(self.footer)
        hcomment=lines*fontheight+(lines-1)*fontleading
        
        #get parameters for raw curve
        rorder=self.windows[0].getSpinBoxValue()
        rleft=self.windows[0].plot.knots[0].getPosition()
        rright=self.windows[0].plot.knots[1].getPosition()
        
        #build string for raw
        rstr="Background: %.3f (%i) %3.f"%(rleft,rorder,rright)

        #get parameters for norm curve
        segs=self.windows[1].getSegs()
        nstr="Spline: %.3f (%i) %.3f"%(segs[0][1],segs[0][0]-1,segs[0][2])
        for i in range(1,len(segs)):
            nstr+=" (%i) %.3f"%(segs[i][0]-1,segs[i][2])
            
        #build string for kspace
        kleft=self.windows[2].plot.knots[0].getPosition()
        kright=self.windows[2].plot.knots[1].getPosition()
        kstr="Window: %.3f-%.3f"%(kleft,kright)
        xmargin=width/60
        ymargin=height/60
        xpadding=width/120
        ypadding=height/30
        
        plotwidth=(width-2*xmargin-2*xpadding)/2 #border of 10 on each side
        plotheight=(height-2*ymargin-2*fontheight-5*ypadding-hcomment)/2 #30 for text height and padding      
        
        painter=QPainter(self)
        #paint name and date
        painter.drawText(xmargin,ymargin+fontheight,self.header)
        

#paint raw
        tempcolor=QColor(self.windows[0].plot.canvasBackground())
        self.windows[0].plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding
        self.windows[0].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[0].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,rstr)
        
#paint norm
        tempcolor=QColor(self.windows[1].plot.canvasBackground())
        self.windows[1].plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding
        self.windows[1].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[1].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        oldfont=self.font()
        newfont=self.font()
        
        while(fm.width(nstr)>=plotwidth):
            newfont.setPointSize(newfont.pointSize()-1)
            fm=QFontMetrics(newfont)
            
        painter.setFont(newfont)
        
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,nstr)
        
        painter.setFont(oldfont)
        
#paint kspace
        tempcolor=QColor(self.windows[2].plot.canvasBackground())
        self.windows[2].plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.windows[2].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[2].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+2*ypadding+plotheight+fontheight
        painter.drawText(x,y,kstr)
        
#paint rspace

        tempcolor=QColor(self.windows[3].plot.canvasBackground())
        self.windows[3].plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.windows[3].plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.windows[3].plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
#paint comments

        yoffset=xmargin+fontheight+ypadding+plotheight+fontheight+ypadding*1.5+plotheight+ypadding+fontheight+ypadding
        
        for line in self.footer:
            painter.drawText(xmargin,yoffset,line)
            yoffset+=(fontheight)
            
        painter.end()
        
        
class PySpline(QMainWindow):
    def __init__(self,parent = None):
        QMainWindow.__init__(self,parent)
        self.statusBar()

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image2 = QPixmap()
        self.image2.loadFromData(image2_data,"PNG")
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        self.image4 = QPixmap()
        self.image4.loadFromData(image4_data,"PNG")
        self.image5 = QPixmap()
        self.image5.loadFromData(image5_data,"PNG")
        self.image6 = QPixmap()
        self.image6.loadFromData(image6_data,"PNG")
        self.image7 = QPixmap()
        self.image7.loadFromData(image7_data,"PNG")
        self.image8 = QPixmap()
        self.image8.loadFromData(image8_data,"PNG")
        self.image9 = QPixmap()
        self.image9.loadFromData(image9_data,"PNG")
        
        self.xdata=[]
        self.ydata=[]
        self.i0data=[]
        self.background=[]
        self.filename=""
        self.title=""
        self.comments=[]

        self.raw=RawPlot(self)
        #self.raw.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.raw.resize(500,300)
        self.raw.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.raw.plot.setAxisTitle(QwtPlot.xBottom,QString("Energy (eV)"))
        
        self.setCentralWidget(self.raw)
        
        self.norm=NormPlot()
        #self.norm.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.norm.resize(600,400)
        self.norm.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.norm.plot.setAxisTitle(QwtPlot.xBottom,QString("Energy (eV)"))
        self.norm.show()
        
        self.kspace=KPlot()
        self.kspace.resize(600,400)
        self.kspace.plot.setAxisScale(QwtPlot.xBottom,0,100)
        self.kspace.plot.setAxisTitle(QwtPlot.xBottom,QString("k (1/A)"))
        self.kspace.show()
        
        self.fft=fftPlot()
        self.fft.resize(600,400)
        self.fft.show()
        self.fft.plot.setAxisTitle(QwtPlot.xBottom,QString("R (A)"))
        
        self.i0=I0Plot()
        self.i0.resize(600,400)
        self.i0.plot.setAxisTitle(QwtPlot.xBottom,QString("Energy (eV)"))
        
        #self.connect(self.raw.plot,PYSIGNAL('positionMessage()'),self.message)
        self.connect(self.raw,SIGNAL('signalPlotChanged()'),self.updateNormPlot)
        self.connect(self.norm,SIGNAL('signalPlotChanged()'),self.updateXAFSPlot)
        self.connect(self.kspace,SIGNAL('signalPlotChanged()'),self.updateXAFSPlot)
        self.connect(self.kspace.plot,SIGNAL('signalUpdate()'),self.updatefftPlot)
        self.connect(self.fft,SIGNAL('signalPlotChanged()'),self.updatefftPlot)
        self.mydirectory=""
        self.initActions()

    def readArray(self,file):
        arr=[]
        str=file.readline()
        while(str): #read each line, which is comma-delimeated
            temp=str.split(' ')
            subarr=[]
            for a in temp:
                subarr.append(float(a))
                
            arr.append(subarr)
            str=file.readline()
        
        #numpy arrays have transpose functions
        return array(arr)
        
    def fileOpen(self):
    
        self.xdata=[]
        self.ydata=[]
        self.i0data=[]
        self.background=[]
        
        dialog = QFileDialog()
        filename=dialog.getOpenFileName(self,"Open pyspline files",self.mydirectory,"All files (*.*)")
        if filename == "":
            return
        self.mydirectory=QString(os.path.dirname(filename.toLatin1()))
        self.fileStringOpen(filename.toLatin1())
        
    def fileStringOpen(self,str):
        
        if str == None:
            return
        
        self.filename=str
        file=open(str)
        
#check to see if it has a title
        line=file.readline()
        if(line[:5]=='TITLE'):
            self.title=line[6:-1]
            line=file.readline()
            
#check to see if line is a comment
        while(line[0]=='#'):
            self.comments.append(line[2:-1])
            line=file.readline()
            
#read E0
        array=string.split(line)
        self.E0=float(array[1])

#read background bounds and order
#BACKGROUND lowx (order)  highx
        line=file.readline()
        array=string.split(line)
        rawlowx = float(array[1])
        rawhighx = float(array[3])
        raworder = int(array[2][1:-1])
        
#read spline info into makers and orders lists
#SPLINE marker (order) marker (order) marker .....
        line=file.readline() 
        array=string.split(line)
        markers=[]
        orders=[]
        
        for i in range(1,len(array)-2,2):
            markers.append(float(array[i]))
            orders.append(int(array[i+1][1]))
        markers.append(float(array[-2])) 
        
#check to see if k-window is specified
#if not, column header is stripped
        line=file.readline()
        array=string.split(line)
        if(array[0]=='KWIN'):
            window=(float(array[1]),float(array[2]))
            line=file.readline()
       
        
#file stream is now data, read it
        arrs=self.readArray(file)
        file.close()

        #arrs looks like:
        #[ [col1 col2 col3 col4]
        #  [col1 col2 col3 col4]
        #  ....
        #  ]]
        #transpose to get columns in useful format
        
        data=transpose(arrs)
        xdata=data[0].tolist()
        #i0data=data[2].tolist()
        ydata=data[3].tolist()
    
        self.resetPlots()
        
        rawlowx=calc.getClosest(rawlowx,xdata)
        rawhighx=calc.getClosest(rawhighx,xdata)
        
        self.setupRawPlot(xdata,ydata,rawlowx,rawhighx,raworder)
        self.setupNormPlot(xdata,markers,orders)
        #self.i0.setI0Data(xdata,i0data)
        
        kmax=calc.toKSpace(xdata[-1],self.E0)
        self.setupXAFSPlot(kmax,window[0],window[1])
        
        self.raw.updatePlot()
#         self.connect(self.raw.plot,PYSIGNAL('positionMessage()'),self.message)
#         self.connect(self.norm.plot,PYSIGNAL('signalChangedPlot'),self.slotUpdateNormPlot)
#         self.connect(self.kspace.plot,PYSIGNAL('signalChangedPlot'),self.slotUpdateKSpacePlot)
    
    def fileImport(self):

        xdata=[]
        ydata=[]
        i0data=[]
#        path=os.getcwd()
#        print path
        dialog = QFileDialog()
        filename=dialog.getOpenFileName(self,"Import Raw Data files",self.mydirectory,"All files (*.*)")
#        filename=QFileDialog.getOpenFileName(self,QString("*.dat"))
        self.filename=str(filename)
        if filename == "":
            return
	# Remember the directory for next time....
        print "filename",filename
        self.mydirectory=QString(os.path.dirname(self.filename))
#        self.filename=filename.toLatin1()
        fileImportDialog=DataImporter(parent=self)
        loadedok=fileImportDialog.loadFile(self.filename)
        if(loadedok==False):
                QMessageBox.critical(self,QString("Error with file"),"This does not appear to be a data file")
                return
        result=fileImportDialog.exec_()
        if(result==QDialog.Rejected):
            return

        xdata,ydata,elementName,elementEdge=fileImportDialog.getData()
        #print 'edge position', fileImportDialog,guess_iz(xdata,ydata)
        
        edgeDialog=EdgeDialog()
        edgeDialog.setElementAndEdge(elementName,elementEdge)
        result=edgeDialog.exec_()
        
        if(result==QDialog.Rejected):
            return
            
        self.E0=edgeDialog.getValue()
        self.title=edgeDialog.getTitle()
        
        #check to see if E0 is reasonable!!
        while((self.E0 < xdata[0]) or (self.E0 > xdata[-1])):
            #for some reason, in windows, the str version used wasn't the
            #builtin version to convert between numbers and strings
            errstr="There appears to be a problem with E0="+str(self.E0)+". This value does not fall in the range of your data."
            QMessageBox.critical(self,QString("Error with E0"),QString(errstr))

            result=edgeDialog.exec_()
            
            if(result==QDialog.Rejected):
                return
                
            self.E0=edgeDialog.getValue()
            self.title=edgeDialog.getTitle()
                
        self.resetPlots()
        #
        # setup raw plot background values.
        # I know the edge position and I know the start of the scan so
        # I will try put it 80% between these values
        #
        backhigh=xdata[0]+(self.E0-xdata[0])*0.8
        backhigh2=calc.getClosest(backhigh,xdata)
        self.setupRawPlot(xdata,ydata,xdata[0],backhigh2,2)
        #print 'xdata[-1]',xdata[-1]
        self.setupNormPlot(xdata,[self.E0,xdata[-1]],[3])
        self.i0.setI0Data(xdata,i0data)
        
        kmax=calc.toKSpace(xdata[-1],self.E0)
        self.setupXAFSPlot(kmax,0,kmax)
        
        self.raw.updatePlot()

    def fileImportXMU(self):

        xdata=[]
        ydata=[]
        i0data=[]
        
        filename=QFileDialog.getOpenFileName(self,"Import Athena mu(E) file",self.mydirectory,"*.xmu")
        self.filename=filename.toLatin1()
        if self.filename == None:
            return
        self.mydirectory=os.path.dirname(self.filename)
        file=open(filename.toLatin1())
        filelines=file.readlines()
        file.close()
        if(self.containsChar(filelines[0],'Athena')==0 or self.containsChar(filelines[1],'mu')==0):
            errstr="This does not appear to be an Athena xmu data file"
            QMessageBox.critical(self,QString("Error"),QString(errstr))
            return


        for line in filelines:
            if(self.containsChar(line,'#')==1):
                continue
            else:            
                array=string.split(line)
                xdata.append(float(array[0]))
                ydata.append(float(array[1]))
                i0data.append(0.0)


        edgeDialog=EdgeDialog()
        result=edgeDialog.exec_()
        
        if(result==QDialog.Rejected):
            return
            
        self.E0=edgeDialog.getValue()
        self.title=edgeDialog.getTitle()
        
        #check to see if E0 is reasonable!!
        while((self.E0 < xdata[0]) or (self.E0 > xdata[-1])):
            #for some reason, in windows, the str version used wasn't the
            #builtin version to convert between numbers and strings
            errstr="There appears to be a problem with E0="+str(self.E0)+". This value does not fall in the range of your data."
            QMessageBox.critical(self,QString("Error with E0"),QString(errstr))

            result=edgeDialog.exec_()
            
            if(result==QDialog.Rejected):
                return
                
            self.E0=edgeDialog.getValue()
            self.title=edgeDialog.getTitle()
                
        self.resetPlots()
        self.setupRawPlot(xdata,ydata,xdata[0],xdata[-1],2)
        #print 'xdata[-1]',xdata[-1]
        self.setupNormPlot(xdata,[self.E0,xdata[-1]],[3])
        self.i0.setI0Data(xdata,i0data)
        
        kmax=calc.toKSpace(xdata[-1],self.E0)
        self.setupXAFSPlot(kmax,0,kmax)
        
        self.raw.updatePlot()

    def containsChar(self,str, set):
        for c in set:
            if c in str: return 1
        return 0



    
    def resetPlots(self):
        #in the event that we are opening a file when one is open,
        #makers and curves need to be cleared
        
        self.raw.plot.resetPlot()
        self.norm.plot.resetPlot()
        self.kspace.plot.resetPlot()
        self.fft.plot.resetPlot()
        
    def setupRawPlot(self,xdata,ydata,lowx,highx,order):
        
        self.raw.setRawData(xdata,ydata,self.E0)
        self.raw.plot.replot()
        self.raw.plot.addKnot(lowx)
        self.raw.plot.addKnot(highx)
        self.raw.plot.replot()
        self.raw.spinBox.setValue(order)
       
    def setupNormPlot(self,xdata,markers,orders):

        #make sure scale of plot is reasonable
        self.norm.plot.setAxisScale(QwtPlot.xBottom,xdata[0],xdata[-1])
        self.norm.plot.replot()
        #adjust markers to closest data positions
        for i in range(len(markers)):
            temp=calc.getClosest(markers[i],xdata)
            #print 'temp',temp
            self.norm.plot.addKnot(temp)
            
        self.norm.plot.addBoundsExceptions(0,0,self.E0)
        
        #set number of knots in normplot window
        self.norm.setNumKnots(len(markers))
        self.norm.setOrders(orders)
        
        self.norm.initializeSlots()
       
    def setupXAFSPlot(self,max,pos1,pos2):
        
        self.kspace.plot.setAxisScale(QwtPlot.xBottom,0,max+0.5)
        self.kspace.plot.replot()
        self.kspace.plot.addKnot(pos1)
        self.kspace.plot.replot()
        self.kspace.plot.addKnot(pos2)
        self.kspace.plot.replot()
        
    def setupI0Curve(self):

        #in the event that we are opening a file when one is open,
        #makers and curves need to be cleared

        self.i0.plot.removeCurves()
        
        self.i0plot=self.i0.plot.insertCurve("I0")
        self.i0.plot.setCurvePen(self.i0plot,QPen(QColor(Qt.black),2))
        self.i0.plot.setAxisScale(QwtPlot.xBottom,self.xdata[0],self.xdata[-1])
        self.i0.plot.setAxisScale(QwtPlot.yLeft,min(self.i0data),max(self.i0data))
        self.i0.plot.setCurveData(self.i0plot,self.xdata,self.i0data)


        
    def fileSave(self):
        try:
            self.save(self.filename,0)
        except AttributeError:
            self.fileSaveAs()
            
    def fileSaveAs(self):
        qstr=QFileDialog.getSaveFileName(self,"Save All PySpline Data",self.mydirectory,QString("*.dat;;*"))

        if(qstr):
            self.filename=qstr.toLatin1()
            self.mydirectory=QString(os.path.dirname(self.filename))
            self.save(self.filename,1)

    def exportFourier(self):
        
        qstr=QFileDialog.getSaveFileName(self,"Save Fourier Transform",self.mydirectory,QString("*.fft;;*"))
        if(qstr):
            self.mydirectory=QString(os.path.dirname(qstr.toLatin1()))
            fout=open(qstr.toLatin1(),"w")
            fout.write("R fftmag imag real\n")

            rdata=self.fft.rdata
            fftdata=self.fft.fftdata
            fftidata=self.fft.fftIdata
            fftrdata=self.fft.fftRdata
        
            for i in range(len(rdata)):
                fout.write("%7.3f %7.3f %7.3f %7.3f\n"%(rdata[i],fftdata[i],fftidata[i],fftrdata[i]))
            fout.close()
               
    def save(self,filestring,fileoption):
        if(fileoption==0):
            if(("pys" in filestring)==0):
                filestring=filestring+".pys"
        self.filename=filestring
        fout=open(filestring,"w")
        #print 'self.filename',self.filename,filestring
        #write title and comments
        fout.write("TITLE "+self.title+"\n")
        for line in self.comments:
            fout.write("# "+line+"\n")
            
        #write E0
        fout.write("E0 %.3f\n" % self.E0)

        #get background marker information
        markers=self.raw.plot.knots
        lowx=markers[0].getPosition()
        highx=markers[1].getPosition()
        order=self.raw.getSpinBoxValue()
        
        #write background info
        #file.write("BACKGROUND "+str(lowx)+" ("+str(order)+") "+str(highx)+" eV\n")
        fout.write("BACKGROUND %.5f (%i) %.5f eV\n" % (lowx,order,highx))

        #write spline segs info
        fout.write("SPLINE ")
        segs=self.norm.getSegs()
        for seg in segs:
            fout.write("%.5f" % seg[1]) #lower bound
            fout.write(" ("+str(seg[0]-1)+") ") #order
        fout.write("%.5f eV\n" % segs[-1][2]) #higher bound of last segment

        #write windowing info
        knots=self.kspace.plot.knots
        min=knots[0].getPosition()
        max=knots[1].getPosition()
        
        fout.write("KWIN %.5f %.5f \n" % (min,max))
        
        #header string
        #fout.write("EV EV_MINUS_E0 K IO RAW BACKGROND NORMAL SPLINE XAFS\n")
        fout.write("EV EV_MINUS_E0 K RAW BACKGROND NORMAL SPLINE XAFS\n")

        #actual data, pad kdata and xafsdata with zeros
        xdata=self.raw.xdata
        #i0data=self.i0.ydata
        ydata=self.raw.ydata
        background=self.raw.background
        normdata=self.norm.normdata
        splinedata=self.norm.splinedata
        xafsdata=self.kspace.xafsdata
        new_xdata = []         
        tempk=self.kspace.kdata
        new_xdata = [] 
        for xi in xdata:
                new_xdata.append(xi-self.E0)
        
        datasize=len(xdata)
        kdata=zeros((datasize),dtype=float)
        kdata[-len(tempk):]=tempk
        xafs=zeros((datasize),dtype=float)
        xafs[-len(xafsdata):]=xafsdata

        data=[xdata,new_xdata,kdata,ydata,background,
                    normdata,splinedata,xafs]
        #print len(xdata),len(i0data),len(ydata),len(background),len(normdata),len(splinedata),len(xafs)

        data2=array(data).astype('float')
        datat=transpose(data2).tolist()

        for row in datat:
            for i in range(len(row)):
                fout.write("%.6f" % row[i])
                if(i==len(row)-1):
                    fout.write("\n")
                else:
                    fout.write(" ")
        
        fout.close()
        
    def filePrint(self):

        #keys=[self.raw,self.norm,self.kspace,self.fft]   
        #self.canvas=Canvas(keys,self.filename,self.E0,self.title,self.comments)
        #self.canvas=Canvas(self)
        
        printer=QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setPageSize(QPrinter.Letter)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputToFile(True)
        
        fileinfo=QFileInfo(self.filename)
        name=fileinfo.baseName().toLatin1()+'.ps'
        
        printer.setOutputFileName(name)
        if printer.setup():
            try:
                printer.setResolution(300)
            except AttributeError:
                pass
            painter=QPainter(printer)
            self.printPlot(painter)
            painter.end()
        
    def printPlot(self,painter):
        
        pd=QPaintDeviceMetrics(painter.device())
        
        width=pd.width()
        height=pd.height()
        
        fm=QFontMetrics(painter.font())
        selfpd=QPaintDeviceMetrics(self)
        
        scale=float(pd.logicalDpiY()/selfpd.logicalDpiY())
        scalex=float(pd.logicalDpiX()/selfpd.logicalDpiX())
        
        fontheight=fm.height()*scale
        fontleading=fm.leading()*scale
        lines=len(self.comments)
        hcomment=lines*fontheight+(lines-1)*fontleading
        
#build raw string
        time=localtime()
        text=asctime(time)
        header=QString(self.title+": "+self.filename+" -- E0: "+str(self.E0)+" eV -- "+text)
        
#get parameters for raw curve
        rorder=self.raw.getSpinBoxValue()
        rleft=self.raw.plot.knots[0].getPosition()
        rright=self.raw.plot.knots[1].getPosition()
        
#build string for raw
        rstr="Background: %.3f (%i) %3.f"%(rleft,rorder,rright)

        #get parameters for norm curve
        segs=self.norm.getSegs()
        nstr="Spline: %.3f (%i) %.3f"%(segs[0][1],segs[0][0]-1,segs[0][2])
        for i in range(1,len(segs)):
            nstr+=" (%i) %.3f"%(segs[i][0]-1,segs[i][2])
            
        #build string for kspace
        kleft=self.kspace.plot.knots[0].getPosition()
        kright=self.kspace.plot.knots[1].getPosition()
        kstr="Window: %.3f-%.3f"%(kleft,kright)
        xmargin=width/(10*scalex)
        ymargin=height/(20*scale)
        xpadding=width/(20*scalex)
        ypadding=height/(20*scale)
        
        plotwidth=(width-2*xmargin-2*xpadding)/2 #border of 10 on each side
        plotheight=(height-2*ymargin-2*fontheight-5*ypadding-hcomment)/2 #30 for text height and padding      
        
#paint name and date
        painter.drawText(xmargin,ymargin,header)
        

#paint raw
        tempcolor=QColor(self.raw.plot.canvasBackground())
        self.raw.plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding
        self.raw.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.raw.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,rstr)
        
#paint norm
        tempcolor=QColor(self.norm.plot.canvasBackground())
        self.norm.plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding
        self.norm.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.norm.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        oldsize=painter.font().pointSize()
        print painter.font().pointSize(),painter.font().pixelSize()
        newsize=oldsize
        family=painter.font().family()
        
        fm=QFontMetrics(painter.font())
        while(fm.width(nstr)>=plotwidth/(scalex*1.3)):
            
            newfont=QFont(family,newsize-1)
            fm=QFontMetrics(newfont)
            newsize-=1
            
            
        print fm.width(nstr),plotwidth/scalex
        
        painter.setFont(QFont(family,newsize))
        
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight
        painter.drawText(x,y,nstr)
        
        painter.setFont(QFont(family,oldsize))
        
#paint kspace
        tempcolor=QColor(self.kspace.plot.canvasBackground())
        self.kspace.plot.setCanvasBackground(Qt.white)
            
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.kspace.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.kspace.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
        x=xmargin
        y=ymargin+fontheight+ypadding+plotheight+fontheight+2*ypadding+plotheight+fontheight
        painter.drawText(x,y,kstr)
        
#paint rspace

        tempcolor=QColor(self.fft.plot.canvasBackground())
        self.fft.plot.setCanvasBackground(Qt.white)
            
        x=xmargin+plotwidth+2*xpadding
        y=ymargin+fontheight+ypadding+plotheight+fontheight+ypadding*2
        self.fft.plot.printPlot(painter,QRect(x,y,plotwidth,plotheight))
        self.fft.plot.setCanvasBackground(tempcolor)
        
        painter.drawRect(x-xpadding,y-ypadding/2,plotwidth+xpadding,plotheight+fontheight+fontleading+ypadding)
        
#paint comments

        yoffset=xmargin+fontheight+ypadding+plotheight+fontheight+ypadding*1.5+plotheight+ypadding+fontheight+ypadding
        
        for line in self.comments:
            painter.drawText(xmargin,yoffset,line)
            yoffset+=(fontheight+fontleading)
        
    def editParameters(self):
        xdata=self.raw.xdata
        if(len(xdata)==0):
            errstr="There doesn't appears to be any data"
            QMessageBox.critical(self,QString("Error"),QString(errstr))
            return
        edgeDialog=EdgeDialog()
        edgeDialog.slotCheckBoxToggled(True)
        edgeDialog.checkBox1.setChecked(True)
        edgeDialog.setTitle(self.title)
        edgeDialog.setValue(self.E0)
        
        result=edgeDialog.exec_()
        
        if(result==QDialog.Rejected):
            return
            
        self.E0=edgeDialog.getValue()
        self.title=edgeDialog.getTitle()
        
        
        #check to see if E0 is reasonable!!
        while((self.E0 < xdata[0]) or (self.E0 > xdata[-1])):
            #for some reason, in windows, the str version used wasn't the
            #builtin version to convert between numbers and strings
            errstr="There appears to be a problem with E0="+__builtins__.str(self.E0)+". This value does not fall in the range of your data."
            QMessageBox.critical(self,QString("Error with E0"),QString(errstr))

            result=edgeDialog.exec_()
            if(result==QDialog.Rejected):
                return
                
        self.E0=edgeDialog.getValue()
        self.title=edgeDialog.getTitle()
        self.norm.plot.addBoundsExceptions(0,0,self.E0)
        pos=calc.getClosest(self.E0,xdata)
        self.norm.plot.knots[0].setPosition(pos)
        
        kmax=calc.toKSpace(xdata[-1],self.E0)
        kmin=calc.toKSpace(pos,self.E0)
        self.kspace.plot.resetPlot()
        
        self.setupXAFSPlot(kmax,kmin,kmax)
        
        #self.kdata,self.k0index=self.calcKSpace(self.xdata)
        self.updateNormPlot()
            
    def editComments(self):
        com=Comments()
        
        mystring=""
        for comment in self.comments:
            mystring+=comment
            mystring+="\n"
        
        com.textEdit1.setPlainText(QString(mystring))
        result=com.exec_()
        
        if(result==QDialog.Rejected):
            return
            
        text=com.textEdit1.toPlainText()
        self.comments=[]
        for line in text.toLatin1().split("\n"):
            self.comments.append(line)
        
    def fileExit(self):
        self.close()

##    def helpIndex(self):
##        print "Form1.helpIndex(): Not implemented yet"
##
##    def helpContents(self):
##        print "Form1.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "about button clicked"
        self.box=AboutBox()
        self.box.show()
        
    def updateNormPlot(self):
        #norm plot
        tempnorm=[]
        ydata=self.raw.ydata
        xdata=self.raw.xdata
        background=self.raw.background
        for i in range(len(ydata)):
            tempnorm.append(ydata[i]-background[i])
        self.norm.setNormData(xdata,tempnorm,self.E0)
        self.norm.updatePlot()
        
    def updateXAFSPlot(self):
        if(len(self.raw.xdata)==0):
            return
        
        self.kspace.clearFixedKnots()
        
        normknots=self.norm.plot.knots
        
        for knot in normknots[:-1]:
            
            pos=knot.getPosition()
            kpos=calc.toKSpace(pos,self.E0)
            self.kspace.addFixedKnot(kpos)
            
        pos=normknots[-1].getPosition()
        kpos=calc.toKSpace(pos,self.E0)
        self.kspace.addFixedKnot(kpos)
        
        xdata=self.raw.xdata
        normdata=self.norm.normdata
        splinedata=self.norm.splinedata
        
        #generate kdata
        kdata=[]
        for x in xdata:
            kdata.append(calc.toKSpace(x,self.E0))
        
        
        k0index=0
        while(xdata[k0index]<self.E0):
            k0index+=1
        self.kspace.setXAFSData2(normdata[k0index:],splinedata[k0index:],kdata[k0index:])
        self.updatefftPlot()
        
    def updatefftPlot(self):
        
        knots=self.kspace.plot.knots
        kmin=knots[0].getPosition()
        kmax=knots[1].getPosition()
        
        kdata=self.kspace.kdata
        xafsdata=self.kspace.xafsdata
        
        fftdata,fftRdata,fftIdata,DR=calc.calcfft(kdata,xafsdata,kmin,kmax,self.fft.currentWindowName)
        
        rdata=[]
        for i in range(len(fftdata)):
            rdata.append(i*DR)
            
        self.fft.setfftData(rdata,fftdata,fftRdata,fftIdata)
        
    
    def message(self,string):
            self.statusBar().message(string)
            
    def __tr(self,s,c = None):
        return qApp.translate("Form1",s,c)
        
    def initActions(self):
        print "initActions"
        self.fileImportAction = QAction(self)
        #self.fileImportXMUAction = QAction(self)
        self.fileOpenAction = QAction(self)
        self.fileOpenAction.setIcon(QIcon(self.image1))
        
        self.fileSaveAction = QAction(self)
        self.fileSaveAction.setIcon(QIcon(self.image2))
        self.fileSaveAsAction = QAction(self)
        self.fileExportfftAction = QAction(self)
        
        #self.filePrintAction = QAction(self)
        #self.filePrintAction.setIcon(QIcon(self.image3))
        self.fileExitAction = QAction(self)
        
        self.editParametersAction = QAction(self)
        self.editCommentsAction = QAction(self)
        
        self.windowNormAction = QAction(self)
        self.windowNormAction.setCheckable(True)
        self.windowNormAction.setChecked(True)
        
        self.windowXAFSAction = QAction(self)
        self.windowXAFSAction.setCheckable(True)
        self.windowXAFSAction.setChecked(True)
        
        self.windowfftAction = QAction(self)
        self.windowfftAction.setCheckable(True)
        self.windowfftAction.setChecked(True)
        
        #self.windowI0Action = QAction(self)
        #self.windowI0Action.setCheckable(True)
        #self.windowI0Action.setChecked(False)
        
        #self.helpContentsAction = QAction(self,"helpContentsAction")
        #self.helpIndexAction = QAction(self,"helpIndexAction")
        self.helpAboutAction = QAction(self)


#        self.toolBar = self.addToolBar("File")
#        self.toolBar.addAction(self.fileOpenAction)
#        self.toolBar.addAction(self.fileSaveAction)
#        self.toolBar.addSeparator()
#        self.toolBar.addAction(self.filePrintAction)


        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.fileImportAction)
        #self.fileMenu.addAction(self.fileImportXMUAction)
        self.fileMenu.addAction(self.fileOpenAction)
        self.fileMenu.addAction(self.fileSaveAction)
        self.fileMenu.addAction(self.fileSaveAsAction)
        self.fileMenu.addAction(self.fileExportfftAction)
        #self.fileMenu.addAction(self.filePrintAction)
        self.fileMenu.addAction(self.fileExitAction)

        self.editMenu = self.menuBar().addMenu("&Edit")        
        self.editMenu.addAction(self.editParametersAction)
        self.editMenu.addAction(self.editCommentsAction)
        
        self.windowMenu = self.menuBar().addMenu("&Windows")        
        self.windowMenu.addAction(self.windowNormAction)
        self.windowMenu.addAction(self.windowXAFSAction)
        self.windowMenu.addAction(self.windowfftAction)
        #self.windowMenu.addAction(self.windowI0Action)


        
        #self.helpMenu = QMenu("Help",self)
        self.helpMenu = self.menuBar().addMenu("&Help")        
##        self.helpContentsAction.addTo(self.helpMenu)
##        self.helpIndexAction.addTo(self.helpMenu)
##        self.helpMenu.insertSeparator()
        self.helpMenu.addAction(self.helpAboutAction)
        #self.helpAboutAction.addTo(self.helpMenu)
        #self.MenuBar.insertItem(QString("Help"),self.helpMenu,4)
        #self.MenuBar.addMenu(self.helpMenu)
        self.languageChange()

        self.resize(QSize(644,630).expandedTo(self.minimumSizeHint()))
        #self.clearWState(Qt.WState_Polished)

        self.connect(self.fileOpenAction,SIGNAL("triggered()"),self.fileOpen)
        self.connect(self.fileImportAction,SIGNAL("triggered()"),self.fileImport)
        #self.connect(self.fileImportXMUAction,SIGNAL("triggered()"),self.fileImportXMU)
        self.connect(self.fileSaveAction,SIGNAL("triggered()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("triggered()"),self.fileSaveAs)
        self.connect(self.fileExportfftAction,SIGNAL("triggered()"),self.exportFourier)
        #self.connect(self.filePrintAction,SIGNAL("triggered()"),self.filePrint)
        self.connect(self.fileExitAction,SIGNAL("triggered()"),self.fileExit)
        
        self.connect(self.editParametersAction,SIGNAL("triggered()"),self.editParameters)
        self.connect(self.editCommentsAction,SIGNAL("triggered()"),self.editComments)
        
        self.connect(self.windowNormAction,SIGNAL("toggled(bool)"),self.norm.setShown)
        self.connect(self.norm,SIGNAL("closed()"),self.slotWindowNormActionToggled)
        
        self.connect(self.windowXAFSAction,SIGNAL("toggled(bool)"),self.kspace.setShown)
        self.connect(self.kspace,SIGNAL("closed()"),self.slotWindowXAFSActionToggled)
        
        self.connect(self.windowfftAction,SIGNAL("toggled(bool)"),self.fft.setShown)
        self.connect(self.fft,SIGNAL("closed()"),self.slotWindowfftActionToggled)
        
        #self.connect(self.windowI0Action,SIGNAL("toggled(bool)"),self.i0.setShown)
        #self.connect(self.i0,SIGNAL("closed()"),self.slotWindowI0ActionToggled)
        
        ##self.connect(self.helpIndexAction,SIGNAL("triggered()"),self.helpIndex)
        ##self.connect(self.helpContentsAction,SIGNAL("triggered()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("triggered()"),self.helpAbout)


    def closeEvent(self,e):
        self.norm.close()
        self.kspace.close()
        self.fft.close()
        e.accept()
        
    def slotWindowNormActionToggled(self):
            self.windowNormAction.setChecked(False)
            
    def slotWindowXAFSActionToggled(self):
            self.windowXAFSAction.setChecked(False)
            
    def slotWindowfftActionToggled(self):
            self.windowfftAction.setChecked(False)
            
    def slotWindowI0ActionToggled(self):
        self.windowI0Action.setChecked(False)
            
    def languageChange(self):
        self.setWindowTitle(self.__tr("Raw Data"))
        
        self.fileImportAction.setText(self.__tr("Import Raw Data (Format: Energy,Mu)"))
       # self.fileImportXMUAction.setText(self.__tr("Import Athena mu(E) file"))
        self.fileOpenAction.setText(self.__tr("Open"))
        self.fileSaveAction.setText(self.__tr("Save"))
        self.fileSaveAsAction.setText(self.__tr("Save As"))
        self.fileExportfftAction.setText(self.__tr("Export Fourier Transform..."))
        #self.filePrintAction.setText(self.__tr("Print"))
        self.fileExitAction.setText(self.__tr("Exit"))
        self.editParametersAction.setText(self.__tr("Parameters..."))
        self.editCommentsAction.setText(self.__tr("Comments..."))
        #set text of windows menu
        self.windowNormAction.setText(self.__tr("&Normalized Data"))
        self.windowXAFSAction.setText(self.__tr("&EXAFS"))
        self.windowfftAction.setText(self.__tr("&Fourier Transform"))
        #self.windowI0Action.setText(self.__tr("I0 Data"))
        #self.fileExitAction.setAccel(QString.null)
        #self.helpContentsAction.setText(self.__tr("Contents"))
        #self.helpContentsAction.setMenuText(self.__tr("&Contents..."))
        #self.helpContentsAction.setAccel(QString.null)
        #self.helpIndexAction.setText(self.__tr("Index"))
        #self.helpIndexAction.setMenuText(self.__tr("&Index..."))
        #self.helpIndexAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("About"))
        #self.helpAboutAction.setMenuText(self.__tr("&About"))
        #self.helpAboutAction.setAccel(QString.null)
        #self.toolBar.setText(self.__tr("Tools"))
        
 
   
