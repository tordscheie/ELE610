#!/usr/bin/env python3
# -*- coding: utf-8 -*-  (no Byte Order Mark, BOM)
#
# ../ELE610/py3/ele610noGUI.py 
#
# The example file to use for UiS ELE610 course if you don't want to use any GUI
# Jume 2026 (KS): made file
#
# Test:
#   ..\py3>python ele610noGUI.py ia13
#   ..\py3>python ele610noGUI.py ia142bw

# import packages
import sys
import inspect
import numpy as np 
import cv2

# by KS
from bf_tools import mpl_plot

# *********************** functions ************************* #

def ia13():
	print(f"1.3.c: Python {sys.version} on {sys.platform}")
	print("Add more Python code to print more answers.")
	
	
def ia142bw():
	"""Make the black and white image with 3 simple objects as in IA 1.4.2
	"""
	A = np.zeros((300,400),dtype=np.uint8)
	A = cv2.line(A, (10,10), (10,50), 255)
	A = cv2.rectangle(A, (20,10), (50,60), 255, thickness=-1)
	A = cv2.ellipse(A, (120,50), (40,40), angle=360, startAngle=0, endAngle=360, color=255, thickness=2)
	#
	mpl_plot(A, title="IA 1.4.2")
	
	

# *********************** main ************************* #
FUNCTIONS = {
	name: obj 
	for name, obj in globals().items()
	if callable(obj) and name.startswith("ia")
}

if __name__ == '__main__':
	for funName in sys.argv[1:]:
		print(f"ele610noGUI.main(): try to run function {funName.lower()}")
		try:
			FUNCTIONS[funName.lower()]()
		except KeyError:
			print(f"Error: '{funName}' is not a valid function")

