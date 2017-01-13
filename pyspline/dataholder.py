#
# A central data container....
# Holds various information about a data set and
# its display options. Also does the calculations etc.
# 
# This effectively seperates the data from the plots which makes
# things a bit cleaner and more obvious as to what happens to data
# Basically the GUIs set and change values like kmin etc. but all the data
# processing is handled by the DataHolder and Calc classes...
#
# also paves the way for holding multiple files in pyspline...
#
class DataHolder:

        def __init__(self):
                self.energy=[]
                self.kdata=[]
                self.rdata=[]
                self.mu=[]
                self.norm=[]
                self.background=[]
                self.spline=[]
                self.fftMag=[]
                self.fftReal=[]
                self.fftImag=[]
                self.chi=[]
                self.kmin=1
                self.kmax=12
                self.kweight=3
                self.segs=[]
                self.E0=0.0
                self.DR=0.05
               	self.windowNames=['hanning', 'hamming', 'bartlett', 'blackman','kaiser','flat']
                self.fftWindow="hanning"
                
        #
        # Return the k,chi data sets
        #
        def getChiData(self):
                return self.kdata,self.chi
                

        #
        # Return the k,chi data sets
        #
        def getFFTData(self):
                return self.rdata,self.fft
                

        #
        # Return the k,chi data sets
        #
        def getNormData(self):
                return self.energy,self.norm
                
        #
        # Return the k,chi data sets
        #
        def getMuData(self):
                return self.energy,self.mu

        #
        #
        # Update the knots...updates the other data sets
        #
        #
        def setKnots(self,knots):
                self.updateSpline()
                self.updateChi()
                self.updateFFT()
                
        #
        # 
        # Update the k range
        # updates the fft data accordingly
        #
        def setKRange(self,kmin,kmax):
                self.kmin=kmin
                self.kmax=kmax                
                self.updateFFT()


        #
        # Update the k data
        # ...depends on E0 position
        #
        def updateKdata(self):
                #generate kdata
                self.kdata=[]
                for x in self.energy:
                        self.kdata.append(calc.toKSpace(x,self.E0))
                # update the chi data                                
                self.updateChi()
                # update the fft data                        
                self.updateFFT()                                        
                        

        def updateChi(self):
                self.chi=calc.calcXAFS2(self.norm,self.spline,self.kdata,self.kweight)
                
        def updateFFT(self):
                self.fftMag,self.fftReal,self.fftImag,self.DR=calc.calcfft(self.kdata,self.chi,self.kmin,self.kmax,self.fftWindow)
                # Update the r data
                self.rdata=[]
                for i in range(len(fftMag)):
                        self.rdata.append(i*self.DR)                
                    
                
        def updateSpline(self):
                self.fftMag,self.fftReal,self.fftImag,self.DR=calc.calcfft(self.kdata,self.chi,self.kmin,self.kmax,self.fftWindow)


                
        
                
