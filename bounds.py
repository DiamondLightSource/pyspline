#!/usr/bin/env python
# bounds.py -- the bounds algorithm used to calculate the matrix
#    needed to solve least squares with constraints
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from numpy import *
import string
from time import time

KEV=0.5123143

def bounds(xdata,ydata,segments,e0):

    if(len(xdata)!=len(ydata)):
        print "Xdata and Ydata need same order!"
        return None,None
    #print 'c1',time()
    #get total number of a_i
    size=0
    for i in segments:
        size=size+i[0]
        
    seg_size=len(segments)
    
    n=size+2*seg_size-2
    # Calculate some arrays in advance to save calculation time...
    # k3 weighting...should I adjust with k selection... in XAFS plot..???..
    mykdata=[]
    for x in xdata:
       mykdata.append(pow(toKSpace(x,e0),3.0))
    
    matrix=zeros([n,n])
    vec=zeros([n])
    
    cur_pos=0 #which column do we start in?
    temp=0
    lenxdata=len(xdata)
    # Calculate some arrays in advance to save calculation time...    	
    # Work maximum of loop over rows, columns (segements)
    # then calculate arrays used in advance
    # Means only do calculation a few times....
    xpower_row=[]
    mymax=segments[0][0]
    for arr in segments:
	if(arr[0] > mymax):
		mymax=arr[0]
		
    for i in range(2*mymax-1):
            xpower_temp=[]
            for j in range(lenxdata):
                xpower_temp.append(pow(xdata[j],i)*mykdata[j])
            xpower_row.append(xpower_temp)    
        
    for arr in segments:
    
        lindex=xdata.index(arr[1])
        hindex=xdata.index(arr[2])
        xllindex=xdata[lindex]
        xhhindex=xdata[hindex]
        tempx=0
        tempy=0
        #print 'arr[0]',arr[0]
        #print 'arr',arr,arr[0],lindex,hindex
        for row in range(arr[0]):
            tempx=0
            tempy=0
            for col in range(arr[0]):
                tempy=0
                tempx=0
                #sum of powers of x, depending on row and column
                for i in range(lindex,hindex+1):
                    tempx=tempx+xpower_row[row+col][i]
                    tempy=tempy+xpower_row[row][i]*ydata[i]
                matrix[cur_pos+row][cur_pos+col]=tempx
                vec[cur_pos+row]=tempy
            
            if(arr==segments[-1] and arr==segments[0]):
                continue #only 1 segment present, so there are no lagrange multiplier conds
            #calc lagrange multiplier columns for da_i    
            #l1 and l2 are 0th and 1st deriv conditions for previous segment
            #r1 and r2 are 0th and 1st deriv conds for subsequent segment
            if(row==0):
                templ1=0
                tempr1=0
                templ2=-0.5
                tempr2=0.5
            elif(row==1):
                templ1=-0.5
                tempr1=0.5
                templ2=-0.5*pow(xllindex,row)
                tempr2=0.5*pow(xhhindex,row)
            else:
                templ1=-0.5*pow(xllindex,row-1)*row
                tempr1=0.5*pow(xhhindex,row-1)*row
                templ2=-0.5*pow(xllindex,row)
                tempr2=0.5*pow(xhhindex,row)
                
            if(arr==segments[-1]): #no right hand bnd conds on last seg, but need left hand
                matrix[cur_pos+row][cur_pos-2]=templ1 #0th deriv
                matrix[cur_pos+row][cur_pos-1]=templ2 #1st deriv
            elif(arr==segments[0]): #no left hand bnd cond on first seg
                matrix[cur_pos+row][cur_pos+arr[0]]=tempr1
                matrix[cur_pos+row][cur_pos+arr[0]+1]=tempr2
            else: #remaining columns have both left and right hand bnds
                matrix[cur_pos+row][cur_pos+arr[0]]=tempr1
                matrix[cur_pos+row][cur_pos+arr[0]+1]=tempr2
                matrix[cur_pos+row][cur_pos-2]=templ1
                matrix[cur_pos+row][cur_pos-1]=templ2
            
        if(arr==segments[-1] and arr==segments[0]):
                continue #only 1 segment
        
        for cols in range(arr[0]):
        
            if(arr==segments[-1]): #last segment doesn't need bottom (high) bnd conds
                matrix[cur_pos-2][cur_pos+cols]=pow(xllindex,cols) #norm
                matrix[cur_pos-1][cur_pos+cols]=pow(xllindex,cols-1)*cols #deriv
            elif(arr==segments[0]): #first segment doesn't need top (low) bnd conds
                matrix[cur_pos+arr[0]][cur_pos+cols]=-1.0*pow(xhhindex,cols)
                matrix[cur_pos+arr[0]+1][cur_pos+cols]=-1.0*pow(xhhindex,cols-1)*cols
            else: #middle segments need both top and bottom bnd conds
                matrix[cur_pos+arr[0]][cur_pos+cols]=-1.0*pow(xhhindex,cols)
                matrix[cur_pos+arr[0]+1][cur_pos+cols]=-1.0*pow(xhhindex,cols-1)*cols
                matrix[cur_pos-2][cur_pos+cols]=pow(xllindex,cols)
                matrix[cur_pos-1][cur_pos+cols]=pow(xllindex,cols-1)*cols
        cur_pos=cur_pos+arr[0]+2 #2 for the cond spots
        
    return matrix,vec
    

def toKSpace(x,e0):
    if(x<e0):
        return 0
    else:
        return KEV*sqrt(x-e0)
        

    
