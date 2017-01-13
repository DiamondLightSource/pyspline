#!/usr/bin/env python
# main.py -- the main PySpline class used for the program
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys

import pyspline
from pyspline import *

if(__name__=='__main__'):
    app=QApplication(sys.argv)
    mainwin=PySpline()
    mainwin.resize(600,400)
    
    #check to see if file was given on command line; if so, open it
    if(len(sys.argv)>=2):
    
        #assume 1st argument is filename, check if it exists
        if(exists(sys.argv[1])):
            mainwin.fileStringOpen(sys.argv[1])
            
    mainwin.show()
    app.exec_()
