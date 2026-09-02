#!/usr/bin/env python3
# -*- coding: utf-8 -*-  (without BOM)
#
# .../Dropbox/ELE610/py3/startup.py    
# On web available at:  http://www.ux.uis.no/~karlsk/ELE610/startup.py
# This file is Python (version >= 3.9) startup file for Karl Skretting at UiS.
# It can be used on my UiS HP Windows 11 computer, on my home Ubuntu (Unix) computer,
# on my Samsung laptop PC (Windows 10), and on the TekNat Unix system, preferable gorina3.
#
# Karl Skretting, UiS, 2017 - 2020 - 2022 - 2025 - 2026

# Anaconda prompt..> activate py12  (or py3[.bat], or something else)
# (py12) C:\..\py3> python -i startup.py 
#
# Unix system at UiS or Ubuntu at home:  
#   ssh karlsk@gorina2   # gorina2.ux.uis.no
#   (login pw)
#   cd ~/python
#   python3 -i startup.py 

# print("** Startup-file for Python 3.x, (x >= 9) import some packages and functions.")

# Python common packages
import sys
print("Here    sys.version : " + sys.version)
print("Running on platform : " + sys.platform)
print(f"Qt versions: {('PyQt6' in sys.modules)=}, {('PyQt5' in sys.modules)=}  ??hmmm??")
from pathlib import Path
from math import sqrt, pi, cos, sin, tan, log, floor, ceil  

# by KS
from mySystem import findMyDropbox, npExist, cv2Exist, qt5Exist, qt6Exist, qtChartExist, gpxPath, imagePath
from funMyTools import argsort, printArray, printElements, whos

# don't use reload that much any more
# try:
# 	from importlib import reload
# except ImportError:
# 	print( "Error importing reload from importlib; reload is not available." )

# more Python packages, that may or may not be installed
print("** startup.py: import more Python packages and assign values to some variables.")
if npExist:
	import numpy as np
	print("Package numpy version is " + np.__version__)
else:
	print(f"numpy is not available, {npExist=}")

try:
	import matplotlib.pyplot as plt   # or import matplotlib as mpl
except ImportError:
	print("ImportError for matplotlib.pyplot; plt is not available.")
except:
	print("Error importing matplotlib.pyplot; plt is perhaps not available.")

if cv2Exist:
	import cv2
	print("Package   cv2 version is " + cv2.__version__)
else:
	print(f"OpenCV is not available, {cv2Exist=}")

# print("** Assign values to some variables.")
X = np.array(range(200)).reshape((25,8))
pm = findMyDropbox('m610')
print( "Find Dropbox path for Matlab files in ELE610: pm = " + str(pm) )
f = sorted([x for x in pm.glob('*.jpg')])  # what ls below do
if (len(f) > 0):	
	print(f"And 'f' is a list of {len(f)} jpg-files in {str(pm)}" )

# print( "** List defined variables and Python is ready to use." )
printElements( vars() )

