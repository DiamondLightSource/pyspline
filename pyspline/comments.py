#!/usr/bin/env python
# comments.py -- a class implementing a dialog for adding comments

# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

#generated using Qt Designer

import sys
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

#from qt import *


class Comments(QDialog):
    def __init__(self,parent = None):
        QDialog.__init__(self,parent)
	self.setModal(True)
        self.setObjectName("Comments")
	self.setWindowTitle("Comments")
        self.setMaximumSize(QSize(460,240))
        CommentsLayout = QGridLayout(self)

        try:
            self.textEdit1 = QTextEdit(self)
            self.textEdit1.setObjectName("textEdit1")
        except NameError:
            self.textEdit1 = QMultiLineEdit(self)
            self.textEdit1.setObjectName("textEdit1")
        
        CommentsLayout.addWidget(self.textEdit1,0,0,3,2)

        self.okButton = QPushButton("Ok")
        CommentsLayout.addWidget(self.okButton,0,2)
        self.cancelButton = QPushButton("Cancel")
        CommentsLayout.addWidget(self.cancelButton,1,2)
        spacer1 = QSpacerItem(251,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        #CommentsLayout.addItem(spacer1,2,2)

        #self.languageChange()

        self.resize(QSize(460,233).expandedTo(self.minimumSizeHint()))
        #self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.reject)
	self.setLayout(CommentsLayout)


    def languageChange(self):
        self.setCaption(self.__tr("Edit Comments..."))
        self.cancelButton.setText(self.__tr("&Cancel"))
        #self.cancelButton.setAccel(self.__tr("Alt+C"))
        self.okButton.setText(self.__tr("&OK"))
        #self.okButton.setAccel(self.__tr("Alt+O"))


    def __tr(self,s,c = None):
        return qApp.translate("Comments",s,c)

if(__name__=='__main__'):
	app=QApplication(sys.argv)
	comments=Comments()
        comments.show()
        app.exec_()
	#app.setMainWidget(comments)
#	result=comments.exec_loop()
	
#	if(result==QDialog.Rejected):#
#		print "Rejected!!"
#	elif(result==QDialog.Accepted):
#		text=comments.textEdit1.text()
#		print text.latin1().split("\n")
