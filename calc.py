# calc.py -- functions for calculating background, spline, etc using
#            passed parameters. Each function *should* be fully independent
#            of PySpline and its graphical interface, so a command-line 
#            interface ought to be nearly trivial to implement
#
# Copyright (c) Adam Tenderholt, Stanford University, 2004-2006
#                               a-tenderholt@stanford.edu
#
# This program is free software; you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from math import sqrt,pi,pow
from numpy import *
from bounds import *
from poly import *
from numpy import linalg
#from scipy import *
from numpy import fft
from time import time
import numpy
DR=0.05 #step size of R
fftPOINTS=1024 #number of fft points; works best if equal to 2^n
    
def getClosest(val,arr): #replace by bisecting sort later?
         
    xmin=0
    xmax=0
    
    if(val<=arr[0]):
        return arr[0]
    elif(val>=arr[-1]):
        return arr[-1]
    
    size=len(arr)
    
    for i in range(size-1):
        if(arr[i] <= val and val <= arr[i+1]):
            xmin=arr[i]
            xmax=arr[i+1]
            
    if(xmin==0 and xmax==0):
        if( val-arr[size-1] < val-arr[0]):
            return arr[size-1]
        else:
            return arr[0]
    
    if(val-xmin < xmax-val):
        return xmin
    else:
        return xmax
    
def calcBackground(xdata,ydata,lindex,hindex,order,E0):
    
    yfit=[]
    
    #build matrix used for least-squares
    #only half needs to be built since it's symmetric
    if(order>0):
    
        #build "empty" matrix so positions can be accessed by row and col
        matrix=array(range(order*order),dtype=float)
        matrix=reshape(matrix,(order,order))
    
        #build "empty" vector so positions can be accessed later
        vector=array(range(order),dtype=float)
        
        for row in range(order):
        
            for col in range(row,order):
            
                tempx=0
                for i in range(lindex,hindex+1):
                    tempx+=pow(xdata[i],row+col)
                
                matrix[row][col]=tempx
                matrix[col][row]=tempx
            
            tempy=0
            for i in range(lindex,hindex+1):
                tempy+=ydata[i]*pow(xdata[i],row)
            vector[row]=tempy
    
    elif(order==0): #ie, is for line of form y=a/x+b
        
        #variables used to build matrix and vector
        pos00=0
        pos01=0
        pos11=0
        y0=0
        y1=0
        
        for i in range(lindex,hindex+1):
            
            pos00+=1
            pos01+=(1/xdata[i])
            pos11+=pow(xdata[i],-2)
            y0+=ydata[i]
            y1+=(ydata[i]/xdata[i])
            
        matrix=array([[pos00,pos01],[pos01,pos11]])
        vector=array([y0,y1])
        
    else:
        print "Not implemented yet! Probably won't be either!"
        
    #coeffs = linalg.solve_linear_equations(matrix,vector)
    coeffs = linalg.solve(matrix,vector)

    
    background=[]
    for x in xdata:
    
        tempx=0
        
        if(order>0):
            for i in range(order):
                tempx=tempx+coeffs[i]*pow(x,i)
        elif(order==0): #actually of form y=a/x+b
            tempx=coeffs[0]+coeffs[1]/x
        else:
            "Not implemented"
            
            
        background.append(tempx)

    #if fit is above edge, adjust background
    if(xdata[hindex]>E0):
        value=min(ydata)
        index=ydata.index(value)
        minpoint=0
        
        #average value around min point in case there is noise
        #5 pts: index-2 index-1 index index+1 index+2
        
        #if that min point is too close to the beginning of data, forget lower part
        #else, do the 5pts
        if(index<2):
            for val in ydata[0:index+3]:
                minpoint+=val
            delta=background[index]-minpoint/len(ydata[0:index+3])
            
        else:
            for val in ydata[index-2:index+3]:
                minpoint+=val
            delta=background[index]-minpoint/len(ydata[index-2:index+3])
            
        for i in range(len(background)):
            background[i]=background[i]-delta
            
    return background

def calcSpline(xdata,ydata,E0,segs):
    #print 'z1bf',time()
    
    lowx=segs[0][1]
    order=segs[0][0]
    data=[]
    
    
    mat,vec=bounds(xdata,ydata,segs,E0)
  
    #handle singular matrices?
    try:
        #print 'z1',time()
        soln=linalg.solve(array(mat),array(vec))
        #print 'z2',time()
    except linalg.LinAlgError:
        print "The spline matrix is singular. Using single line as polynomial estimate"
        
        #Get first and last marker position and corresponding indexes of the xdata
        lowx=segs[0][1]
        highx=segs[-1][2]
        lindex=xdata.index(lowx)
        hindex=xdata.index(highx)
        
        #get y-values of the markers
        lowy=ydata[lindex]
        highy=ydata[hindex]
        
        slope=(highy-lowy)/(highx-lowx)
        
        for i in range(len(xdata)):
            dx=xdata[i]-lowx
            dy=slope*dx
            
            data.append(lowy+dy)
        
        return data
        
    #make polynomials
    #print 'z3',time()
    polys=[]
    offset=0
    
    for seg in segs:
        order=seg[0]
        
        coeffs=soln[offset:offset+order].tolist()
        
        poly=Polynomial(coeffs)
        polys.append(poly)
        
        offset=offset+order+2
        
    #generate individual spline data for pre-1st segment
    for i in range(0,xdata.index(lowx)): #interate through each point of pre-segment except last
        temp=polys[0].eval(xdata[i])
        data.append(temp)
    
    offset=0
    
    for i in range(len(segs)): #for each of the segments
        lowx=segs[i][1]
        highx=segs[i][2]
        lowindex=xdata.index(lowx)
        highindex=xdata.index(highx)
        
        #iterate through xdata bound by seg ranges
        for j in range(lowindex,highindex): #iterate through each point of segment except last one
        #for i in [0,1]:
            temp=polys[i].eval(xdata[j])
            data.append(temp)
            
        
    #print 'z4',time()        
    highx=segs[-1][2]
    order=segs[-1][0]
    
    for i in range(xdata.index(highx),len(xdata)):
        temp=polys[-1].eval(xdata[i])
        data.append(temp)    
        #data.append(1)
     
    sp_E0=polys[0].eval(E0)
    #print 'z5',time()
    return data,sp_E0
       
def calcXAFS(ydata,splinedata,kdata): #expect only ranges > E0 are given

    data=[]
    if not (len(ydata) == len(splinedata)):
        print "ydata and spline data are not same length"
        print len(ydata),len(splinedata)    
        return data
        
    if not (len(kdata) == len(ydata)):
        print "kdata is different length than ydata,splinedata"
        return data
            
    for i in range(len(ydata)):
        diff=(ydata[i]-splinedata[i])
        data.append(diff*pow(kdata[i],3))
        
    return data 

def calcXAFS2(ydata,splinedata,kdata,kweight): #expect only ranges > E0 are given

    data1=[]
    data2=[]
    if not (len(ydata) == len(splinedata)):
        print "ydata and spline data are not same length"
        print len(ydata),len(splinedata)    
        return data1
        
    if not (len(kdata) == len(ydata)):
        print "kdata is different length than ydata,splinedata"
        return data1
            
    for i in range(len(ydata)):
        diff=(ydata[i]-splinedata[i])
        data1.append(diff)
        data2.append(diff*pow(kdata[i],kweight))
        
    return data1,data2
#
#
# Fourier transform
#
#
def calcfft(kdata,k3xafsdata,kmin,kmax,windowType='hanning'):
    #calculate dk
    dk=pi/(fftPOINTS*DR)
    # 1/sqrt(pi)
    sqrtpi = 0.56418958350
    # Normalization
    cnorm = dk * sqrtpi
    index=0
    # Bin the data to a grid
    bindata=[]
    krange=arange(dk,kdata[-1],dk).tolist()
    for bin in krange:
        mysum=0
        for k in kdata[index:]: #only count from last bin
            if(k<bin): #if k falls into bin
                last=kdata.index(k)
                temp=k3xafsdata[last]
                mysum+=temp
            else:
                last=kdata.index(k) #first k that doesn't fall in bin
                break
        bindata.append(mysum*cnorm/(last-index+1))
        index=last
    # apply window
    index_kmin=nearest_x(kmin,krange)
    index_kmax=nearest_x(kmax,krange)
    
    window_len=index_kmax-index_kmin+1
    if not windowType in ['flat', 'hanning', 'hamming', 'bartlett','blackman']:
	windowType=='flat'
    if windowType == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('numpy.'+windowType+'(window_len)')
    for i in range(len(bindata)):
        if(i>=index_kmin and i<=index_kmax):    
                bindata[i]=bindata[i]*w[i-index_kmin]
        else:                
            bindata[i]=0.0
            

    # FFT    
    rawfftdata=fft.fft(bindata,fftPOINTS)
    conjfftdata=conjugate(rawfftdata)
    fftdata=sqrt(rawfftdata*conjfftdata).real
    fftlist=fftdata.tolist()
    data=[]
    realdata=[]
    imagdata=[]    
    for i in range(len(fftlist)/2):
        data.append((fftlist[i]+fftlist[-i])/2.0)
        realdata.append((rawfftdata.real[i]+rawfftdata.real[-i])/2.0)
        imagdata.append((rawfftdata.imag[i]-rawfftdata.imag[-i])/2.0)
    # Return magnitude, real and imaginary data
    return data,realdata,imagdata,DR
    
def simpleInterpolate(self,x,xdata,ydata):
    
    lindex=0
    hindex=len(xdata)
    
    while(hindex-lindex>1):
        mindex=(hindex+lindex)/2
        if(x < xdata[mindex]):
            hindex=mindex
        elif(x > xdata[mindex]):
            lindex=mindex
        
    slope=(ydata[hindex]-ydata[lindex])/(xdata[hindex]-xdata[lindex])
    
    dx=x-xdata[lindex]
    dy=dx*slope
    
    return ydata[lindex]+dy


def nearest_x(x,array):
        #
        #   return index in array with value closest to scalar x.
        #   arguments
        #   x      value to find in array  
        #   array  double precision array (monotonically increasing)
        #
        #
        # hunt by bisection
        imin = 0
        imax = len(array)-1
        inc = ( imax - imin ) / 2
        while(1):
                it  = imin + inc
                xit = array[it]
                if ( x < xit ):
                        imax = it
                elif ( x > xit ):
                        imin = it
                else:
                        nofx = it
                        return nofx
                inc = ( imax - imin ) / 2
                if ( inc <= 0 ): break
        # x is between imin and imin+1
        xave = ( array[imin] + array[imin+1])/2.0
        if ( x < xave ):
                nofx = imin
        else:
                nofx = imin + 1
        return nofx

def findNearestIndex(self,x,xdata,ydata):
    
    lindex=0
    hindex=len(xdata)
    
    while(hindex-lindex>1):
        mindex=(hindex+lindex)/2
        if(x < xdata[mindex]):
            hindex=mindex
        elif(x > xdata[mindex]):
            lindex=mindex
        
    slope=(ydata[hindex]-ydata[lindex])/(xdata[hindex]-xdata[lindex])
    
    dx=x-xdata[lindex]
    dy=dx*slope
    
    return ydata[lindex]+dy




def linear_interpolataiontrp(rawx, rawy, xgrid):
#
#    linear interpolation for use in loops where xin increases 
#    steadily through the monotonically increasing array x. 
#  arguments:
#     x      array of ordinate values                   [in]
#     y      array of abscissa values                   [in]
#     npts   length of arrays x and y                   [in]
#     xin    value of x at which to interpolate         [in]
#     ip     index such that x(ip) <= xin <= x(ip+1)    [in/out]
#     y      interpolated abscissa at xin               [out]
#  note: this routine is called extremely often 
#        -- anything to improve efficiency should be done
        tiny = 1.0e-9
#  find ip such that   x(ip) <= xin < x(ip+1)
#       hunt(x, npts, xin, ip)
#               yout=[]
#        for x in xgrid:
                               
 #      yout = y(ip) 
 #      if ((x(ip+1)-x(ip)) .gt. tiny)  yout = yout + (y(ip+1)-y(ip)) * (xin-x(ip)) / (x(ip+1)-x(ip))
        return

#  end subroutine lintrp


def toKSpace(x,e0):

    #temp=2.0*H_bar/Me*(x-e0)
    #return sqrt(temp)
    if(x<e0):
        return 0
    else:
        return KEV*sqrt(x-e0)
        
def fromKSpace(k,e0):

    if(k<0):
        return e0
    else:
        return pow(k/KEV,2)+e0
        
        
        
def smooth(x,window_len=10,window='hanning'):
#"""smooth the data using a window with requested size.
#  TAKEN FROM SCIPY COOKBOOK   
#  This method is based on the convolution of a scaled window with the signal.
#  The signal is prepared by introducing reflected copies of the signal 
#      (with the window size) in both ends so that transient parts are minimized
#      in the begining and end part of the output signal.
#      
#      input:
#          x: the input signal 
#          window_len: the dimension of the smoothing window
#          window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
#              flat window will produce a moving average smoothing.
#  
#      output:
#          the smoothed signal
#          
#      example:
#  
#      t=linspace(-2,2,0.1)
#      x=sin(t)+randn(len(t))*0.1
#      y=smooth(x)
#      
#      see also: 
#      
#      numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
#      scipy.signal.lfilter
#   
#      TODO: the window parameter could be the window itself if an array instead of a string   
#      """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')
        
    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]
    
#
#
#
# First derivative of x,y data set
# Returns dy/dx 
#
#
def deriv(x,y):
    # Make an array
    myarray = np.array(x,y)
    # Differences (xN-xN-1, yN-yN-1) etc...
    result=numpy.diff(myarray,n=1)
    # deltaY/deltaX
    result=result[1]/result[0]
    # convert to a python list and return
    return result.tolist()
        
#
#
# Sloped sigmoid function (basically a sigmoid on a sloping background
# A sigmoid should be the easiest to roughly find the edge of a data set 
#                
def sigmoid(x,*args):
        xdata=args[0]
        ydata=args[1]
        #print 'len',len(xdata),len(ydata)
        result=0.0
        for i in range(len(xdata)):
                result=result+(ydata[i]-(x[0]+x[1]/(1.0+exp((x[2]-xdata[i])/x[3]))))**2
        #print 'result',x,result        		
        return result
                
                
def fitedge(xdata,ydata):
        # find min,max
        ymin=min(ydata)
        ymax=max(ydata)                
        xmin=min(xdata)
        xmax=max(xdata)                
        x0=ymin,ymax,(xmax+xmin/2.0),5.0
        mybounds=[(ymin-(ymax-ymin)*0.3,ymin+(ymax-ymin)*0.3),(ymin,ymax*2.0),(xmin,xmax),(0.1,20.0)]
        #print 'bounds',mybounds
        result = optimize.fmin_l_bfgs_b(sigmoid, x0, args = (xdata,ydata), approx_grad = True, bounds = mybounds,iprint=1)
        #print 'result',result        
        
        
        def nearest_x(self,x,array):
                #
                #   return index in array with value closest to scalar x.
                #   arguments
                #   x      value to find in array  
                #   array  double precision array (monotonically increasing)
                #
                #
                # hunt by bisection
                imin = 1
                imax = len(array)-1
                inc = ( imax - imin ) / 2
                while(1):
                        it  = imin + inc
                        xit = array[it]
                        if ( x < xit ):
                                imax = it
                        elif ( x > xit ):
                                imin = it
                        else:
                                nofx = it
                                return nofx
                        inc = ( imax - imin ) / 2
                        if ( inc <= 0 ): break
                # x is between imin and imin+1
                xave = ( array[imin] + array[imin+1])/2.0
                if ( x < xave ):
                        nofx = imin
                else:
                        nofx = imin + 1
                return nofx

       
        def findee(energy, mu):
                #
                #   find ee of x-ray absorption data 
                #   (maximum deriv, with check that it is at least
                #    the third positive deriv in a row)
                # inputs :
                #   nxmu     length of array energy, xmu, and xmuout
                #   energy   array of energy points
                #   xmu      array of raw absorption points
                # outputs:
                #   ee       energy origin of data
                
                #
                # Fit a sigmoid to the data to 
                # determine the edge position (rough but pretty close)
                # Then fine scan over the edge to find the first inflection point 
                #
                #
                zero = 0.0
                tiny = 1.0e-9
                onepls = 1.00001
                ee  = energy[0]
                nxmu=len(mu)
                #print 'nxmu',nxmu
                if(nxmu<=8): return
                inc=[False]*3
                dxde  = zero
                demx  = zero
                ntry  = max(2, int(nxmu/2)) + 3
                #print 'ntry',ntry,ee
                # smooth it first....
                mu2 = numpy.array(mu)
                xmu=calc.smooth(mu2)
                for i in range(1, ntry):
                        deltae1  = energy[i] - energy[i-1]
                        deltae2  = energy[i+1] - energy[i]
                        deltae3  = energy[i+2] - energy[i+1]
                        dxde1   = (xmu[i] - xmu[i-1])/deltae1
                        dxde2   = (xmu[i+1] - xmu[i])/deltae2
                        dxde3   = (xmu[i+2] - xmu[i+1])/deltae3
                        if((dxde3>dxde2>dxde1) and dxde3 > 0.0 and dxde2 > 0.0 and dxde1 > 0.0):  
                                ee   = energy[i]
                                break
                return ee



                
                        
        def guess_iz(en,mu):
                #  given a spectra of mu(e), guess the atomic number based on
                #  edge position as found by findee
                #  only k and l shells are considered, though it could be expanded.
                #  data used is taken from mcmaster.
                #  args:
                #       en    array of energy      [in]
                #       mu    array of xmu         [in]
                #       npts  size of energy,xmu   [in]
                #       e0    guessed e0 value     [out]
                # returns:   
                #      iz     atomic number
                #
                edges = [0.014,0.025,0.049,0.050,0.055,0.063,\
         	0.072,0.073,0.087,0.099,0.100,0.112,0.118,0.135,0.136,0.153,\
 	        0.162,0.164,0.188,0.193,0.200,0.202,0.238,0.248,0.251,0.284,\
        	0.287,0.295,0.297,0.341,0.346,0.350,0.399,0.400,0.402,0.404,\
        	0.454,0.461,0.463,0.512,0.520,0.531,0.537,0.574,0.584,0.604,\
        	0.639,0.650,0.682,0.686,0.707,0.720,0.754,0.778,0.793,0.842,\
        	0.855,0.867,0.872,0.929,0.932,0.952,1.012,1.021,1.044,1.072,\
        	1.100,1.115,1.142,1.196,1.218,1.249,1.302,1.305,1.325,1.360,\
        	1.414,1.436,1.477,1.530,1.550,1.560,1.596,1.653,1.675,1.726,\
 	        1.782,1.805,1.839,1.863,1.920,1.940,2.007,2.065,2.080,2.149,\
         	2.156,2.216,2.223,2.307,2.371,2.373,2.465,2.472,2.520,2.532,\
        	2.625,2.677,2.698,2.793,2.822,2.838,2.866,2.967,3.003,3.043,\
        	3.146,3.173,3.202,3.224,3.330,3.351,3.412,3.524,3.537,3.605,\
        	3.607,3.727,3.730,3.806,3.929,3.938,4.018,4.038,4.132,4.156,\
        	4.238,4.341,4.381,4.465,4.493,4.557,4.612,4.698,4.781,4.852,\
        	4.939,4.965,5.012,5.100,5.188,5.247,5.359,5.452,5.465,5.483,\
        	5.624,5.713,5.724,5.891,5.965,5.987,5.989,6.165,6.208,6.267,\
        	6.441,6.460,6.540,6.549,6.717,6.722,6.835,6.977,7.013,7.112,\
        	7.126,7.243,7.312,7.428,7.515,7.618,7.709,7.737,7.790,7.931,\
        	8.052,8.071,8.252,8.333,8.358,8.376,8.581,8.648,8.708,8.919,\
                 8.943,8.979,9.047,9.244,9.265,\
        	9.395,9.561,9.618,9.659,9.752,9.881,9.978,10.116,10.204,\
        	10.349,10.367,10.488,10.534,10.739,10.870,10.871,11.104,\
         	11.136,11.215,11.272,11.542,11.564,11.680,11.868,11.918,\
        	11.957,12.098,12.284,12.384,12.525,12.657,12.658,12.824,\
        	12.964,13.035,13.273,13.418,13.424,13.474,13.733,13.892,\
        	14.209,14.322,14.353,14.612,14.698,14.846,15.198,15.200,\
        	15.344,15.708,15.860,16.105,16.300,16.385,17.080,17.167,\
         	17.334,17.998,18.053,18.055,18.986,19.692,19.999,20.470,\
        	20.947,21.045,21.756,22.117,22.263,23.095,23.220,24.350,\
        	25.514,26.711,27.940,29.200,30.491,31.813,33.169,34.582,\
        	35.985,37.441,38.925,40.444,41.991,43.569,45.184,46.835,\
        	48.520,50.240,51.996,53.789,55.618,57.486,59.390,61.332,\
        	63.314,65.351,67.414,69.524,71.676,73.872,76.112,78.395,\
        	80.723,83.103,85.528,88.006,90.527,98.417,109.649,115.603,\
 	        121.760]

                iedge=[1,2,12,12,3,12,13,13,13,14,14,4,14,\
                15,15,15,16,16,5,16,17,17,17,18,18,6,18,19,19,19,20,20,21,20,\
                7,21,22,22,21,23,23,22,8,24,24,23,25,25,24,9,26,26,25,27,27,\
                26,28,10,28,27,29,29,28,30,30,11,29,31,31,30,32,32,31,12,33,\
                33,32,34,34,33,35,13,35,34,36,36,35,37,14,37,36,38,38,37,39,\
                15,39,38,40,40,41,39,41,16,42,40,42,43,41,43,17,44,42,44,45,\
                43,45,46,18,44,46,47,45,47,48,46,19,48,49,47,50,49,48,20,51,\
                50,49,52,51,50,21,53,52,51,54,53,52,22,55,54,53,56,55,54,23,\
                57,56,55,58,57,59,56,24,58,60,57,59,61,25,58,62,60,59,63,61,\
                26,60,64,62,61,65,63,27,62,66,64,63,67,65,28,68,64,66,69,65,\
                67,70,29,66,71,68,67,72,69,30,68,73,70,69,74,71,31,70,75,72,\
                71,76,32,73,77,72,74,78,73,33,79,75,74,80,76,75,81,34,77,76,\
                82,78,83,77,35,79,78,80,36,79,86,81,80,82,37,81,83,82,38,90,\
                83,39,92,86,40,94,86,41,90,42,90,92,43,92,44,94,94,45,46,47,\
                48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,\
                68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,86,90,92,94]

                #  guess e0 from spectra 
                guess = 30
                e0=self.findee(en,mu)
                #  find closest energy in table
                ex = e0/1000.0
                guess = iedge[self.nearest_x(ex,edges)]
                return guess
        
        
        
    
