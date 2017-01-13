#//////////////////////////////////////////////////////////////////////
# I'm happy to acknowledge the edge determination algorithms
# findee, guess_iz and nofx have been reproduced, in python, from Matt
# Newvilles ifeffit code
# Copyright (c) 1997--2000 Matthew Newville, The University of Chicago
# Copyright (c) 1992--1996 Matthew Newville, University of Washington
#
# Permission to use and redistribute the source code or binary forms of
# this software and its documentation, with or without modification is
# hereby granted provided that the above notice of copyright, these
# terms of use, and the disclaimer of warranty below appear in the
# source code and documentation, and that none of the names of The
# University of Chicago, The University of Washington, or the authors
# appear in advertising or endorsement of works derived from this
# software without specific prior written permission from all parties.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THIS SOFTWARE.
#//////////////////////////////////////////////////////////////////////


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from ExclusiveModel import *
from random import randint
import numpy
#from scipy import *
from dataplot import *
#
#
# A class to help with importing data files
#
#
#
class DataImporter(QDialog):
	def __init__(self,parent = None):
		QDialog.__init__(self,parent)
		# Array which will hold the column data
		self.parentWindow=parent
		self.dataArray=[]
		self.numeratorList=[1]
		self.denominatorList=[2]
		self.energySelection=0
		self.energy=[]
		self.mu=[]
		self.edgeEnergy=7111.0
		self.atomicNumber=29
		self.elementName='Fe'
		self.elementEdge='K'
		# Window - widgets and layout
		self.setWindowTitle("Import Data")
		self.denominator_model = QStandardItemModel()
		self.numerator_model= QStandardItemModel()
		self.energy_model=ExclusiveModel()
		self.denominatorLabel = QLabel(self)
		self.denominatorLabel.setText("Denominator")
		self.denominator_view = QListView(self)
		self.denominator_view.setModel(self.denominator_model)
		self.denominator_view.setSelectionMode(QListView.NoSelection)
		self.numerator_view = QListView(self)
		self.numerator_view.setModel(self.numerator_model)
		self.numeratorLabel = QLabel(self)
		self.numeratorLabel.setText("Numerator")
		self.energy_view = QListView(self)
		self.energy_view.setModel(self.energy_model)
		self.energy_view.setSelectionMode(QListView.NoSelection)
		self.energyLabel = QLabel(self)
		self.energyLabel.setText("Energy")
		self.overalllayout= QVBoxLayout()
		#self.dataViewerLayout1 = QVBoxLayout()
		#self.fileLabel = QLabel(self)
		#self.fileLabel.setText("Data File")
		#self.dataViewerLayout1.addWidget(self.fileLabel)
		#self.overalllayout.addLayout(self.dataViewerLayout1)
		self.dataViewerLayout2 = QHBoxLayout()
		self.fileText = QTextEdit()
		self.fileText.setLineWrapMode(QTextEdit.NoWrap)
		self.previewPlot = DataPlot(QColor(Qt.black))
		#self.previewPlot.setAxisScale(QwtPlot.xBottom,0,100)
		self.previewCurve=self.previewPlot.insertCurve("Preview")
		self.tab_widget = QTabWidget()
		self.tab1Layout = QHBoxLayout()		
		self.tab1Layout.addWidget(self.fileText)
		self.tab_widget.addTab(self.fileText, "File contents")
		self.tab_widget.addTab(self.previewPlot, "Preview Plot")
		#self.dataViewerLayout2.addWidget(self.fileText)
		#self.dataViewerLayout2.addWidget(self.previewPlot)
		self.dataViewerLayout2.addWidget(self.tab_widget)
		self.overalllayout.addLayout(self.dataViewerLayout2)
		self.dataLoaderLayout = QGridLayout()
		self.dataLoaderLayout.addWidget(self.energyLabel,1,1)
		self.dataLoaderLayout.addWidget(self.numeratorLabel,1,2)
		self.dataLoaderLayout.addWidget(self.denominatorLabel,1,3)
		self.dataLoaderLayout.addWidget(self.energy_view ,2,1)
		self.dataLoaderLayout.addWidget(self.numerator_view,2,2)
		self.dataLoaderLayout.addWidget(self.denominator_view,2,3)
		self.overalllayout.addLayout(self.dataLoaderLayout)
		self.equationViewerLayout = QHBoxLayout()
		self.equationOption = QCheckBox(self)
		self.equationOption.setText("Natural Log")
		self.equationLabel = QLabel(self)
		self.equationLabel.setText("mu(E)")
		self.equationText = QLineEdit()
		self.equationText.setReadOnly(True)
		self.equationViewerLayout.addWidget(self.equationOption)
		self.equationViewerLayout.addWidget(self.equationLabel)
		self.equationViewerLayout.addWidget(self.equationText)
		numeratorstring,denomstring,logstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring,logstring)
		self.overalllayout.addLayout(self.equationViewerLayout)
		self.OK = QPushButton(self)
		self.OK.setText("OK")
		self.CANCEL = QPushButton(self)
		self.CANCEL.setText("CANCEL")
		self.okcancelLayout = QHBoxLayout()
		self.okcancelLayout.addWidget(self.OK)
		self.okcancelLayout.addWidget(self.CANCEL)
		self.overalllayout.addLayout(self.okcancelLayout)
		self.setLayout(self.overalllayout)
		# Signals and slots		
		self.connect(self.OK,SIGNAL("clicked()"),self.accept)
		self.connect(self.CANCEL,SIGNAL("clicked()"),self.reject)
		self.connect(self.denominator_model,SIGNAL("itemChanged( QStandardItem *)"),self.testit)
		self.connect(self.numerator_model,SIGNAL("itemChanged( QStandardItem *)"),self.testit)
		#self.connect(self.denominator_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.denominatorUpdate)
		#self.connect(self.numerator_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.numeratorUpdate)
		#self.connect(self.energy_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.energyUpdate)
		self.connect(self.equationOption,SIGNAL("stateChanged(int)"),self.testit)
		self.connect(self.energy_model,SIGNAL("itemChanged( QStandardItem *)"),self.energyUpdate)
		
	def testit(self,object1):
		#print 'update'
		numeratorstring,denomstring,logstring=self.constructEquationStrings()
		#print numeratorstring,denomstring
		self.updateEquation(numeratorstring,denomstring,logstring)
		#print 'checkeroo'
		#for row in range(self.denominator_model.rowCount()):
	#		item = self.denominator_model.item(row, 0)
	#		print item.checkState(),row

	#
	# Read in an ascii file containing columns of data
	#
	def loadFile(self,filename):
	        loadedok=True
	        # Read in the data
	        fin=open(filename,'r')
        	datalines=fin.readlines()
	        fin.close()
        	# 
	        comments=('#','!','-','%')
        	successive_dataLines=0
	        numberOfLines=len(datalines)
		#
		# Skip over the comments 
		# Expected comments to start with #,!,-,%
		#   
		startLine=0
        	for i in range(numberOfLines):
        	        # if it starts with comments cycle
			print datalines[i]
        	        if(datalines[i].strip().startswith(comments)):
				startLine=i+1
        	                continue
        	        else:
        	                break
		#
		# Ok..just cos I've skipped over the obvious comment indicators
		# doesn't mean I'm in the clear
		# Keep checking until I get 3 consequtive lines 
		# of column like data
		#
		newStartLine=startLine
		for i in range(startLine,numberOfLines-3,3):
			idata1,columns1=self.isColumnData(datalines[i])
			idata2,columns2=self.isColumnData(datalines[i+1])
			idata3,columns3=self.isColumnData(datalines[i+2])
			if((idata1 and idata2 and idata3) and (columns1==columns2==columns3)):
				newStartLine=i
				break
		for i in range(newStartLine,numberOfLines):
				dataf,datas=self.stringToFloatList(datalines[i])
				self.dataArray.append(dataf)
                if(len(self.dataArray[0])<2):
                        loadedok=False
                        return loadedok
		#
		# Paste the data into the data text viewer
		#
		for data in datalines:
			self.fileText.insertPlainText(data)
		self.fileText.moveCursor(QTextCursor.Start,QTextCursor.MoveAnchor)
		#self.fileText.moveCursor(QTextCursor.Start)
		#
		# Fill in the column data in the widget...
		#
		self.denominator_model.clear()
		self.numerator_model.clear()
		self.energy_model.clear()
		noOfColumns=len(self.dataArray[0])
		# Create list starting from 1 rather than 0
		for n in range(1,noOfColumns+1):                   
			item1 = QStandardItem('Column %s' % n)
			item1.setCheckable(True)
			item2 = QStandardItem('Column %s' % n)
			item2.setCheckable(True)
			item3 = QStandardItem('Column %s' % n)
			item3.setCheckable(True)
			self.denominator_model.appendRow([item1])
			self.numerator_model.appendRow([item2])
			self.energy_model.appendRow([item3])  
		# Set up some selections ...just so something is selected
		# and we have some defaults
		self.readPreferences()
		#if(noOfColumns==2):
		maxdenom=0
		if(len(self.denominatorList)>0):
			maxdenom=max(self.denominatorList)
		maxnumer=0
		if(len(self.numeratorList)>0):
			maxnumer=max(self.numeratorList)
			
		if(noOfColumns==2 or (maxnumer>noOfColumns) or (maxdenom>noOfColumns)):
			#self.numerator_view.selectionModel().setCurrentIndex(self.numerator_model.index(1,0),QItemSelectionModel.Select)
			#print 'here 2'
			self.energy_model.item(0, 0).setCheckState(Qt.Checked)
			self.numerator_model.item(1, 0).setCheckState(Qt.Checked)
			#self.denomitor_model.
		else:
			t1 = self.denominatorList
			t2 = self.numeratorList
			#print 'i am here',self.denominatorList,self.numeratorList,self.energySelection
			self.energy_model.item(self.energySelection, 0).setCheckState(Qt.Checked)
			for x in t2:
				#print x
				self.numerator_model.item(x, 0).setCheckState(Qt.Checked)
			print 'here b',len(self.denominatorList),len(self.numeratorList),self.denominatorList
			for x in t1:
				#print x
				self.denominator_model.item(x, 0).setCheckState(Qt.Checked)
			if(self.logcheck==1):
				self.equationOption.setCheckState(Qt.Checked)
		return loadedok

	def readPreferences(self):
		fin=open("formatPreferences.ini","r")
		preferences=fin.readlines()
		fin.close()
		datai,datas=self.stringToIntegerList(preferences[0])
		self.energySelection=datai[0]
		datai,datas=self.stringToIntegerList(preferences[1])
		self.numeratorList=datai
		datai,datas=self.stringToIntegerList(preferences[2])
		self.denominatorList=datai
		datai,datas=self.stringToIntegerList(preferences[3])
		self.logcheck=datai[0]
		#print 'self.logcheck',self.logcheck
		#print self.denominatorList,self.numeratorList,self.energySelection
		
	def writePreferences(self):
		fout=open("formatPreferences.ini","w")
		print >>fout,"Energy",self.energySelection
		print >>fout,"Numerator",str(self.numeratorList[0:]).strip('[]').replace(',','')
		print >>fout,"Denominator",str(self.denominatorList[0:]).strip('[]').replace(',','')
		if(self.equationOption.isChecked()):
			print >>fout,"Log",1
		else:
			print >>fout,"Log",0
		fout.close()
		

		

	#
	# Push the ok button
	# process the columns and send to main widget...
	#
	def accept(self):
		# Return mu based on selection
		#print self.denominatorList
		#print self.numeratorList
		self.writePreferences()
		self.mu=[]
		self.energy=[]
		for i in range(len(self.dataArray)):
			mydenominator_sum=0.0
			mynumerator_sum=0.0
			if(len(self.denominatorList)==0):
				mydenominator_sum=1.0
			else:
				for j in self.denominatorList:
					mydenominator_sum=mydenominator_sum+self.dataArray[i][j]
			if(len(self.numeratorList)==0):
				mynumerator_sum=1.0
			else:
				for j in self.numeratorList:
					mynumerator_sum=mynumerator_sum+self.dataArray[i][j]
			self.energy.append(self.dataArray[i][self.energySelection])
			# Check not dividing by zero
			if(mydenominator_sum==0.0):
				self.mu.append(0.0)
			else:
				# Natural log
				if(self.equationOption.isChecked()):
					self.mu.append(math.log(mynumerator_sum/mydenominator_sum))
				else:
					self.mu.append(mynumerator_sum/mydenominator_sum)
                self.atomicNumber,self.elementName,self.elementEdge=self.guess_iz(self.energy,self.mu)
                QDialog.accept(self)

        #
        # Return the energy and mu data
        #         
        def getData(self):
                return self.energy,self.mu,self.elementName,self.elementEdge

	#
	# Push the cancel button
	#
	def reject(self):
		QDialog.reject(self)
	#
	# Based on the selected columns construct a string
	# showing the equation which will be used to construct
	# mu
	#
	def constructEquationStrings(self):
		logstring=""
		self.tempdenominatorList=[]
		for row in range(self.denominator_model.rowCount()):
			item = self.denominator_model.item(row, 0)
			if(item.checkState()>0):
				self.tempdenominatorList.append(row)
#		print 'length',self.denominatorList,len(self.denominatorList)
		if(len(self.tempdenominatorList)==0):
			denomstring='1'
#			print 'its empty'
		else:
			denomstring='('
			for value in self.tempdenominatorList:
				denomstring=denomstring+"col("+str(value+1)+")"+"+"
			denomstring=denomstring.rstrip("+")
			denomstring=denomstring+")"
#		print 'denomstring',denomstring
		#
		# Numerator line
		# 
		self.tempnumeratorList=[]
		for row in range(self.numerator_model.rowCount()):
			item = self.numerator_model.item(row, 0)
			if(item.checkState()>0):
				self.tempnumeratorList.append(row)
		if(len(self.tempnumeratorList)==0):
			numeratorstring='1'
		else:
			numeratorstring='('
			for value in self.tempnumeratorList:
				numeratorstring=numeratorstring+"col("+str(value+1)+")"+"+"
			numeratorstring=numeratorstring.rstrip("+")
			numeratorstring=numeratorstring+")"
		self.mu=[]
		self.energy=[]
		for i in range(len(self.dataArray)):
			mydenominator_sum=0.0
			mynumerator_sum=0.0
			if(len(self.tempdenominatorList)==0):
				mydenominator_sum=1.0
			else:
				for j in self.tempdenominatorList:
					mydenominator_sum=mydenominator_sum+self.dataArray[i][j]
			if(len(self.tempnumeratorList)==0):
				mynumerator_sum=1.0
			else:
				for j in self.tempnumeratorList:
					mynumerator_sum=mynumerator_sum+self.dataArray[i][j]

			self.energy.append(self.dataArray[i][self.energySelection])
			# Check not dividing by zero
			if(self.equationOption.isChecked()):
				logstring="log(abs"
			else:
				logstring=""
			if(mydenominator_sum==0.0):
				self.mu.append(0.0)
			else:
				if(self.equationOption.isChecked()):
					self.mu.append(math.log(math.fabs(mynumerator_sum/mydenominator_sum)))
				else:
					self.mu.append(mynumerator_sum/mydenominator_sum)
		self.previewPlot.setCurveData(self.previewCurve,self.energy,self.mu)
		self.previewPlot.replot()
		self.numeratorList=self.tempnumeratorList
		self.denominatorList=self.tempdenominatorList
		return numeratorstring,denomstring,logstring

	#
	# When the selection changes in the denominator window
	# update the equation string
	#
	def denominatorUpdate(self,event1,event2):
		numeratorstring,denomstring.logstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring,logstring)

	#
	# When the selection changes in the numerator window
	# update the equation string
	#
	def numeratorUpdate(self,event1,event2):
		numeratorstring,denomstring,logstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring,logstring)


	#
	# When the selection changes in the numerator window
	# update the equation string
	#
	def energyUpdate(self,event1):
		for row in range(self.energy_model.rowCount()):
			item = self.energy_model.item(row, 0)
			if(item.checkState()>0):
				self.energySelection=row
				numeratorstring,denomstring,logstring=self.constructEquationStrings()
				break


	#
	# Update the equation text field in the widget
	#
	def updateEquation(self,string1,string2,string3):
		myequationstring=string3+"("+string1+"/"+string2+")"
		self.equationText.setText(myequationstring)

	#
	#
	# Check if a string is a number
	#
	#        
	def isNumber(self,input_string):
		result=False
		try:
			number=float(input_string)
			result=True
		except:
			result=False
		return result
        
	#
	# tests if string contains numerical data
	# returns true if the first (up to eight) words in string can
	#  all be numbers. requires at least two words, and tests only
	# the first eight columns
	#
	def isColumnData(self,input_string):
		isdata = False
		# Convert string to list of floats and strings
		floats,strings=self.stringToFloatList(input_string)
		# How many floats and strings do we have
		numberOfFColumns=len(floats)
		numberOfSColumns=len(strings)
		# data needs to have at least two columns and more floats than strings
		if (numberOfFColumns >= 2 and numberOfSColumns<=1):
			isdata = True
		return isdata,numberOfFColumns

	def stringToFloatList(self,input_string):
		line=input_string.replace(',', ' ')
		line=line.strip()
		# split it up
		data = line.split()
		returnData=[]
		returnStrings=[]
		for x in data:
			if(self.isNumber(x)):
				returnData.append(float(x))
			else:
				returnStrings.append(x)
		return returnData,returnStrings

	def stringToIntegerList(self,input_string):
		line=input_string.replace(',', ' ')
		line=line.strip()
		# split it up
		data = line.split()
		returnData=[]
		returnStrings=[]
		for x in data:
			if(self.isNumber(x)):
				returnData.append(int(x))
			else:
				returnStrings.append(x)
		return returnData,returnStrings

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

       
        def findee(self,energy, mu):
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
                        if((dxde3> demx) and dxde3 > 0.0 and dxde2 > 0.0 and dxde1 > 0.0):  
                                ee   = energy[i+2]
                                demx = dxde3*1.00001
#                                        break
                return ee



                
                        
        def guess_iz(self,en,mu):
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

                edge_index=[1,2,12,12,3,12,13,13,13,14,14,4,14,\
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
                
                edge_type=['K','K','L3','L3','K','L1','L3','L2','L1','L3','L2','K','L1',\
                'L3','L2','L1','L3','L2','K','L1','L3','L2','L1','L3','L2','K','L1','L3','L2','L1','L3','L2','L3','L1',\
                'K','L2','L3','L2','L1','L3','L2','L1','K','L3','L2','L1','L3','L2','L1','K','L3','L2','L1','L3','L2',\
                'L1','L3','K','L2','L1','L3','L2','L1','L2','L3','K','L1','L3','L2','L1','L3','L2','L1','K','L3',\
                'L2','L1','L3','L2','L1','L3','K','L2','L1','L3','L2','L1','L3','K','L2','L1','L3','L2','L1','L3',\
                'K','L2','L1','L3','L2','L3','L1','L2','K','L3','L1','L2','L3','L1','L2','K','L3','L1','L2','L3',\
                'L1','L2','L3','K','L1','L2','L3','L1','L2','L3','L1','K','L2','L3','L1','L3','L2','L1','K','L3',\
                'L2','L1','L3','L2','L1','K','L3','L2','L1','L3','L2','L1','K','L3','L2','L1','L3','L2','L1','K',\
                'L3','L2','L1','L3','L2','L3','L1','K','L2','L3','L1','L2','L3','K','L1','L3','L2','L1','L3','L2',\
                'K','L1','L3','L2','L1','L3','L2','K','L1','L3','L2','L1','L3','L2','K','L3','L1','L2','L3','L1',\
                'L2','L3','K','L1','L3','L2','L1','L3','L2','K','L1','L3','L2','L1','L3','L2','K','L1','L3','L2',\
                'L1','L3','K','L2','L3','L1','L2','L3','L1','K','L3','L2','L1','L3','L2','L1','L3','K','L2','L1',\
                'L3','L2','L3','L1','K','L2','L1','L2','K','L1','L3','L2','L1','L2','K','L1','L2','L1','K','L3',\
                'L1','K','L3','L2','K','L3','L1','K','L2','K','L1','L2','K','L1','K','L2','L1','K','K','K',\
                'K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K',\
                'K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K']
                
                edge_element=['H','He','Mg','Mg','Li','Mg','Al','Al','Al','Si','Si','Be','Si',\
                'P','P','P','S','S','B','S','Cl','Cl','Cl','Ar','Ar','C','Ar','K','K','K','Ca','Ca','Sc','Ca',\
                'N','Sc','Ti','Ti','Sc','V','V','Ti','O','Cr','Cr','V','Mn','Mn','Cr','F','Fe','Fe','Mn','Co','Co',\
                'Fe','Ni','Ne','Ni','Co','Cu','Cu','Ni','Zn','Zn','Na','Cu','Ga','Ga','Zn','Ge','Ge','Ga','Mg','As',\
                'As','Ge','Se','Se','As','Br','Al','Br','Se','Kr','Kr','Br','Rb','Si','Rb','Kr','Sr','Sr','Rb','Y',\
                'P','Y','Sr','Zr','Zr','Nb','Y','Nb','S','Mo','Zr','Mo','Tc','Nb','Tc','Cl','Ru','Mo','Ru','Rh',\
                'Tc','Rh','Pd','Ar','Ru','Pd','Ag','Rh','Ag','Cd','Pd','K','Cd','In','Ag','Sn','In','Cd','Ca','Sb',\
                'Sn','In','Te','Sb','Sn','Sc','I','Te','Sb','Xe','I','Te','Ti','Cs','Xe','I','Ba','Cs','Xe','V',\
                'La','Ba','Cs','Ce','La','Pr','Ba','Cr','Ce','Nd','La','Pr','Pm','Mn','Ce','Sm','Nd','Pr','Eu','Pm',\
                'Fe','Nd','Gd','Sm','Pm','Tb','Eu','Co','Sm','Dy','Gd','Eu','Ho','Tb','Ni','Er','Gd','Dy','Tm','Tb',\
                'Ho','Yb','Cu','Dy','Lu','Er','Ho','Hf','Tm','Zn','Er','Ta','Yb','Tm','W','Lu','Ga','Yb','Re','Hf',\
                'Lu','Os','Ge','Ta','Ir','Hf','W','Pt','Ta','As','Au','Re','W','Hg','Os','Re','Tl','Se','Ir','Os',\
                'Pb','Pt','Bi','Ir','Br','Au','Pt','Hg','Kr','Au','Rn','Tl','Hg','Pb','Rb','Tl','Bi','Pb','Sr','Th',\
                'Bi','Y','U','Rn','Zr','Pu','Rn','Nb','Th','Mo','Th','U','Tc','U','Ru','Pu','Pu','Rh','Pd','Ag',\
                'Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho',\
                'Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Rn','Th','U','Pu']
                
                

                #  guess e0 from spectra 
                guess = 30
                e0=self.findee(en,mu)
                print 'ee -estimated edge position',e0
                #  find closest energy in table
                ex = e0/1000.0
                elementindex=self.nearest_x(ex,edges)
                guess = edge_index[elementindex]
                edgetype=edge_type[elementindex]
                elementName=edge_element[elementindex]
                #print 'guess',guess,edgetype
                return guess,elementName,edgetype





if(__name__=='__main__'):
    app=QApplication(sys.argv)
    datal=DataImporter()
    datal.loadFile("18657.dat.xmu")
    datal.show()
    app.exec_()


