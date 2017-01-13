from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from random import randint

#
#
# A class to help with importing data files
#
#
#
class DataImporter(QWidget):
	def __init__(self,parent = None):
		QWidget.__init__(self,parent)
		# Array which will hold the column data
		self.dataArray=[]
		self.numeratorList=[]
		self.demoninatarList=[]
		self.energySelection=0
		self.energy=[]
		self.mu=[]
		# Window - widgets and layout
		self.setWindowTitle("Import Data")
		self.denominatar_model = QStandardItemModel()
		self.numerator_model= QStandardItemModel()
		self.energy_model= QStandardItemModel()
		self.denominatarLabel = QLabel(self)
		self.denominatarLabel.setText("Denominator")
		self.denominatar_view = QListView(self)
		self.denominatar_view.setModel(self.denominatar_model)
		self.denominatar_view.setSelectionMode(QListView.MultiSelection)
		self.numerator_view = QListView(self)
		self.numerator_view.setModel(self.numerator_model)
		self.numerator_view.setSelectionMode(QListView.MultiSelection)
		self.numeratorLabel = QLabel(self)
		self.numeratorLabel.setText("Numerator")
		self.energy_view = QListView(self)
		self.energy_view.setModel(self.energy_model)
		self.energy_view.setSelectionMode(QListView.SingleSelection)
		self.energyLabel = QLabel(self)
		self.energyLabel.setText("Energy")
		self.overalllayout= QVBoxLayout()
		self.dataViewerLayout = QVBoxLayout()
		self.fileLabel = QLabel(self)
		self.fileLabel.setText("Data File")
		self.fileText = QTextEdit()
		self.dataViewerLayout.addWidget(self.fileLabel)
		self.dataViewerLayout.addWidget(self.fileText)
		self.overalllayout.addLayout(self.dataViewerLayout)
		self.dataLoaderLayout = QGridLayout()	
		self.dataLoaderLayout.addWidget(self.energyLabel,1,1)
		self.dataLoaderLayout.addWidget(self.numeratorLabel,1,2)
		self.dataLoaderLayout.addWidget(self.denominatarLabel,1,3)
		self.dataLoaderLayout.addWidget(self.energy_view ,2,1)
		self.dataLoaderLayout.addWidget(self.numerator_view,2,2)
		self.dataLoaderLayout.addWidget(self.denominatar_view,2,3)
		self.overalllayout.addLayout(self.dataLoaderLayout)
		self.equationViewerLayout = QHBoxLayout()
		self.equationOption = QCheckBox(self)
		self.equationOption.setText("Natural Log")
		self.equationLabel = QLabel(self)
		self.equationLabel.setText("mu(E)")
		self.equationText = QLineEdit()
		self.equationViewerLayout.addWidget(self.equationOption)
		self.equationViewerLayout.addWidget(self.equationLabel)
		self.equationViewerLayout.addWidget(self.equationText)
		numeratorstring,denomstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring)
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
		self.connect(self.denominatar_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.denominatarUpdate)
		self.connect(self.numerator_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.numeratorUpdate)
		self.connect(self.energy_view.selectionModel(),SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),self.energyUpdate)


	#
	# Read in an ascii file containing columns of data
	#
	def loadFile(self,filename):
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
        	        # if it startes with comments cycle
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
		for i in range(startLine,numberOfLines,3):
			idata1,columns1=self.isColumnData(datalines[i])
			idata2,columns2=self.isColumnData(datalines[i+1])
			idata3,columns3=self.isColumnData(datalines[i+2])
			if((idata1 and idata2 and idata3) and (columns1==columns2==columns3)):
				newStartLine=i
				break
		for i in range(newStartLine,numberOfLines):
				dataf,datas=self.stringToFloatList(datalines[i])
				self.dataArray.append(dataf)
		#
		#
		# Paste the data into the data text viewer
		#
		for data in datalines:
			self.fileText.insertPlainText(data)

		#
		# Fill in the column data in the widget...
		#
		self.denominatar_model.clear()
		self.numerator_model.clear()
		self.energy_model.clear()
		noOfColumns=len(self.dataArray[0])
		# Create list starting from 1 rather than 0
		for n in range(1,noOfColumns+1):                   
			item1 = QStandardItem('Column %s' % n)
			item2 = QStandardItem('Column %s' % n)
			item3 = QStandardItem('Column %s' % n)
			self.denominatar_model.appendRow(item1)
			self.numerator_model.appendRow(item2)
			self.energy_model.appendRow(item3)  

		# Set up some selections ...just so something is selected
		# and we have some defaults
		if(noOfColumns==2):
			self.energy_view.selectionModel().setCurrentIndex(self.energy_model.index(0,0),QItemSelectionModel.Select)
			self.numerator_view.selectionModel().setCurrentIndex(self.numerator_model.index(1,0),QItemSelectionModel.Select)
		else:
			self.energy_view.selectionModel().setCurrentIndex(self.energy_model.index(0,0),QItemSelectionModel.Select)
			self.numerator_view.selectionModel().setCurrentIndex(self.numerator_model.index(1,0),QItemSelectionModel.Select)
			self.denominatar_view.selectionModel().setCurrentIndex(self.denominatar_model.index(2,0),QItemSelectionModel.Select)



	#
	# Push the ok button
	# process the columns and send to main widget...
	#
	def accept(self):
		# Return mu based on selection
		print 'ok'
		print self.demoninatarList
		print self.numeratorList
		for i in range(len(self.dataArray)):
			mydenominatar_sum=0.0
			mynumerator_sum=0.0
			if(len(self.demoninatarList)==0):
				mydenominatar_sum=1.0
			else:
				for j in self.demoninatarList:
					mydenominatar_sum=mydenominatar_sum+self.dataArray[i][j]
			if(len(self.numeratorList)==0):
				mynumerator_sum=1.0
			else:
				for j in self.numeratorList:
					mynumerator_sum=mynumerator_sum+self.dataArray[i][j]

			self.energy.append(self.dataArray[i][self.energySelection])
			# Check not dividing by zero
			if(mydenominator==0.0):
				self.mu.append(0.0)
			else:
				self.mu.append(mynumerator_sum/mydenominatar_sum)					
			# Natural log


	#
	# Push the cancel button
	#
	def reject(self):
                self.hide()
                self.emit(SIGNAL("closed()"),())
	#
	# Based on the selected columns construct a string
	# showing the equation which will be used to construct
	# mu
	#
	def constructEquationStrings(self):
		self.demoninatarList=[]
		for x in self.denominatar_view.selectedIndexes():
			self.demoninatarList.append(x.row())
		# construct denominator line
		self.demoninatarList.sort()
		if(len(self.demoninatarList)==0):
			denomstring='1'
		else:
			denomstring='('
			for value in self.demoninatarList:
				denomstring=denomstring+"col("+str(value+1)+")"+"+"
			denomstring=denomstring.rstrip("+")
			denomstring=denomstring+")"
		#
		# Numerator line
		# 
		self.numeratorList=[]
		for x in self.numerator_view.selectedIndexes():
			self.numeratorList.append(x.row())
		# construct denominator line
		self.numeratorList.sort()
		if(len(self.numeratorList)==0):
			numeratorstring='1'
		else:
			numeratorstring='('
			for value in self.numeratorList:
				numeratorstring=numeratorstring+"col("+str(value+1)+")"+"+"
			numeratorstring=numeratorstring.rstrip("+")
			numeratorstring=numeratorstring+")"
		return numeratorstring,denomstring	

	#
	# When the selection changes in the denominatar window
	# update the equation string
	#
	def denominatarUpdate(self,event1,event2):
		numeratorstring,denomstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring)

	#
	# When the selection changes in the numerator window
	# update the equation string
	#
	def numeratorUpdate(self,event1,event2):
		numeratorstring,denomstring=self.constructEquationStrings()
		self.updateEquation(numeratorstring,denomstring)


	#
	# When the selection changes in the numerator window
	# update the equation string
	#
	def energyUpdate(self,event1,event2):
		if(len(self.energy_view.selectedIndexes())==1):
			print self.energy_view.selectedIndexes()[0].row()
			self.energySelection=self.energy_view.selectedIndexes()[0].row()

	#
	# Update the equation text field in the widget
	#
	def updateEquation(self,string1,string2):
		myequationstring=string1+"/"+string2
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


if(__name__=='__main__'):
    app=QApplication(sys.argv)
    datal=DataImporter()
    datal.loadFile("18657.dat.xmu")
    datal.show()
    app.exec_()


