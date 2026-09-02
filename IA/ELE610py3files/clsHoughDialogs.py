#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsHoughDialogs.py 
#
#  The classes:  HoughLinesDialog and HoughCirclesDialog
#  For test:     MainWindow
#  Functions:    getBestHoughLines, draw_lines 
#
# Karl Skretting, UiS, January-February 2024, October 2025 made clsHoughLinesDialog.py and clsHoughCirclesDialog.py
#   March 2026, collect these in one file and one test and made some improvements
#   CoPilot helped to make methods more 'Phytonic' and according to Qt good practice

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3>activate py12
#   (py12) C:\..\py3>python clsHoughDialogs.py
#   .../ELE610/py3$ python3 clsHoughDialogs.py
# Example on how to use file in a python program  
#   from clsHoughDialogs import HoughLinesDialog, HoughCirclesDialog, getBestHoughLines, draw_lines

_fileName = "clsHoughDialogs.py"
_author = "Karl Skretting, UiS" 
_version = "2026.03.19"      # "yyyy.mm.dd"

# common:
import sys 
import numpy as np

# Qt, https://doc.qt.io/qt-6/classes.html
from mySystem import QT_BINDING, cv2Exist, qt5Exist, qt6Exist 
if QT_BINDING == "None":
	print("Importing Qt failed.")
	raise ImportError(f"{_fileName}: Requires PyQt6, PySide6 or PyQt5")
else: # ok
	from mySystem import (QT_VERSION_STR, Qt, QAction, QFont, pyqtSignal,  
	  QApplication, QButtonGroup, QDialog, QDialogButtonBox, QDoubleSpinBox,  
	  QHBoxLayout, QLabel, QMainWindow, QPushButton, QRadioButton, 
	  QSlider, QSpinBox, QTextBrowser, QVBoxLayout, 
	  QDialogButtonBox_Apply, QDialogButtonBox_ApplyRole, QDialogButtonBox_Cancel, 
	  QDialogButtonBox_Ok, Qt_AlignRight, Qt_Horizontal)

if cv2Exist: 
	import cv2


# 'Old' function, not changed March 2026
def getBestHoughLines(linesFound, B, nofLines, distLines, verbose=True):
	"""Sort and select the 'best' lines from lines as returned by 
	HoughLines or HoughLinesP. Also line representation is changed.
	Angle theta is in radians and shown in degrees.
	
	Use:
	  lines = getBestHoughLines(linesFound, B, nofLines, distLines)
	Input arguments:
	  linesFound : the lines as returned by HoughLines or HoughLinesP
	  B          : the binary image used to find the lines
	               needed to find the 'cover' property of a line
	  nofLines   : maximum number of lines to return
	  distLines  : ignore lines closer to each other than given by distLines
	  verbose    : True (print much) or False (print nothing)
	Output argument:
	  lines      : a numpy array with nofLines rows and 8 columns 
	  lines[row] : each row is a line given by 8 values, two alternative
	    representations and two derived properties
	  (x1,y1) = (line[0],line[1]) first point for line
	  (x2,y2) = (line[2],line[3]) second point for line, x2 >= x1
	  rho = line[4] is distance from line to origin
	  theta = line[5] is angle [radians] from upward in clockwise direction
	  length = line[6] is length from first point to second point
	  cover = line[7] is how many pixels in a thin line from first point 
	    to second point that is non-zero in binary image B     
	"""
	if not (isinstance(linesFound, np.ndarray) and (linesFound.ndim == 3) and \
	        linesFound.size):
		print( "getBestHoughLines(): first argument 'linesFound' not as expected. " )
		print( "Is it from cv2.HoughLines() or cv2.HoughLinesP() ?" )
		return None
	if not (isinstance(B, np.ndarray) and (B.ndim == 2)):
		print( "getBestHoughLines(): second argument 'B' not as expected. " )
		return None
	if (len(linesFound) == 0) or (nofLines < 1) : return None
	#
	L = len(linesFound)
	(w,h) = (B.shape[1], B.shape[0])
	lines = np.zeros((L,8),dtype=np.float64)
	if verbose:
		print( f"\ngetBestHoughLines(..,{nofLines=},{distLines=:6.2f}): started " \
		       f"with {L=} lines in numpy array 'lines'." )
		print( "-- first shows lines in the order they were found by cv2.HoughLines[P] --" )
	# find the two representations and two properties of each line
	for idxLine in range(L):
		line = linesFound[idxLine]
		# HoughLines:  line = array([[rho, theta]], dtype=float32)   # theta in radians
		# HoughLinesP: line = array([[x1,y1,x2,y2]], dtype=int32)
		if (line.ndim == 2) and (line[0].size == 2):  # from HoughLines
			(rho,theta) = line[0]           
			(a,b) = (np.cos(theta), np.sin(theta))
			(x0,y0) = (a*rho, b*rho)   # point on line closest to origin
			(x1,y1) = (int(x0 + 8000*(-b)), int(y0 + 8000*(a)))
			(x2,y2) = (int(x0 - 8000*(-b)), int(y0 - 8000*(a)))
			# input arguments of clipLine should be int, and returned values are int
			(inSide,(x1,y1),(x2,y2)) = cv2.clipLine((0,0,w,h),(x1,y1),(x2,y2))
		elif (line.ndim == 2) and (line[0].size == 4):  # from HoughLinesP
			(x1,y1,x2,y2) = line[0]
		else:
			print( f"ERROR in getBestHoughLines(): {line=}" )
			return None
		# end if
		# use (x1,y1) and (x2,y2) to (re)calculate rho and theta
		length = np.hypot(x2-x1,y2-y1)
		theta = np.arctan2(x2-x1,y1-y2)  # x2-x1 >= 0 ==> 0 <= theta <= pi
		rho = (x2*y1-x1*y2)/length if length else 0.0
		#
		cover = 0
		if (theta < np.pi/4) or (theta > np.pi*3/4):
			# let y go from y1 to y2 and find corresponding x
			for y in range(min(y1,y2),max(y1,y2)+1):
				a = (y-y1)/(y2-y1)
				x = int((1-a)*x1+a*x2)
				if B[y,x]: cover = cover+1
			#
		else:
			# let x go from x1 to x2 and find corresponding y
			for x in range(x1,x2+1):
				a = (x-x1)/(x2-x1)
				y = int((1-a)*y1+a*y2)
				if B[y,x]: cover = cover+1
			#
		# 
		if verbose:
			print( f"line {idxLine:4d}: {rho=:8.2f}, theta={theta*180/np.pi:6.1f} [deg] or " +\
			       f"({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}) ==> {length=:6.1f}, {cover=:4d}." )
		lines[idxLine] = [x1,y1,x2,y2, rho,theta, length,cover]
	# end for
	idx = np.flip(lines[:,7].argsort())
	lines = lines[idx,:].copy()
	if verbose:
		print( "-- lines ordered by 'cover' after copy() --" )
		for idxLine in range(L):
			(x1,y1,x2,y2, rho,theta, length,cover) = lines[idxLine]
			print( f"line {idxLine:4d}: {rho=:8.2f}, theta={theta*180/np.pi:6.2f} [deg] or " +\
			       f"({x1=:7.2f},{y1=:7.2f}), ({x2=:7.2f},{y2=:7.2f}) " + \
			       f"==> {length=:7.2f}, {cover=:7.2f}." )
	#
	# we should still check if some lines are 'overlapping' 
	thetaLim = 5*np.pi/180  # two lines with angle difference larger than this does NOT match
	if verbose:
		print( f"-- check lines for overlap, thetaLim = {{thetaLim*180/np.pi:6.2f}} --" )
		print( f"      Keep line in row    0 as row    0 in 'lines'.")
	okRows = 1   # lines[okRows-1] is the last good row to return
	tryRow = 1   # the next row to try
	while (okRows < min(nofLines, L)) and (tryRow < L):
		tryRowOK = True
		(x1,y1,x2,y2, rho,theta, length,cover) = lines[tryRow]
		(x2x1, y2y1) = (x2-x1, y2-y1)
		# but tryRow need to be different from all okRows
		(closeIdx, closeTh, closeD1, closeD2, closeD) = (0,180,9999,9999,9999)
		for idxRow in range(okRows):   
			# compare lines[tryRow] to lines[idxRow]
			# find d as distance between the two lines, this can be done in several ways
			(x3,y3,x4,y4, rho3,theta3, length3,cover3) = lines[idxRow]
			(tMin,tMax) = (min(theta,theta3),max(theta,theta3))
			thetaDiff = min(tMax-tMin, tMin+np.pi-tMax)
			# We may have that 
#	An angle difference larger than 5 degrees, or rho difference larger
#	than 'distLines' means that the lines are regarded as unique lines.
#	Perhaps also thetaLim (here 5*pi/180) should be an input argument.
			#if verbose and (thetaDiff < 2*thetaLim):
			#	print( f"line {tryRow=:4d} and line {idxRow=:4d} " + \
			#		   f"(angles: {theta*180/np.pi:6.2f} and {theta3*180/np.pi:6.2f}) " + \
			#		   f"has angle difference of {thetaDiff*180/np.pi:6.2f}." )
			#	print( f"{tryRow=:4d} {lines[tryRow,5]*180/np.pi:6.2f} [deg], " + \
			#	       f"{idxRow=:4d} {lines[idxRow,5]*180/np.pi:6.2f} [deg]." )
			#
			#if (thetaDiff > thetaLim) or (abs(rho3-rho) > distLines): continue  
			#
			# distance between end points of each line
			d1 = ( min(np.hypot(x3-x1,y3-y1), np.hypot(x3-x2,y3-y2)) + \
			       min(np.hypot(x4-x1,y4-y1), np.hypot(x4-x2,y4-y2)) )/2
			# or distance of end points projected onto the other line
			d2 = ( abs(x2x1*(y3-y1)-(x3-x1)*y2y1) + \
			       abs(x2x1*(y4-y1)-(x4-x1)*y2y1) )/(2*length)
			# or a combination
			d = (d1+d2)/2
			#
			if (d < closeD):
				(closeIdx, closeTh, closeD1, closeD2, closeD) = (idxRow,thetaDiff,d1,d2,d)
			#if verbose and (d < 2*distLines): 
			#	print( f"line {tryRow=:4d} and line {idxRow=:4d}, " + \
			#	       f"angle difference {thetaDiff*180/np.pi:6.2f}, " + \
			#	       f"end points distances {d2=:6.1f}, {d=:6.1f}, {d1=:6.1f}." )
			#
			if (d < distLines): # to small distance
				tryRowOK = False
				break   # for loop
			#
		#end for (all idxRow)
		if verbose:
			print( f"line {tryRow:4d} has 'closest' line {closeIdx:4d}, " + \
			       f"angle difference is {closeTh*180/np.pi:6.2f} [deg], " + \
			       f"end points distances d2={closeD2:6.1f}, " + \
			       f"d={closeD:6.1f}, d1={closeD1:6.1f}." )
		#
		if tryRowOK:
			if verbose:
				print( f"  ==> Keep line in row {tryRow=:4d} as row {okRows=:4d} in 'lines'.")
			if (okRows < tryRow): lines[okRows] = lines[tryRow]  
			okRows = okRows + 1
		elif verbose: 
			print( f"  ==> Discard line in row {tryRow=:4d}.")
		#
		tryRow = tryRow + 1
	# end while
	if verbose:
		print( f"-- getBestHoughLines() returns {okRows} lines in numpy array --\n" )
	#
	return lines[:okRows]

#  ..\ELE610\py3\bf1.py  contains the first version of this function
# 'Old' function, not changed March 2026
def draw_lines(lines, img, color=(0,255,0), thickness=3, verbose=True):
	"""Draw lines, as returned by HoughLines or HoughLinesP or getBestHoughLines into 
	img, a BGR image of the same size as the binary image used when the lines were found.
	The image has origin in upper left corner, 
	x-axis is to the right (width) and y-axis downwards (height).
	rho is distance from line to origin, 
	and rho is negative if closest point, (x0,y0) in code, has negative y-value.
	theta is angle [radians] from upward in clockwise direction
	Note that color and thickness is as used in cv2.line function,
	color should be a BGR tuple and thickness is not exactly width in pixels.
	see: https://stackoverflow.com/questions/24682797/python-opencv-drawing-line-width
	"""
	if verbose:
		print( f"draw_lines(..): started, {lines.shape=}, {img.shape=}" )
	(w,h) = (img.shape[1], img.shape[0])
	for line in lines:
		# print( f"lines[{no}] = {line = }" )
		# HoughLines:  line = array([[rho, theta]], dtype=float32)   # theta in radians
		# HoughLinesP: line = array([[x1,y1,x2,y2]], dtype=int32)
		if (line.ndim == 2) and (line[0].size == 2):  # lines are from HoughLines
			(rho,theta) = line[0]           
			(a,b) = (np.cos(theta), np.sin(theta))
			(x0,y0) = (a*rho, b*rho)   # point on line closest to origin
			(x1,y1) = (int(x0 + 3000*(-b)), int(y0 + 3000*(a)))
			(x2,y2) = (int(x0 - 3000*(-b)), int(y0 - 3000*(a)))
			# input arguments of clipLine should be int, and returned values are int
			(inSide,(x1,y1),(x2,y2)) = cv2.clipLine((0,0,w,h),(x1,y1),(x2,y2))
			length = np.hypot(x1-x2,y1-y2)
			if verbose:
				print( f"  HL line: {rho=:8.2f}, theta={theta*180/np.pi:6.1f} [deg] " +\
				       f"gives ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), {length=:6.1f}" )
		elif (line.ndim == 2) and (line[0].size == 4):  # lines are from HoughLinesP
			(x1,y1,x2,y2) = line[0]
			length = np.hypot(x1-x2,y1-y2)
			if verbose:
				print( f"  HLP line: ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), {length=:6.1f}" )
		elif (line.ndim == 1) and (line.size == 8):  # lines are from getBestHoughLines
			(x1,y1,x2,y2) = (int(line[0]),int(line[1]),int(line[2]),int(line[3]))
			(rho,theta,length,cover) = (line[4],line[5],line[6],int(line[7]))
			if verbose:
				print( f"  BHL line: ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), " + \
			           f"theta={theta*180.0/np.pi:6.1f} [deg], {length=:6.1f}, {cover=}" )
		else:
			print( f"ERROR in draw_lines(): line not as expected. \n{line=}" )
			return
		# 
		# x2 >= x1
		cv2.line(img,(x1,y1),(x2,y2),color,thickness)
	return


myHelpStyleSheet = """
    QTextBrowser {
        font-family: "Segoe UI";
        font-size: 11pt;
        font-weight: normal;
    }
""" 

helpHoughLines = """<h3>Standard Hough Line Transform</h3>
<p>This dialogs allows you to give the parameters to use in either the standard Hough transform 
<code>HoughLines()</code>, or the probabilistic Hough transform <code>HoughLinesP()</code>.
For both functions the input image should be 8-bit, single-channel binary image. 
The output depends of the function and is explained in the 
<a href="https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html">OpenCV tutorial</a>.
I recommend that you read this tutorial to better understand the OpenCV functions.
</p>
<p>In this dialog you may select which function you want to give parameters for. 
The two last parameters here may be used by caller to restrict which lines to consider more than
what the parameters from OpenCV does.
The parameters that can be changed here are:
<ul>
  <li><b>rho</b>: The resolution of the parameter <i>r</i> in pixels</li>
  <li><b>theta</b>: The resolution of the parameter &theta;. 
  Note that it is used in radians in OpenCV but here it is given and returned in degrees.</li>
  <li><b>threshold</b>: The minimum number of (pixel) intersections to 'detect' a line</li>
  <li><b>minLineLength</b>: The minimum number of points that can form a line. Lines with less than this number of points are disregarded. Used only for <code>HoughLinesP()</code>.</li>
  <li><b>maxLineGap</b>: The maximum gap between two points to be considered in the same line.
  Used only for <code>HoughLinesP()</code>.</li>
  <li><b>nofLines</b>: Maximum number of lines to keep and show.</li>
  <li><b>distLines</b>: Discard lines closer to each other than given distance.</li>
</ul></p>
<p>This dialog returnes a tuple of 5 or 7 values, i.e. 
(rho, theta, threshold, nofLines, distLines) for HoughLines() and
(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) for HoughLinesP().<br>
For images the origin is upper left corner, x-axis to the right and y-axis downward. 
Angle is 0 or 180 degrees is for vertical lines, 45 degrees for lines from lower-left to upper-right, 
90 degrees for horizontal lines, and 135 degrees for lines from upper-left to lower-right.<br>
[Try it] button will show all lines found by HoughLines but after [OK] button is clicked 
the caller (calling program) may discard some of these lines as given by the bottom two values.<p>
""" + f"File: {_fileName}, date: {_version}, author: {_author}"

class HoughLinesDialog(QDialog):  
	"""A modal dialog widget for giving HoughLines parameters
	Emits lineValuesChanged(tuple) when [Apply]-button is clicked
	"""
	lineValuesChanged = pyqtSignal(tuple)
	
	def _makeRow(self, label, spinbox, slider):
		row = QHBoxLayout()
		row.addWidget(label)
		row.addWidget(spinbox)
		row.addWidget(slider)
		return row

	def __init__(self, parent, title="", default=(2.0, 1.0, 500, 25.0, 25.0, 10, 10.0)):
		#				
		super().__init__(parent)
		
		if isinstance(title, str) and len(title):
			self.title = title
		else:
			self.title = "Dialog for finding lines in binary image"
			
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+150, 700, 700)
		
		if not (isinstance(default, (tuple,list)) and (len(default)==7)):
			default=(2.0, 1.0, 500, 25.0, 25.0, 10, 10.0)
		
		self._createWidgets(default)
		self._createLayout()
		self._connectSignals()

	def _createWidgets(self, default):
		headFont = QFont("Arial",11,weight=75)
		labelWidth = 80
		spinBoxWidth = 80
		sliderWidth = 250
		#
		a = self.browser = QTextBrowser()
		a.setMinimumHeight(200)  # a small browser in dialog widget 
		a.setAcceptRichText(False)
		a.setHtml(helpHoughLines)
		a.setStyleSheet(myHelpStyleSheet)
		a.setOpenExternalLinks(True)
		#
		# qbgHLorHLP, 2 radio buttons 
		a = self.qrbUseHL = QRadioButton('Use HoughLines() function.')
		a.setFont(headFont)
		a.setChecked(True)
		a = self.qrbUseHLP = QRadioButton('Use HoughLinesP() function.')
		a.setFont(headFont)
		a = self.qbgHLorHLP = QButtonGroup()
		a.addButton(self.qrbUseHL, 0)
		a.addButton(self.qrbUseHLP, 1)
		a.setExclusive(True)
		#
		label_texts = ["rho:", "theta:", "threshold:", "minLineLength:",
				"maxLineGap:", "nofLines:", "distLines:"]
		labels = [QLabel(text) for text in label_texts]
		for label in labels:
			label.setAlignment(Qt_AlignRight)
			label.setFixedWidth(labelWidth)
		#
		self.spinBoxes = [QDoubleSpinBox(), QDoubleSpinBox(), QSpinBox(), 
				QDoubleSpinBox(), QDoubleSpinBox(), QSpinBox(), QDoubleSpinBox()]
		spin_specs = [
			(0.0, 50.0, 1.0,  default[0]),     # rho
			(0.0, 45.0, 0.5,  default[1]),     # theta
			(0,   4000, 100,  default[2]),     # threshold
			(0,   200,  25.0, default[3]),     # minLineLength
			(0,   200,  25.0, default[4]),     # maxLineGap
			(0,   200,  5,    default[5]),     # nofLines
			(0.0, 100.0, 5.0, default[6])      # distLines
		]
		for sb, (mn, mx, step, initial) in zip(self.spinBoxes, spin_specs):
			sb.setRange(mn, mx)
			sb.setSingleStep(step)
			sb.setValue(initial)
			sb.setFixedWidth(spinBoxWidth)
			if isinstance(sb, QDoubleSpinBox):
				sb.setDecimals(2)
		
		self.sliders = [QSlider(Qt_Horizontal) for i in range(7)]
		for sb, sl in zip(self.spinBoxes, self.sliders):
			sl.setFixedWidth(sliderWidth)
			sl.setMinimum(0)
			sl.setMaximum(200)
			sl.setTracking(False)  # valueChanged() only when mouse button is released
			relVal = (sb.value() - sb.minimum()) / (sb.maximum() - sb.minimum())
			sl.setSliderPosition( int(200*relVal) )  
		
		self.lines = [self._makeRow(l, sb, sl)
			for l, sb, sl in zip(labels, self.spinBoxes, self.sliders)]

		# --- OK / Cancel / Apply buttons ---
		self.buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel | QDialogButtonBox_Apply)

	def _createLayout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.browser)
		#
		qrbLine = QHBoxLayout()
		qrbLine.addWidget(self.qrbUseHL)
		qrbLine.addWidget(self.qrbUseHLP)
		layout.addLayout(qrbLine)
		#
		layout.addWidget(QLabel( "Common arguments for HoughLines() and HoughLinesP():" ))
		for i in range(7):
			if i==3:
				layout.addWidget(QLabel( "Additional arguments only for HoughLinesP():" ))
			if (i == 5):
				layout.addWidget(QLabel( "Additional arguments only for caller:" ))
			layout.addLayout(self.lines[i])
		#
		layout.addWidget(self.buttons)
		self.setLayout(layout)

	def _connectSignals(self):
		# Only [Apply]-button emit signal lineValuesChanged but this can easily be changed below
		for i, sb in enumerate(self.spinBoxes):
			sb.valueChanged.connect(lambda val, i=i: self.spinBoxValueChanged(val, i, False))
		for i, sl in enumerate(self.sliders):
			sl.valueChanged.connect(lambda val, i=i: self.sliderValueChanged(val, i, False))
			sl.sliderMoved.connect(lambda val, i=i: self.sliderValueChanged(val, i, False))
		self.buttons.accepted.connect(self.accept)
		self.buttons.rejected.connect(self.reject)
		self.buttons.clicked.connect(self.applyClicked) 

	def values(self):
		"""Return 5 or 7 values as elements in a tuple"""
		rho = self.spinBoxes[0].value()
		theta = self.spinBoxes[1].value()
		threshold = self.spinBoxes[2].value()
		nofLines = self.spinBoxes[5].value()
		distLines = self.spinBoxes[6].value()
		if self.qrbUseHL.isChecked(): 
			t = (rho, theta, threshold, nofLines, distLines)
		else: 
			minLineLength = self.spinBoxes[3].value()
			maxLineGap = self.spinBoxes[4].value()
			t = (rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines)
		#
		return t

	def spinBoxValueChanged(self, val, boxNo, doEmit):
		# move spinBox value, 'val' or sb.value(), into slider value (position)
		sb = self.spinBoxes[boxNo]
		relVal = (val - sb.minimum()) / (sb.maximum() - sb.minimum())
		sl = self.sliders[boxNo]
		sl.blockSignals(True)
		sl.setSliderPosition( int(200*relVal) )  
		sl.blockSignals(False)
		if doEmit: 
			print("spinBoxValueChanged(): emit values")
			self.lineValuesChanged.emit(self.values())

	def sliderValueChanged(self, relVal, boxNo, doEmit):
		# move slider value 'relVal' into spinBox value
		sb = self.spinBoxes[boxNo]
		val = sb.minimum() + (relVal/200)*(sb.maximum() - sb.minimum())
		if (boxNo == 2) or (boxNo == 5):
			val = int(val)
		sb.blockSignals(True)
		sb.setValue(val)
		sb.blockSignals(False)
		if doEmit: 
			print("sliderValueChanged(): emit values")
			self.lineValuesChanged.emit(self.values())

	def applyClicked(self, button):
		# actually any of the buttons may be clicked!
		if self.buttons.buttonRole(button) != QDialogButtonBox_ApplyRole:
			return
			
		print("applyClicked(): emit values")
		self.lineValuesChanged.emit(self.values())


	def getValues(self):
		"""Execute the dialog widget and return the 5 or 7 values."""
		self.exec()
		return self.values()
	#end class HoughLinesDialog

helpHoughCircles = """<h3>OpenCV Hough Circles function arguments</h3>
<p>In this dialog you can give the parameters used in OpenCV <code>HoughCircles()</code> function. 
The function finds circles in a grayscale image using a modification of the Hough transform. See 
<a href="https://docs.opencv.org/4.x/da/d53/tutorial_py_houghcircles.html">OpenCV tutorial</a> 
or look up the function in 
<a href="https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html">OpenCV documentation</a>. 
for more information<br>
The parameters are described as in OpenCV documentation:
<ul>
  <li><b>method</b>: Detection method, 
  see <a href="https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html">HoughModes</a>. 
  The available methods are cv2.HOUGH_GRADIENT (=3) and cv2.HOUGH_GRADIENT_ALT (=4). <br>
  Note that this parameter is <b>not</b> possible to change here, which method to use is left to the caller. 
  The HOUGH_GRADIENT method should be a good choice.</li>
  <li><b>dp</b>: Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width and height. For HOUGH_GRADIENT_ALT the recommended value is dp=1.5, unless some very small circles need to be detected.</li>
  <li><b>minDist</b>: Minimum distance between the centers of the detected circles. If the parameter is too small, multiple neighbor circles may be falsely detected in addition to a true one. If it is too large, some circles may be missed.</li>
  <li><b>param1, Canny high threshold</b>: First method-specific parameter. It is the higher threshold of the two passed to the Canny edge detector (the lower one is twice smaller). Note that HOUGH_GRADIENT_ALT uses Scharr algorithm to compute image derivatives, so the threshold value should normally be higher, such as 300 or normally exposed and contrasty images.</li>
  <li><b>param2, accumulator threshold</b>: Second method-specific parameter. In case of HOUGH_GRADIENT, it is the accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false circles may be detected. Circles, corresponding to the larger accumulator values, will be returned first. <br>
  In the case of HOUGH_GRADIENT_ALT algorithm, this is the circle "perfectness" measure. The closer it to 1, the better shaped circles algorithm selects. In most cases 0.9 should be fine. If you want get better detection of small circles, you may decrease it to 0.85, 0.8 or even less. But then also try to limit the search range [minRadius, maxRadius] to avoid many false circles.</li>
  <li><b>minRadius</b>: Minimum circle radius.</li>
  <li><b>maxRadius</b>: Maximum circle radius. If &le; 0, uses the maximum image dimension. If &lt; 0, HOUGH_GRADIENT returns centers without finding the radius. HOUGH_GRADIENT_ALT always computes circle radiuses.</li>
  <li><b>maxCircles</b>: Maximun number of circles to keep. This parameter is not used in OpenCV, it can be used by caller to restrict the number of circle to use.</li>
</ul></p>
<p>This dialog returnes a tuple of 7 values, i.e. <br>
(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles). <br>
[Apply] button will emit a signal 'circleValuesChanged' that the caller can connect to a slot to apply the parameters and display the result.</p>
""" + f"File: {_fileName}, date: {_version}, author: {_author}"

""" I asked CoPilot (18/3-26):
Class HoughLinesDialog (attached) is good and I am satisfied with it. I hope you are too. Could you now make a new dialog class, based on this, but for the arguments of the HoughCircles function in OpenCV. Of course, the radio buttons are not needed in that class, but I would like a spinBox and a slider for each argument, and reasonable ranges, initial values and defaults for each. Use my way (with underscore) to name Qt enums. 
The answer had some remarks and included the new class as below: 
With some corrections (correct data type, 'int', in default[4:], and QSpinBox in general!) it worked well.
"""
class HoughCirclesDialog(QDialog):
	"""A modal dialog widget for giving HoughCircles parameters.
	   Emits circleValuesChanged(tuple) when [Apply]-button is clicked.
	"""
	circleValuesChanged = pyqtSignal(tuple)

	def _makeRow(self, label, spinbox, slider):
		row = QHBoxLayout()
		row.addWidget(label)
		row.addWidget(spinbox)
		row.addWidget(slider)
		return row

	def __init__(self, parent, title="", default=(1.0, 20.0, 100.0, 30.0, 25, 100, 20)):
		super().__init__(parent)

		if isinstance(title, str) and len(title):
			self.title = title
		else:
			self.title = "Dialog for finding circles in grayscale image"

		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+150, 800, 800)

		# Validate default tuple
		if not (isinstance(default, (tuple, list)) and len(default) == 7):
			default = (1.0, 20.0, 100.0, 30.0, 25, 100, 20)

		self._createWidgets(default)
		self._createLayout()
		self._connectSignals()

	def _createWidgets(self, default):
		headFont = QFont("Arial", 11, weight=75)
		labelWidth = 120
		spinBoxWidth = 80
		sliderWidth = 250

		# Help browser
		a = self.browser = QTextBrowser()
		a.setMinimumHeight(180)
		a.setAcceptRichText(False)
		a.setHtml(helpHoughCircles)     # You must define this string
		a.setStyleSheet(myHelpStyleSheet)
		a.setOpenExternalLinks(True)

		# Labels for HoughCircles parameters
		label_texts = [
			"dp:",
			"minDist:",
			"param1:",
			"param2:",
			"minRadius:",
			"maxRadius:",
			"maxCircles"
		]
		labels = [QLabel(text) for text in label_texts]
		for label in labels:
			label.setAlignment(Qt_AlignRight)
			label.setFixedWidth(labelWidth)

		# Spinboxes
		self.spinBoxes = [
			QDoubleSpinBox(),  # dp
			QDoubleSpinBox(),  # minDist
			QDoubleSpinBox(),  # param1
			QDoubleSpinBox(),  # param2
			QSpinBox(),        # minRadius
			QSpinBox(),        # maxRadius
			QSpinBox()         # maxCircles
		]

		# Reasonable ranges for HoughCircles
		spin_specs = [
			(0.1, 10.0,  0.1, default[0]),   # dp
			(1.0, 500.0, 1.0, default[1]),   # minDist
			(1.0, 500.0, 1.0, default[2]),   # param1 (Canny high threshold)
			(0.1, 200.0, 1.0, default[3]),   # param2 (accumulator threshold)
			(0,   400,   1,   int(default[4])),   # minRadius
			(0,   500,   1,   int(default[5])),   # maxRadius
			(1,   300,   1,   int(default[6]))    # maxCircles
		]

		for sb, (mn, mx, step, initial) in zip(self.spinBoxes, spin_specs):
			sb.setRange(mn, mx)
			sb.setSingleStep(step)
			sb.setValue(initial)
			sb.setFixedWidth(spinBoxWidth)
			if isinstance(sb, QDoubleSpinBox):
				sb.setDecimals(2)

		# Sliders
		self.sliders = [QSlider(Qt_Horizontal) for _ in range(7)]
		for sb, sl in zip(self.spinBoxes, self.sliders):
			sl.setFixedWidth(sliderWidth)
			sl.setMinimum(0)
			sl.setMaximum(200)
			sl.setTracking(False)
			relVal = (sb.value() - sb.minimum()) / (sb.maximum() - sb.minimum())
			sl.setSliderPosition(int(200 * relVal))

		# Rows
		self.lines = [
			self._makeRow(l, sb, sl)
			for l, sb, sl in zip(labels, self.spinBoxes, self.sliders)
		]

		# Buttons
		self.buttons = QDialogButtonBox(
			QDialogButtonBox_Ok |
			QDialogButtonBox_Cancel |
			QDialogButtonBox_Apply
		)

	def _createLayout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.browser)

		layout.addWidget(QLabel("Arguments for HoughCircles():"))
		for row in self.lines:
			layout.addLayout(row)

		layout.addWidget(self.buttons)
		self.setLayout(layout)

	def _connectSignals(self):
		for i, sb in enumerate(self.spinBoxes):
			sb.valueChanged.connect(lambda val, i=i: self.spinBoxValueChanged(val, i, False))

		for i, sl in enumerate(self.sliders):
			sl.valueChanged.connect(lambda val, i=i: self.sliderValueChanged(val, i, False))
			sl.sliderMoved.connect(lambda val, i=i: self.sliderValueChanged(val, i, False))

		self.buttons.accepted.connect(self.accept)
		self.buttons.rejected.connect(self.reject)
		self.buttons.clicked.connect(self.applyClicked)

	def values(self):
		"""Return the 7 HoughCircles parameters as a tuple."""
		dp = self.spinBoxes[0].value()
		minDist = self.spinBoxes[1].value()
		param1 = self.spinBoxes[2].value()
		param2 = self.spinBoxes[3].value()
		minRadius = self.spinBoxes[4].value()
		maxRadius = self.spinBoxes[5].value()
		maxCircles = self.spinBoxes[6].value()
		return (dp, minDist, param1, param2, minRadius, maxRadius, maxCircles)

	def spinBoxValueChanged(self, val, boxNo, doEmit):
		sb = self.spinBoxes[boxNo]
		relVal = (val - sb.minimum()) / (sb.maximum() - sb.minimum())
		sl = self.sliders[boxNo]
		sl.blockSignals(True)
		sl.setSliderPosition(int(200 * relVal))
		sl.blockSignals(False)
		if doEmit:
			self.circleValuesChanged.emit(self.values())

	def sliderValueChanged(self, relVal, boxNo, doEmit):
		sb = self.spinBoxes[boxNo]
		val = sb.minimum() + (relVal / 200) * (sb.maximum() - sb.minimum())
		if isinstance(sb, QSpinBox):
			val = int(val)
		sb.blockSignals(True)
		sb.setValue(val)
		sb.blockSignals(False)
		if doEmit:
			self.circleValuesChanged.emit(self.values())

	def applyClicked(self, button):
		if self.buttons.buttonRole(button) != QDialogButtonBox_ApplyRole:
			return
		self.circleValuesChanged.emit(self.values())

	def getValues(self):
		self.exec()
		return self.values()


class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of Hough line and circle dialogs")
		self.setGeometry(150, 50, 800, 800)  # initial window position and size
		#
		qaLineDialog = QAction('showLineDialog', self)
		qaLineDialog.setShortcut('Ctrl+L')
		qaLineDialog.setToolTip('Show the Hough line dialog')
		qaLineDialog.triggered.connect(self.showLineDialog)
		#
		qaCircleDialog = QAction('showCircleDialog', self)
		qaCircleDialog.setShortcut('Ctrl+C')
		qaCircleDialog.setToolTip('Show the Hough circle dialog')
		qaCircleDialog.triggered.connect(self.showCircleDialog)
		#
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&Dialogs')
		fileMenu.addAction(qaLineDialog)
		fileMenu.addAction(qaCircleDialog)
		fileMenu.setToolTipsVisible(True)


	def showLineDialog(self): 
		d = HoughLinesDialog(parent=self)   # create object (but does not run it)
		d.lineValuesChanged.connect(self.showLineValues)
		t = d.getValues()   # display dialog and return values in a tuple
		print(f"MainWindow.showLineDialog(): Returned tuple with {len(t)} values and {d.result()=}")
		self.printLineValues(t)
		d.lineValuesChanged.disconnect(self.showLineValues)

	def showLineValues(self, t):
		print(f"MainWindow.showLineValues(): Signal lineValuesChanged emitted, {len(t)=}")
		self.printLineValues(t)

	def printLineValues(self, t):   
		"""Print the returned parameters given in tuple 't'."""
		if (len(t) == 5):
			(rho, theta, threshold, nofLines, distLines) = t
			print( f"Should do HoughLines({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=})" )
			print( f"and show max {nofLines} lines with difference larger than {distLines}." )
		elif (len(t) == 7):
			(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) = t
			print( f"Should do HoughLinesP({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=}, " + \
			       f"{minLineLength=:.2f}, {maxLineGap=:.2f})" )
			print( f"and show max {nofLines} lines with difference larger than {distLines}." )
		else: 
			print( "printLineValues: dialog response 't'  has not expected length." )

	def showCircleDialog(self): 
		d = HoughCirclesDialog(parent=self)   # create object (but does not run it)
		d.circleValuesChanged.connect(self.showCircleValues)
		t = d.getValues()   # display dialog and return values in a tuple
		print(f"MainWindow.showCircleDialog(): Returned tuple with {len(t)} values and {d.result()=}")
		self.printCircleValues(t)
		d.circleValuesChanged.disconnect(self.showCircleValues)

	def showCircleValues(self, t):
		print(f"MainWindow.showCircleValues(): Signal circleValuesChanged emitted, {len(t)=}")
		self.printCircleValues(t)

	def printCircleValues(self, t):   
		"""Print the returned parameters given in tuple 't'."""
		if (len(t) == 7):
			(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = t
			print( f"Parameters are: ({dp=:.2f}, {minDist=:.2f}, {param1=:.2f}, {param2=:.2f}, " + 
			       f"{minRadius=}, {maxRadius=}, {maxCircles=})" )
		else: 
			print( "printCircleValues: dialog response 't'  has not expected length." )
#end class MainWindow


if __name__ == '__main__':
	print( f"** clsHoughDialogs.py: Using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	if qt6Exist:
		sys.exit(mainApp.exec())
	else:
		sys.exit(mainApp.exec_())
	
