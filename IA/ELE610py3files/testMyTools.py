#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/testMyTools.py
#
# Use: ..\py3>python testMyTools.py
# Use: ..\py3>python -m unittest testMyTools.TestMyTools.test_01  
#
#  Functions for testing and demonstration of funMyGetData.py.
#
#  A brief overview is:
#  test_01  Test of printArray(), some examples
#  test_02  Test of uniqueRandomKinL(), some examples
#  test_03  Test of printValueName(), some examples
#  test_04  Test of printElements(), some examples
#
#  Karl Skretting, UiS, March 2025

_fileName = "funMyTools.py"
_author = "Karl Skretting, UiS"  
_version = "2026-08-07"             # "yyyy-mm-dd"

makePlots = True

# common:
# from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 
import numpy as np
import unittest
# import warnings   # commented out here and below
if makePlots:  
	import matplotlib.pyplot as plt
import time
from math import pi, sin # ceil, floor, hypot, isclose , sqrt, 
# by KS:
from funMyTools import *

# *** The unit test class
class TestMyTools(unittest.TestCase):
	""" to do all tests, methods starting with 'test' 
	(py11) C:/../py3>python TestMyTools.py
	"""

	def test_01(self):
		print( "\ntest_01  Test of printArray(), some examples")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		k_pi = np.array(pi*np.arange(5))
		X = np.array(range(200)).reshape((25,8))
		Z = np.exp(1j*np.arange(0,2*np.pi,np.pi/6))
		#
		printArray(k_pi, "k_pi")
		printArray(k_pi, name="k_pi", maxN=0)
		printArray(X)
		printArray(X[:,4], name="X[:,4]", maxN=16)
		#printArray(X[:20,3:5], name="X[:20,3:5]", maxN=8)
		printArray(X[:20,:2].T, name="X[:20,:2].T", maxN=16)
		printArray(Z,'Z')
		return
		
	def test_02(self):
		print( "\ntest_02  Test of uniqueRandomKinL(), some examples")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		idx = uniqueRandomKinL(4,12)
		printArray(idx, "idx = uniqueRandomKinL(4,12)", "%3d ", maxN=12)
		idx = uniqueRandomKinL(12,20)
		printArray(idx, "idx = uniqueRandomKinL(12,20)", "%3d ", maxN=12)
		idx = uniqueRandomKinL(12,20000)
		printArray(idx, "idx = uniqueRandomKinL(12,20000)", "%5d ", maxN=12)
		return
		
	def test_03(self):
		print( "\ntest_03  Test of printValueName(), some examples")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		def returnEmptyString():
			return ''
		#
		k_pi = np.array(pi*np.arange(5))
		X = np.array(range(200)).reshape((25,8))
		Z = np.exp(1j*np.arange(0,2*np.pi,np.pi/6))
		# simple
		printValueName(0o642,'i')
		printValueName(3.1416e-1,'long_name_is_just_shortened')
		printValueName([1,2,5,pi,'absd']*3,'lst')
		printValueName((1,2,5,pi,'ab'),'tup')
		printValueName({1:"one", 'n2':23, 3:'tre'},'d1')
		printValueName(np.pi,'np.pi')
		printValueName(3+6j,'z1')
		# numpy
		printValueName(np.exp(1j*np.pi/6),'z2 is a complex number on unit circle 30 degrees')
		printValueName(X,'X')
		printValueName(Z,'Z')
		# more
		printValueName(_fileName,"_fileName")
		printValueName("En lang string som går over \nflere linjer. "*3,"s2")
		printValueName("A long string on only one single line. "*3,"s3")
		printValueName(b'ab\x63def\xf1\xf2',"tegn")
		printValueName(bytearray.fromhex('2E f0 F1f2  '),"bA")
		# and more
		printValueName(time,"time")
		printValueName(returnEmptyString,"returnEmptyString")
		printValueName(self,"self")
		#
		return
		
	def test_04(self):
		print( "\ntest_04  Test of printElements(), some examples")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		#
		a = {"one":1, 'n2':23, 'tre':3, 4:'four'} 
		aSet = {2, 'two', '1+1', 'sqrt(4)'}
		aList = [1,2,'three',a,(2,3,4)]
		aDict = {"aList":aList, "a_var":a, "date":"Aug 23rd", "_hidden":-1, \
		         "on":True, "none":None, "fun":argsort, \
		         "f1":sin, "f2":np.sin, "num":np.pi}
		aRange = range(4,12,2)
		#
		printElements(aSet,name='aSet')
		printElements(aList,'aList')
		printElements(aList[-1],name='aList[-1]')
		printElements(aRange,name='aRange')
		printElements(name='a',a='a')
		printElements(name='variables in test_04')
		#
		printElements(aDict,name="Elements that start with 'a' or 'n'",mask_name='[an]')
		printElements(aDict,name="aDict", show_hidden=True, var_type='fv')
		return
		
	def test_05(self):
		print( "\ntest_05  Smallest enclosing circle of points")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		#
		A = np.random.randn(18, 2)
		p = make_circle(A)
		if makePlots:
			# circle
			theta = np.linspace(0, 2*np.pi, 400)
			x = p[0] + p[2]*np.cos(theta)
			y = p[1] + p[2]*np.sin(theta)
			plt.plot(x, y, 'b-')   
			# track points as line 
			plt.plot(A[:,0], A[:,1], 'r3')   
			#
			plt.axis('equal')
			plt.title('Points and enclosing circle')
			plt.xlabel('x')
			plt.ylabel('y')
			plt.grid(True)
			plt.show()
		
		
#end of class TestSpaseApprox

if __name__ == '__main__':
    unittest.main()
