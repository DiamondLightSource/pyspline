import sys
#check to see if qt,pyqt, and numeric are installed
#try:
#	import PyQt4 as qt
#except ImportError:
#	print "Please install PyQt first."
#	sys.exit(1)

#try:
#	from PyQt4 import Qwt5 as qwt
#except ImportError:
#	print "Please install PyQwt first."
#	sys.exit(1)

#try:
#	import numpy
#except ImportError:
#	print "Please install numpy first."
#	sys.exit(1)

#check to see if py2exe is wanted
with_py2exe=True
try:
    import py2exe
except ImportError:
    with_py2exe=False

#are we using py2exe
if with_py2exe and len(sys.argv)>1 and sys.argv[1]=='py2exe':
    from distutils.core import setup
    setup(name="PySpline",
          version="1.2",
          author="Adam Tenderholt and Paul Quinn",
          author_email="paul.quinn@diamond.ac.uk",
          url="http://pyspline.sourceforge.net",
          package_dir = {'pyspline':'src_new'},
          packages=['pyspline'],
          windows=['PySpline'],
          scripts=['pyspline'],
          options = {"py2exe": {"includes":"numpy, sip,PyQt4.QtCore,PyQt4.QtGui,PyQt4,PyQt4.Qwt5"}}
          )

else:
    from setuptools import setup
    setup(name="PySpline",
          version="1.2",
          author="Adam Tenderholt and P Quinn",
          author_email="paul.quinn@diamond.ac.uk",
          url="http://pyspline.sourceforge.net",
          include_package_data=True,
          packages=['pyspline'],
          #package_dir = {'pyspline':'pyspline'},
          #data_files = ('data', ['pyspline/data/edges.dat']),
          scripts=['bin/pyspline'],
          install_requires = ['numpy', 'appdirs']
          )
