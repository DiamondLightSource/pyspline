#!/usr/bin/env python

# edge.py -- the edge  class used for selecting the element, edge, and E0
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#Generated with the help of Qt designer

from PyQt4.Qt import *
from PyQt4.Qwt5 import *

#from qt import *
import sys


haveFile=True

#check to see if we have it
try:
    myfile=open("edges.dat")
except IOError:
    print 'edges.dat not found'
    haveFile=False
    
if haveFile:
    #skip header
    line=myfile.readline()
    
    data={}
    #each line contains one element and it's edges:energies
    line=myfile.readline()
    while(line):
        arr=line.split()
        edges={}
        for edge in arr[1:]:
            info=edge.split(":")
            edges[info[0]]=float(info[1])
        data[arr[0]]=edges
        line=myfile.readline()
    myfile.close()
    
else:
    data={
    'Chlorine': {'K':2840.0},
    'Chromium': {'K':6005.0},
    'Cobalt': {'K': 7725.0},
    'Copper': {'K': 9000.0},
    'Iron': {'K': 7130.0},
    'Manganese': {'K': 6555.0},
    'Molybdenum': {'K':20025.0, 'L3':2530.0, 'L2':2640.0},
    'Sulfur': {'K':2490.0},
    'Titanium': {'K': 4985.0},
    'Zinc': {'K': 9680.0}
    }




class EdgeDialog(QDialog):
    def __init__(self,parent = None):
        QDialog.__init__(self,parent)

        self.setModal(1)
        self.setMaximumSize(QSize(300,300))

        edgeLayout = QGridLayout()
        self.setLayout(edgeLayout)

        self.elementBox = QComboBox(self)
        #0,self,"comboBox1"
        edgeLayout.addWidget(self.elementBox,0,1)

        self.edgeBox = QComboBox(self)
        self.edgeBox.setEditable(0)
        #self.edgeBox.setSizeLimit(4)
        edgeLayout.addWidget(self.edgeBox,1,1)

        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setEnabled(0)
        edgeLayout.addWidget(self.lineEdit1,2,1)

        self.eleLabel = QLabel(self)
        edgeLayout.addWidget(self.eleLabel,0,0)

        self.edgeLabel = QLabel(self)
        edgeLayout.addWidget(self.edgeLabel,1,0)

        self.energyLabel = QLabel(self)
        edgeLayout.addWidget(self.energyLabel,2,0)

        self.titleLabel = QLabel(self)
        edgeLayout.addWidget(self.titleLabel,4,0)
        
        self.titleEdit = QLineEdit(self)
        edgeLayout.addWidget(self.titleEdit,4,1)
        
        self.checkBox1 = QCheckBox(self)
        edgeLayout.addWidget(self.checkBox1,3,1)
        
        self.okButton = QPushButton(self)
        self.okButton.setText("Ok")
        self.cancelButton = QPushButton(self)
        self.okButton.setText("Cancel")        
        hlayout=QHBoxLayout()
        hlayout.addWidget(self.okButton)
        hlayout.addWidget(self.cancelButton)
    
        edgeLayout.addLayout(hlayout,5,1)
        
        self.languageChange()

        self.resize(QSize(300,283).expandedTo(self.minimumSizeHint()))
        #self.clearWState(Qt.WState_Polished)

        self.initData()
        
        self.connect(self.elementBox,SIGNAL("activated(const QString&)"),self.elementChanged)
        self.connect(self.edgeBox,SIGNAL("activated(const QString&)"),self.edgeChanged)
        self.connect(self.checkBox1,SIGNAL("toggled(bool)"),self.slotCheckBoxToggled)
        self.connect(self.okButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.reject)

    def languageChange(self):
        self.setWindowTitle("Choose Edge...")
        self.eleLabel.setText("Element:")
        self.edgeLabel.setText("Edge:")
        self.energyLabel.setText("Energy:")
        self.titleLabel.setText("Title:")
        self.checkBox1.setText("Custom Energy Value")
        self.okButton.setText("&Ok")
        self.cancelButton.setText("&Cancel")

    def initData(self):
        keys = data.keys()
        keys.sort()

        for key in keys:
            self.elementBox.addItem(key)
        self.elementChanged(QString(keys[0]))

    def edgeChanged(self,edge):
    
        element=self.elementBox.currentText().toAscii()
        edges=data[str(element)]
        
        text=edges[str(edge)]
        self.lineEdit1.setText(str(text))
        
    
    def elementChanged(self,element):

        self.edgeBox.clear()
        edges=data[str(element)]
        for edge in edges.keys():
            self.edgeBox.addItem(edge)
            
        self.edgeChanged(QString(edges.keys()[0]))
        
    def setElementAndEdge(self,element,edge):
        index=self.elementBox.findText(QString(element))
        self.elementBox.setCurrentIndex(index)
        self.elementChanged(element)
        index=self.edgeBox.findText(QString(edge))
        self.edgeBox.setCurrentIndex(index)
        self.edgeChanged(edge)                
        
            
    def slotCheckBoxToggled(self,bool):
        
        element=self.elementBox.currentText().toAscii()
        self.elementChanged(QString(element))
        
        if not (bool):
            edge=self.edgeBox.currentText().toAscii()
            edges=data[element]
            text=edges[edge]
            
            self.lineEdit1.setText(str(text))
        
        self.lineEdit1.setEnabled(bool)
            
    def getValue(self):
        return float(self.lineEdit1.text().toAscii())
        
    def getTitle(self):
        return self.titleEdit.text().toAscii()
    
    def setTitle(self,title):
        
        self.titleEdit.setText(str(title))
        
    def setValue(self,val):
        
        text="%.3f"%(val,)
        self.lineEdit1.setText(text)
        
    def __tr(self,s,c = None):
        return qApp.translate("edge",s,c)

if(__name__=='__main__'):
	app=QApplication(sys.argv)
	edit=EdgeDialog()
	edit.show()
	app.exec_()

