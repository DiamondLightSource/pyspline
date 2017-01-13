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
                it  = imin + inc
                xit = array[it]
                while(1):
                        if ( x < xit ):
                                imax = it
                        elif ( x > xit ):
                                imin = it
                        else:
                                nofx = it
                                return nofx
                        inc = ( imax - imin ) / 2
                        if ( inc <= 0 ) break
                # x is between imin and imin+1
                xave = ( array[imin] + array[imin+1])/2.0
                if ( x < xave ):
                        nofx = imin
                else:
                        nofx = imin + 1
                return nofx

       
        def findee(energy, xmu):
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
                zero = 0.0
                tiny = 1.0e-9
                onepls = 1.00001
                ee  = zero
                if(len(xmun)<=8): return
                inc=[False]*3
                dxde  = zero
                demx  = zero
                ntry  = max(2, int(nxmu/2)) + 3
                for i in range(1, ntry):
 	            deltae  = energy[i] - energy[i-1]
 	            if (deltae>tiny):
 	         	dxde   = (xmu[i] - xmu[i-1])/deltae
        	 	inc[0] = dxde > zero
        	 	incall = inc[2] and inc[1] and inc[0]
        	    if (incall  and (dxde> demx) ):
        	 	ee   = energy[i]
        	 	demx = dxde * onepls
        	    for j  in range(2, 1, -1):
        	 	inc[j] = inc[j - 1]
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
                guess_iz = 0
                e0=findee(en,mu)
                #  find closest energy in table
                ex = e0/1000.0
                guess_iz = iedge[nofx(ex,edges,nedges)]
                return guess_iz

