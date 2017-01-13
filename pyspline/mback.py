
import math
import numpy
import scipy.optimize
import scipy.special

#MUCAL:	To calculate cross-sections using McMaster data
#
#in May, 1969 edition.
#
#barn=mucal(Z,E) return total x-section for the element Z
#in unit of [cm^2/g]
#xsec=mucal(Z,E,'b') return values in unit of [barns/atom]
#
#Z:atomic number of the element (Z_max=94)
#E:photon energy range for calculation, in KeV. 
#Tsu-Chien Weng, 07/01/98
#Copyleft, The Penner-Hahn research group
# 10/24/00: correction on L-edge jumps by T.-C.
#2005-03-11: clean up, re-make element.mat using make_element.m
# status=warning;
# warning off
# set default values of atom type and energy range
#
def McMaster(Z, energy, unit):
	lj1=1.160
	lj2=0.141000E+01 
	Z_max=94
	data=readMcMaster()
	mcdata=[]
	if Z < 0:
		print 'The atomic number should be positive.'
	elif Z > Z_max:
		print 'Your atom is too heavy.'
	elif (Z==84 or Z==85 or Z==87 or Z==88 or Z==89 or Z==91 or Z==93):
		# They are Po, At, Fr, Ra, Ac, Pa, Np.
		print 'McMaster does not have values for this element'
	else:
		for e in energy:
			ek=data[Z-1]['Kedge']/1000.0
			el3=data[Z-1]['L3edge']/1000.0
			el2=data[Z-1]['L2edge']/1000.0
			el1=data[Z-1]['L1edge']/1000.0
			em=data[Z-1]['Medge']/1000.0
			ak=data[Z-1]['ak']
			al=data[Z-1]['al']
			am=data[Z-1]['am']
			an=data[Z-1]['an']
			coherent=data[Z-1]['coherent']
			incoherent=data[Z-1]['incoherent']
			cf=data[Z-1]['density conversion']
			temp=0.0
			sum=0.0
			for i in range(4):
				if(e>=ek):
					if (e == 1.):
						temp=ak[i]*1.0
					else:
						temp=ak[i]*(math.log(e)**i)
				elif(e <= ek and e >= el3):
					if (e == 1.):
						temp=al[i]*1.0
					else:
						temp=al[i]*(math.log(e)**i)
				elif(e < el3 and e >= em) :
					if (e == 1.):
						temp=am[i]*1.0
					else:
						temp=am[i]*math.log(e)**i
				elif(e < em):
					if (e == 1.):
						temp=an[i]*1.0
					else:
						temp=an[i]*math.log(e)**i
				sum=sum+temp
			# exponent
			
			absorption=math.exp(sum)
			#----------------------------------------------------------------+
			#     correct for l-edges since mcmaster uses l1-edge            |
			#     use edge jumps for correct x-sections                      |
			#----------------------------------------------------------------+
			if(e>=el3 and e < el2):
				absorption=absorption/(lj1*lj2)
			if(e>=el2 and e< el1):
				absorption=absorption/lj1
			# Coherent scattering
			coherent_scattering=0.0
			temp=0.0
			for i in range(4):
				if (e == 1.0):
					temp=coherent[i]*1.0
				else:
					temp=coherent[i]*(math.log(e))**i
				coherent_scattering=coherent_scattering+temp
			coherent_scattering=math.exp(coherent_scattering)
			# in Coherent scattering
			incoherent_scattering=0.0
			temp=0.0
			for i in range(4):
				if (e == 1.0):
					temp=incoherent[i]*1.0
				else:
					temp=incoherent[i]*(math.log(e))**i
				incoherent_scattering=incoherent_scattering+temp
			incoherent_scattering=math.exp(incoherent_scattering)
			# The total 
			total=absorption+coherent_scattering+incoherent_scattering
			if(unit=='c'):
				total=total/cf
			mcdata.append(total)
		#print mcdata
	return numpy.array(mcdata)

	
	#
#
# Check if a string is a number
#
#        
def isNumber(input_string):
	result=False
	try:
		number=float(input_string)
		result=True
	except:
		result=False
	return result

	
def stringToFloatList(input_string):
	line=input_string.replace(',', ' ')
	line=line.strip()
	# split it up
	data = line.split()
	returnData=[]
	returnStrings=[]
	for x in data:
		if(isNumber(x)):
			returnData.append(float(x))
		else:
			returnStrings.append(x)
	return returnData,returnStrings


#
# Read in the mcmaster data file
#
def readMcMaster():
	fin=open("mcmaster.dat")
	data=fin.readlines()
	fin.close()
	# skip the header
	datastart=20
	# loop through the data and process it....
	zmax=94
	linestep=10
	listOfElements=[]
	for i in range(zmax):
		numbers1,strings1= stringToFloatList(data[datastart+1])
		numbers2,strings2= stringToFloatList(data[datastart+2])
		numbers3,strings3= stringToFloatList(data[datastart+3])
		numbers4,strings4= stringToFloatList(data[datastart+4])
		numbers5,strings5= stringToFloatList(data[datastart+5])
		numbers6,strings6= stringToFloatList(data[datastart+6])
		numbers7,strings7= stringToFloatList(data[datastart+7])
		numbers8,strings8= stringToFloatList(data[datastart+8])
		numbers9,strings9= stringToFloatList(data[datastart+9])
		#print 'numbers',numbers1,numbers2
		listOfElements.append(\
		{'atomic_symbol':strings1[0],'atomic_number':numbers1[0],'atomic_weight':numbers1[1],'density conversion':numbers1[3], \
		'Kedge':numbers2[0],'L1edge':numbers2[1],'L2edge':numbers2[2], 'L3edge':numbers2[3], 'Medge':numbers2[4], \
		'flu_Kbeta':numbers3[0],'flu_Lbeta':numbers3[1],'flu_Kalpha':numbers3[2],'flu_Lalpha':numbers3[3],'L3_jump':numbers3[4], \
		'ak':numbers4,'al':numbers5,'am':numbers6,'an':numbers7,'incoherent':numbers8,'coherent':numbers9})
		datastart=datastart+linestep
	return listOfElements

#
#
# MBGFUN_FULL 
# Background function called by MBACK for
#full non-linear least-squares optimization
# Tsu-Chien Weng, James E. Penner-Hahn, 2000-06-27
# Copyright (c), by the Penner-Hahn group, the University of Michigan
#2001-07-26: Change variable names to be consistent with the paper.
#
#
def mbgfun(alpha,energy,Mu_obs,E_edge,E_fluo,weight):
	#print 'alpha',alpha[0]
	Scale=alpha[0]	# scale factor for Mu_obs
	Amp=alpha[1]	# Amplitude of erfc()
	xi=alpha[2]	# spectra width in erfc()
	coef=alpha[3:]	# coefficients for polynomials
	mymu=[]
	#print "coef",coef
	#print 'here',len(energy),len(mymu)
	for i in range(len(energy)):
		bg_erfc=Amp*scipy.special.erfc((energy[i]-E_fluo)/xi)
		bg_poly=0.0
		bg_poly=numpy.polyval(coef,energy[i]-E_edge)
		bg_tot=bg_erfc+bg_poly
		Mu=((Scale*Mu_obs[i])-bg_tot)*weight[i]
		mymu.append(Mu)
	return numpy.array(mymu)

def mbgfun2(alpha,energy,Mu_obs,E_edge,E_fluo,weight):
	#print 'alpha',alpha[0]
	Scale=alpha[0]	# scale factor for Mu_obs
	Amp=alpha[1]	# Amplitude of erfc()
	xi=alpha[2]	# spectra width in erfc()
	coef=alpha[3:]	# coefficients for polynomials
	#print "coef",coef
	mymu=[]
	back=[]
	#print 'here',len(energy),len(mymu)
	for i in range(len(energy)):
		bg_erfc=Amp*scipy.special.erfc((energy[i]-E_fluo)/xi)
		bg_poly=0.0
		bg_poly=numpy.polyval(coef,energy[i]-E_edge)
		bg_tot=bg_erfc+bg_poly
		Mu=((Scale*Mu_obs[i])-bg_tot)*weight[i]
		mymu.append(Mu)
		back.append(bg_tot)
	return numpy.array(mymu),numpy.array(back)
	
	
def mback_residual(alpha,energy,mu_tab,mu_obs,E_edge,E_fluo,weight):
	mu=mbgfun(alpha,energy,mu_obs,E_edge,E_fluo,weight)
	max=mu-mu_tab
	print sum(max*max)
	return max
def mback_residual2(alpha,energy,mu_tab,mu_obs,E_edge,E_fluo,weight):
	mu=mbgfun(alpha,energy,mu_obs,E_edge,E_fluo,weight)
	mymax=mu-mu_tab
	mymax=mymax/(alpha[0]*mu_obs)
	sumit=sum(mymax*mymax)
	print sumit
	return mymax

#
# 
#MBACK Normalize raw data to tabulated mass absorption coefficients
# with erfc() and polynomials as the background functions.
# Tsu-Chien Weng, James E. Penner-Hahn, 2000-06-27
# Copyleft (c), by the Penner-Hahn group, the University of Michigan
#2001-07-26: Implement the full non-linear optimization with Jacobian.
#
# Converted to python - P Quinn 2010
#

def mback(Z,energy_eV,muData,E_edge,E_fluo,fitrange=[],Nth=2,core=''):
	energy_KeV=numpy.array(energy_eV)/1000.0
	#energy_KeV=energy_KeV-0.009
	mu_raw=numpy.array(muData)
	# (1a)  energy in KeV
	elementData=readMcMaster()
	data=readMcMaster()
	ek=data[Z-1]['Kedge']/1000.0
	el3=data[Z-1]['L3edge']/1000.0
	el2=data[Z-1]['L2edge']/1000.0
	el1=data[Z-1]['L1edge']/1000.0
	
	if (len(fitrange)==0):
		# skip XANES for proper scaling
		# default: [E_edge - 20eV, E_edge + 80eV]
		pre_edge =E_edge - 0.020 
		post_edge=E_edge + 0.080 
		# Find index of these points
		idx_pre =numpy.where(energy_KeV<=pre_edge)
		idx_post=numpy.where(energy_KeV>=post_edge)
	elif(len(fitrange) == 2):
		pre_edge =E_edge - fitrange[0]
		post_edge=E_edge + fitrange[1]
		idx_pre =numpy.where(energy_KeV<=pre_edge)
		idx_post=numpy.where(energy_KeV>=post_edge)
		
	elif(len(fitrange) == 4):
		print 'here',fitrange[1],fitrange[0]
		conditionList=[energy_KeV<fitrange[1],energy_KeV>fitrange[0]]
		choiceList=[energy_KeV,energy_KeV]
		energy_temp=numpy.select(conditionList,choiceList)
		idx_pre=numpy.where(energy_temp==energy_KeV)
		conditionList=[energy_KeV>fitrange[2],energy_KeV<=fitrange[3]]
		choiceList=[energy_KeV,energy_KeV]
		energy_temp=numpy.select(conditionList,choiceList)
		print 'energy_temp',energy_temp
		idx_post=numpy.where(energy_temp==energy_KeV)
		print 'idx_pre',idx_pre
	# If its not a K edge could have more than more L edge...need to ignore XANES or other L edges
	# if(core!='K'):
		# pre_edge3 =el3 - fitrange[0]
		# post_edge3=el3 + fitrange[1]
		# pre_edge2 =el2 - fitrange[0]
		# post_edge2=el2 + fitrange[1]
		# pre_edge1 =el1 - fitrange[0]
		# post_edge1=el1 + fitrange[1]
		# conditionList=[energy_KeV<pre_edge1,energy_KeV>post_edge1]
		# choiceList=[energy_KeV,energy_KeV]
		# enrg1=numpy.select(conditionList,choiceList)
		# conditionList=[enrg1<pre_edge2,enrg1>post_edge2]
		# choiceList=[enrg1,enrg1]
		# enrg2=numpy.select(conditionList,choiceList)
		# conditionList=[enrg2<pre_edge3,enrg2>post_edge3]
		# choiceList=[enrg2,enrg2]
		# enrg3=numpy.select(conditionList,choiceList)
		# indices=numpy.where(enrg3==energy_KeV)
		# print 'indices',indices
		
		
		# idx_pre1  =numpy.where(energy_KeV<=pre_edge1)
		# idx_post1 =numpy.where(energy_KeV>=post_edge1)
		# idx_pre2  =numpy.where(energy_KeV<=pre_edge12
		# idx_post2 =numpy.where(energy_KeV>=post_edge2)
		# idx_pre3  =numpy.where(energy_KeV<=pre_edge3)
		# idx_post3 =numpy.where(energy_KeV>=post_edge3)
		# i
		
		
	idx_fit=numpy.append(idx_pre,idx_post) # index for pre-/post-edge data points
	idx_xanes=numpy.delete(numpy.arange(len(energy_KeV)),idx_fit)
	#print idx_pre,len(idx_pre[0]),pre_edge,E_edge
	num_pre_edge_points =len(idx_pre[0])
	num_post_edge_points=len(idx_post[0])
	# (2) Tabulated mass absorption coefficients
	# Ref: McMaster et al. (1969) "Compilation of X-ray Cross sections"
	mutab=McMaster(Z,energy_KeV,'c')
	#print 'mu_mcaster',len(mutab),len(energy_KeV)
	# Points below the edge.....mu from mcmaster is sharp interface function anyway.
	idx_res=numpy.where(energy_KeV<E_edge)
	# Fit 2nd order poly to region < edge and then get poly curve over the full energy range
	#print 'v',numpy.take(energy_KeV,idx_res)[0]
	poly=numpy.polyfit(numpy.take(energy_KeV,idx_res)[0],numpy.take(mutab,idx_res)[0],Nth)
	res=numpy.polyval(poly,energy_KeV)
	# mu = mu - background
	mutab=mutab-res
	# Should be zero as we have removed the background but just set to zero....
#	for index in idx_res:
#		mutab[index]=0.0
	# (3a) Scale raw data and mu_tab
	# Max over the xanes range
	mu_span =numpy.take(mutab,idx_xanes).max()
	#print 'mu_span',mu_span
	# upper and lower limits of the data over the xanes region
	raw_span=numpy.take(mu_raw,idx_xanes).max()-numpy.take(mu_raw,idx_xanes).min()
	print 'raw_span',raw_span,mu_span
	# scale mu mcmaster data
	# extract subset of fit data and divide by span
	
	mu_tab=numpy.take(mutab,idx_fit)/mu_span
	# scale the raw data
	mu_obs=numpy.take(mu_raw,idx_fit)/raw_span
	# energy fit data set
	KeV_obs=numpy.take(energy_KeV,idx_fit)
	# (3b) Normalization
	xi0=0.5
	# Fit a poly of order n from pre-edge to end  and use as your initial guess
	pi0=numpy.polyfit(KeV_obs[num_pre_edge_points+1:]-E_edge,mu_tab[num_pre_edge_points+1:],Nth)
	# S,A,xi, pi0
	guess=numpy.array([1.0,1.0, xi0])
	guess=numpy.append(guess,pi0) # initial guess: [S,A,xi,{P_i}]
	# A list of ones
	weight_one=numpy.ones(len(mu_raw))
	# Weighting for the fit.............weight to number of points pre and post edge
	weight_fit=numpy.append(numpy.tile(1.0/math.sqrt(num_pre_edge_points),num_pre_edge_points),\
		numpy.tile(1.0/math.sqrt(num_post_edge_points),num_post_edge_points))
	#print weight_fit
	# Least squares fit of mu_tab*weight_fit to mbgfun
	#print len(KeV_obs),len(mu_tab),len(weight_fit),num_pre_edge_points,num_post_edge_points,guess,pi0[1:Nth][0]
	#fits=scipy.optimize.leastsq(mback_residual,guess,args=(KeV_obs,mu_tab*weight_fit,mu_obs,E_edge,E_fluo,weight_fit),maxfev=5000,ftol=1.0e-8,gtol=1.0e-8)
	#mybounds=[(0.0,1.0e20),(-1.0e20,1.0e20),(1.0e-20,1.0e20),(-1.0e20,1.0e20),(-1.0e20,1.0e20),(-1.0e20,1.0e20),(-1.0e20,1.0e20)]
	#mybounds=[(0.0,1.0e20),(-1.0e20,0.0),(0.0,1.0e20),(-1.0e20,1.0e20),(-1.0e20,1.0e20),(-1.0e20,1.0e20)]	
	#print mybounds,len(guess),guess
	#fits=scipy.optimize.fmin_l_bfgs_b(mback_residual2,guess,fprime=None,approx_grad=True,factr=10.0,bounds=mybounds,args=(KeV_obs,mu_tab*weight_fit,mu_obs,E_edge,E_fluo,weight_fit))
	fits=scipy.optimize.leastsq(mback_residual2,guess,args=(KeV_obs,mu_tab*weight_fit,mu_obs,E_edge,E_fluo,weight_fit),full_output=1,)
	#alpha,energy,mu_tab,mu_obs,E_edge,E_fluo,weight
	# Normalized data is with no weighting....
	print 'fits',fits[0]
	#print idx_fit
	guess=numpy.array([1.0,1.0, xi0])
	guess=numpy.append(guess,pi0) # initial guess: [S,A,xi,{P_i}]
	norm_xas,back=mbgfun2(fits[0],energy_KeV,mu_raw/raw_span,E_edge,E_fluo,weight_one)
	#print 'lens',len(norm_xas),len(energy_KeV),len(mutab)
	fout=open("test.dat","w")
	for i in range(len(norm_xas)):
		print>>fout,energy_KeV[i],norm_xas[i],mutab[i]/mu_span,fits[0][0]*mu_raw[i]/raw_span,back[i]
	fout.close()
	
	
fin=open("Ce_L3.dat")
data=fin.readlines()
fin.close()
enrg=[]
mux=[]
fout=open("test2.dat","w")
for i in range(1,len(data)):
	spx=data[i].split()
	#print spx
	enrgt=float(spx[0])
	enrg.append(enrgt)
	#muxt=float(spx[25])/float(spx[3])
	muxt=float(spx[1])
	mux.append(muxt)
	print >>fout,enrgt/1000.0,muxt
fout.close()
	
E_f=5.84569979
E_k=6.97700024
z=63

mback(z,enrg,mux,E_k,E_f,fitrange=[6.869,6.948,7.090,7.520],Nth=2,core='')




