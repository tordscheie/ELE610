#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# 
# ../ELE610/py3/clsImageViewFrame.py 
#
#  includes classes: ImageQGV        the QGraphicsView where the image is shown
#                    ImageViewFrame  (inherits QFrame) the main class here which contains ImageQGV
#                    TestWindow      a QMainWindow to test the ImageViewFrame class 
#
#  Qt6 documentation: https://doc.qt.io/qt-6/classes.html 
#  The ImageViewFrame class may be useful to include in Qt applications that need to show an image.
#  It is based on appImageViewer1.py as used in ELE610 at UiS and as such it also includes some
#  example cv2 image processing options. The first target application for this class is 
#  appImageSegmentation.py which will --- hopefully --- be developed during the next months.
#
#  In class ImageViewFrame the image is storde as an QImage objectt only, as opposed to in the appImageViewer1
#  program where it is stored both as a QPixmap, Qimage, an numpy array. The Qt6 documentation says:
#    There are functions to convert between QImage and QPixmap. Typically, the QImage class is used to load an image file, 
#    optionally manipulating the image data, before the QImage object is converted into a QPixmap to be shown on screen. 
#    Alternatively, if no manipulation is desired, the image file can be loaded directly into a QPixmap.
#  Here the QImage object is converted to a QPixmap object when it is wanted to show the image on the scene, and
#  the QImage object is converted to a numpy array when openCV (cv2) functions is used to do image processing.
#
# Karl Skretting, UiS, October 2025 --> 
#   March 2026: removed image processing methods (OpenCV), import Qt via mySystem

# Example on how to use file: 
# (C:\...\Anaconda3) C:\..\py3>activate qtenv310 
# (qtenv310) C:\..\py3>python clsImageViewFrame.py
# (qtenv310) C:\..\py3>python clsImageViewFrame.py kart1.png
# (qtenv310) C:\..\py3>python clsImageViewFrame.py "https://www.ux.uis.no/sigproc/textures/brodatz/Nat-5c_1.pgm"
# (qtenv310) C:\..\py3>python clsImageViewFrame.py C:\Karl\tctdata\Outex_SS_00000\008\train_01.ras

_fileName = "clsImageViewFrame.py" 
_author = "Karl Skretting, UiS" 
_version = "2026.06.02"       # yyyy.mm.dd 

import sys
from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 
import numpy as np 

# Qt, https://doc.qt.io/qt-6/classes.html
from mySystem import QT_BINDING, qt5Exist, qt6Exist, qtChartExist, imagePath 
if QT_BINDING == "None":
	print("Importing Qt failed.")
	raise ImportError(f"{_fileName}: Requires PyQt6, PySide6 or PyQt5")
else: # ok
	from mySystem import (Qt, QPoint, QPointF, QRect, QSize, QT_VERSION_STR, pyqtSignal, pyqtSlot, 
	  QAction, QBrush, QColor, QFont, QImage, QPainter, QPen, QPixmap, QTransform, 
	  QApplication, QFileDialog, QFrame, QGraphicsView, QGraphicsScene, 
	  QLabel, QMainWindow, QRubberBand,
	  QFrame_Box, QImage_Format_Grayscale8, QImage_Format_Indexed8, QImage_Format_RGB32, 
	  QPainter_Antialiasing, QRubberBand_Rectangle, 
	  Qt_LeftButton, Qt_RightButton, Qt_IgnoreAspectRatio, Qt_FastTransformation, 
	  Qt_AlignLeft, Qt_AlignHCenter, Qt_AlignVCenter, Qt_AlignBottom)
	if qtChartExist:
		from mySystem import QBarSeries, QBarSet, QBarCategoryAxis, QChart, QChart_SeriesAnimations, QLineSeries, QValueAxis  

# by KS (UiS) 
from clsELE610Dialogs import ResizeDialog
from funImageTools import np2qimage, qimage2np, myOpenImageFile
from funMyTools import rounded_range 


class ImageQGV(QGraphicsView):
	"""This is the viewer where the pixmap image is shown, and perhaps histogram, 
	it is a simple extension of QGraphicsView.
	
	Mouse events, and rubber band, are processed in this class.
	Note that this class uses some variables belonging to the parent, p = self.parent()
	  p.rubberBandActive  is used to show rubber band when left button is pressed
	  p.image             is used to find image size and format
	  p.imPixel           shows the pixel information 
	  p.chartHist         may be used if it exists
	""" 
	rubberBandRectGiven = pyqtSignal(QRect) 

	def __init__(self, scene, parent=None):
		"""Initialize, basically as for the inherited class 'QGraphicView', 
		but add mouse tracking and rubber band functionality."""
		super().__init__(scene, parent)
		#
		self.setMouseTracking(True)
		self.pos1 = QPoint()
		self.rubberBand = QRubberBand(QRubberBand_Rectangle, self)
		self.rubberBand.hide()   
	
	
	def mousePressEvent(self, event):
		"""Print where the mouse is when a mouse button is pressed.
		Note that event.pos() gives the location in the view, while (x,y) gives the
		location in the scene, which here corresponds to the pixel index of the pixmap.
		"""
		# 
		p = self.parent()
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		#
		if (event.button() == Qt_LeftButton):
			print("ImageQGV.mousePressEvent: Press LeftButton at:  ", end='') 
			self.pos1 = event.pos()
			if hasattr(p, 'rubberBandActive') and p.rubberBandActive:
				self.rubberBand.setGeometry(QRect(event.pos(), QSize()))
				self.rubberBand.show()
		if (event.button() == Qt_RightButton):
			print("ImageQGV.mousePressEvent: Press RightButton at: ", end='')
		print(f"{str(event.pos())}, in scene at (x,y) = ({x},{y})")
	
	
	def mouseMoveEvent(self, event): 
		"""Displays position of mouse pointer and, from the QImage object, the pixel color. 
		If not self.rubberBand.isHidden(), also updates the rubber band rectangle.
		""" 
		p = self.parent()
		(w,h) = (p.image.width(), p.image.height())
		if not self.rubberBand.isHidden():   # or  self.rubberBand.isVisible()  ??
			self.rubberBand.setGeometry(QRect(self.pos1, event.pos()).normalized())
		# 
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		if ((x >= 0) and (x < w) and (y >= 0) and (y < h)):
			if not p.image.isNull():  
				col = p.image.pixelColor(x, y)
				if (p.image.format() == QImage_Format_Grayscale8): 
					p.imPixel.setText(f"In image (x,y) = ({x},{y}):  gray = {col.value()}") 
				elif (p.image.format() == QImage_Format_Indexed8): 
					p.imPixel.setText(f"In image (x,y) = ({x},{y}):  index  = {col.value()}")
				else: # QImage_Format_RGB32, or other
					(r,g,b,a) = (col.red(), col.green(), col.blue(), col.alpha())
					if (a == 255):
						p.imPixel.setText(f"In image (x,y) = ({x},{y}):  (r,g,b) = ({r},{g},{b})")
					else:
						p.imPixel.setText(f"In image (x,y) = ({x},{y}):  (r,g,b,a) = ({r},{g},{b},{a})")
			else: 
				p.imPixel.setText(f"Null image (w,h) = ({w},{h})  (x,y) = ({x},{y}) Hmm")
		elif ((x >= 0) and (x < 600 and (y >= h+5) and (y < h+5+400))):
			if hasattr(p, 'chartHist') and (p.chartHist is not None) and hasattr(p.chartHist.series()[0], 'barSets'):
				serie = p.chartHist.series()[0]  # first and only series
				binVal = int(p.chartHist.mapToValue(QPointF(x,100), serie).x()+1.0)
				if binVal < 0 or binVal > 255:
					p.imPixel.setText(f"In Chart: (x,y) = ({x},{y-h-5})") 
				else:
					barSet = serie.barSets()[0] # first and only
					count = int(barSet.at(binVal))
					p.imPixel.setText(f"In Chart: bin {binVal} has count {count}") 
			else:   # part of scene reserved for histogram, but no histogram 
				p.imPixel.setText(f"In scene: (x,y) = ({x},{y-h-5})") 
		else:
			p.imPixel.setText(f"In scene: (x,y) = ({x},{y})") 
		return
	
	
	def mouseReleaseEvent(self, event):
		"""Just print when the left mouse button is released.
		If not self.rubberBand.isHidden() a signal with the rubber band rectangle is emitted
		"""
		# 
		if (event.button() == Qt_LeftButton):
			print("ImageQGV.mouseReleaseEvent():  Button pressed and released")
			if not self.rubberBand.isHidden():   # or  self.rubberBand.isVisible()  ??
				self.rubberBand.hide()
				posScene = self.mapToScene(self.pos1)
				(x,y) = (int(posScene.x()), int(posScene.y()))
				posScene = self.mapToScene(event.pos())
				(w,h) = (int(posScene.x())-x, int(posScene.y())-y)
				self.rubberBandRectGiven.emit( QRect(x,y,w,h).normalized() )

	#end class ImageQGV


class ImageViewFrame(QFrame):
	"""This is the frame showing image information and the image itself, 
	it also prepare and handle image actions.
	An image is represented both as QPixmap and QImage to allow for flexible processing.
	"""
	imageChanged = pyqtSignal()    # emitted whenever the (displayed) image is changed

	def __init__(self, parent=None):
		""" Initialize ImageViewFrame, basically as for the inherited class 'QGraphicView'.
		Mouse tracking and (some) rubber band functionality is available in view.
		Fields for content is added, the image and text (imHead, imFile, and imPixel)
		"""
		super().__init__(parent)
		self.scaleUpFactor = 2.0     # or 1.4142135623730951 
		self.rubberBandActive = False 
		self.image = QImage()        # a null image
		self.prevImage = QImage()    # another (for previous image)
		self.scene = QGraphicsScene(parent=self)
		self.view = ImageQGV(self.scene, parent=self) 
		# 
		# layout
		# (w,h) = (self.width(), self.height())   # initially small!
		# print(f"ImageViewFrame.__init__(): {w=}, {h=}")
		# self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
		fontNormal = QFont()
		fontNormal.setPointSize(12)
		fontLarge = QFont()
		fontLarge.setPointSize(14)
		self.setMinimumSize(200,400) 
		self.setFrameStyle(QFrame_Box)
		self.imHead = QLabel('imHead: ', parent = self)
		self.imHead.setAlignment(Qt_AlignLeft | Qt_AlignVCenter)
		self.imHead.setFont(fontLarge)
		self.imFile = QLabel('imFile: ', parent = self)
		self.imFile.setAlignment(Qt_AlignLeft | Qt_AlignVCenter)
		self.imFile.setFont(fontNormal)
		self.imPixel = QLabel('imPixel: ', parent = self)
		self.imPixel.setAlignment(Qt_AlignHCenter | Qt_AlignBottom)
		self.imPixel.setFont(fontNormal)
		if qt6Exist:
			self.view.setGeometry( 5, 70, self.width()-10, self.height()-75 ) 
		else:
			self.view.setGeometry( 5, 100, self.width()-10, self.height()-105 ) 
		self.view.setFrameStyle(QFrame_Box)
	
	
	def resizeEvent(self, arg):
		""" Places the visual widgets in frame
		This method is a virtual method in QWidget, not a slot, thus no @pyqt decorator
		Anyway, it is called whenever the size of the frame changes.
		"""
		(w,h) = (self.width(), self.height())
		# print(f"ImageViewFrame.resizeEvent(): {w=}, {h=}")
		if qt6Exist:
			self.imHead.setGeometry( 5, 1, w-10, 28) 
			self.imFile.setGeometry( 5, 30, w-10, 20)   
			self.imPixel.setGeometry( 5, 50, w-10, 20) 
			self.view.setGeometry( 5, 70, w-10, h-75 ) 
		else:
			self.imHead.setGeometry( 5, 1, w-10, 35) 
			self.imFile.setGeometry( 5, 40, w-10, 27)   
			self.imPixel.setGeometry( 5, 70, w-10, 27) 
			self.view.setGeometry( 5, 100, w-10, h-105 ) 
			
	
	def populateImageMenu(self, menu):
		"""Usually called from parent
		"""
		# Actions for Image[View] menu 
		a = self.qaOpenImageFileDlg = QAction('Open image file', self)
		a.setShortcut('Ctrl+O')
		a.triggered.connect(self.openImageFileDlg)
		a = self.qaSaveImageFileDlg = QAction('Save image file', self)
		a.setShortcut('Ctrl+S')
		a.triggered.connect(self.saveImageFileDlg)
		a = self.qaClearImage = QAction('Clear image', self)
		a.setShortcut('Ctrl+C')
		a.setToolTip('Remove the current pixmap item from scene.')
		a.triggered.connect(self.clearImage)
		a = self.qaPrintImageInfo = QAction('Print image Info', self)
		a.setShortcut('Ctrl+I')
		a.triggered.connect(self.printImageInfo)
		#
		a = self.qaScaleOne = QAction('Scale 1', self)
		a.setShortcut('Ctrl+1')
		a.triggered.connect(self.scaleOne)
		a = self.qaScaleUp = QAction('Scale Up', self)
		a.setShortcut('Ctrl++')
		a.triggered.connect(self.scaleUp)
		a = self.qaScaleDown = QAction('Scale Down', self)
		a.setShortcut('Ctrl+-')
		a.triggered.connect(self.scaleDown)
		a = self.qaCrop = QAction('Crop image', self) 
		a.triggered.connect(self.cropStart)
		a.setToolTip('Crop the current image, select and indicate rectangle to keep')
		a.setShortcut('Ctrl+Y')  # as in IrfanView
		a = self.qaResize = QAction('Resize image', self)
		a.triggered.connect(self.resizeImage)
		a.setToolTip('Resize the current image') 
		a.setShortcut('Ctrl+R')  # as in IrfanView
		a = self.qaToGray = QAction('To Gray', self) 
		a.triggered.connect(self.toGray)
		a.setToolTip('Convert the current (RGB) image to gray scale, and display it')
		a.setShortcut('Ctrl+G')
		a = self.qaUndoLast = QAction('Undo last', self)
		a.setShortcut('Ctrl+Z')
		a.triggered.connect(self.undoLast)
		a = self.qaMakeHistogram = QAction('Make Histogram', self)
		a.setShortcut('Ctrl+H')
		a.triggered.connect(self.makeHistogram)
		# 
		menu.addAction(self.qaOpenImageFileDlg)
		menu.addAction(self.qaSaveImageFileDlg)
		menu.addAction(self.qaClearImage)
		menu.addAction(self.qaPrintImageInfo)
		menu.addAction(self.qaScaleOne)
		menu.addAction(self.qaScaleUp)
		menu.addAction(self.qaScaleDown)
		menu.addAction(self.qaCrop)
		menu.addAction(self.qaResize)
		menu.addAction(self.qaToGray)
		menu.addAction(self.qaUndoLast)
		menu.addAction(self.qaMakeHistogram)
		menu.setToolTipsVisible(True)
	
	
	def setMenuItems(self):
		"""Enable/disable menu items as appropriate.
		"""
		im = self.image
		isOk = not (im.isNull() or self.rubberBandActive)  # what is needed for most actions here
		isGray = (im.format() == QImage_Format_Grayscale8) 
		# print(f"ImageViewFrame.setMenuItems(): {im.format()=} --> {isOk=}, {isGray=}")
		self.qaOpenImageFileDlg.setEnabled(not self.rubberBandActive)
		self.qaSaveImageFileDlg.setEnabled(isOk)
		self.qaClearImage.setEnabled(isOk)
		self.qaPrintImageInfo.setEnabled(isOk)
		self.qaScaleOne.setEnabled(isOk)
		self.qaScaleUp.setEnabled(isOk)
		self.qaScaleDown.setEnabled(isOk) 
		self.qaCrop.setEnabled(isOk)
		self.qaResize.setEnabled(isOk)
		self.qaToGray.setEnabled(isOk and (not isGray))
		self.qaUndoLast.setEnabled(not self.prevImage.isNull())
		self.qaMakeHistogram.setEnabled(qtChartExist and isOk and isGray)
	
	
	def showImageOnScene(self, qim=None):  
		"""Copy qim, or |	, to a pixmap object and show it on scene.
		"""
		if qim == None: qim = self.image
		if (not qim.isNull()):
			# clear the scene
			for item in self.scene.items():      # remove all items in scene
				if item.parentItem() is None:    # skip child items
					self.scene.removeItem(item)  # as this also removes child items
			#
			pixmap = QPixmap.fromImage(qim)
			self.scene.addPixmap(pixmap)    
			self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
			self.scaleOne() 
		
		self.setMenuItems()
		self.imageChanged.emit()
	
	
	# Methods for open, save and close image file
	@pyqtSlot()
	def openImageFileDlg(self, fName: str = ""):   
		"""Open the image file as QImage object, self.image
		Used as a slot for qaOpenImageFileDlg, a QAction.triggered() signal where the cheched argument is ignored, 
		here fName="" and QFileDialog.getOpenFileName is used.
		Method can also be called with a file name argument
		"""
		#    the 'normal' way to define a  QAction.triggered() slot 
		# @pyqtSlot(bool)
		# def openImageFileDlg(self, checked: bool):
		print(f"ImageViewFrame.openImageFileDlg() started, {fName=}" )
		# we suppose format is given by 4 last chars of fName.lower()
		qtReadFormats = ['.bmp', '.cur', '.gif', '.ico', 'jfif', 'jpeg', '.jpg', \
		                 '.pbm', '.pgm', '.png', '.ppm', '.svg', 'svgz', '.xbm', '.xpm']
		# as given: https://doc.qt.io/qt-6/qpixmap.html#reading-and-writing-image-files 
		if (not isinstance(fName,str)) or (fName == ""):
			fName, used_filter = QFileDialog.getOpenFileName(
					parent=self, 
					caption="Open image file", 
					filter="PNG files (*.png);;BMP files (*.bmp);;JPG files (*.jpg);;All files (*)",
					# options=QFileDialog_DontUseNativeDialog | QFileDialog_HideNameFilterDetails, 
					directory=str(imagePath), 
			)
		# 
		self.viewImage(fName)   
		print(f"ImageViewFrame.openImageFileDlg() ended." )
	
	
	def viewImage(self, fName):   
		qim = myOpenImageFile(fName)
		if qim.isNull():
			print(f"  the image returned by myOpenImageFile('{fName}') isNull")
		elif isinstance(qim, QImage):
			self.image = qim 
			self.showImageOnScene()
			self.imHead.setText(f"Image, (w,h) = ({self.image.width()},{self.image.height()})")
			self.imFile.setText(f"{fName}")  # May have found image in another directory
		else:
			print(f"  the supplied image is not a QImage object")
	
	
	@pyqtSlot()
	def saveImageFileDlg(self):   
		"""Use the Qt QFileDialog.getSaveFileName to select file to save image into.
		Used as a slot for qaSaveImageFileDlg, a QAction.triggered() signal where the cheched argument is ignored, 
		Then save the QImage object in self.image into this file.
		"""
		fName, used_filter = QFileDialog.getSaveFileName(
				parent=self, 
				caption="Save image file as", 
				filter="PNG files (*.png);;BMP files (*.bmp);;JPG files (*.jpg);;All files (*)",
				# options=QFileDialog_DontUseNativeDialog | QFileDialog_HideNameFilterDetails, 
				directory=str(imagePath) 
		)
		if (fName != ""): 
			if self.image.save(fName):
				print(f"Saved image into file {fName}")
				self.imHead.setText(f"Saved image, (w,h) = ({self.image.width()},{self.image.height()})")
				self.imFile.setText(f"Filename: {fName}")
			else:
				print("Failed to save image into file {fName}")
	
	
	@pyqtSlot()
	def clearImage(self):
		"""Move the current image to prevImage and clear scene, view and image
		Used as a slot for qaClearImage, a QAction.triggered() signal where the cheched argument is ignored, 
		"""
		if not self.image.isNull(): 
			self.prevImage = self.image
			self.image = QImage()    # a new empty image 
		# 
		self.scene = QGraphicsScene(parent=self)  # clear scene
		self.view.setScene(self.scene) 
		self.rubberBandActive = False
		self.imHead.setText("No image") 
		self.imFile.setText("Filename: ")
		self.setMenuItems()
		self.imageChanged.emit()


	# ***** Methods for actionFs on the Image menu *********************************************
	@pyqtSlot()
	def scaleOne(self):
		"""Scale to 1, i.e. set the transform to identity matrix
		"""
		if not self.image.isNull():
			self.view.setTransform(QTransform())  # identity
	
	
	@pyqtSlot()
	def scaleUp(self):
		"""Scale up the view by factor set by 'self.scaleUpFactor'
		"""
		if not self.image.isNull():
			self.view.scale(self.scaleUpFactor, self.scaleUpFactor)  
	
	
	@pyqtSlot()
	def scaleDown(self):
		"""Scale down the view by factor set by 1.0/'self.scaleUpFactor'
		"""
		if not self.image.isNull():
			self.view.scale(1.0/self.scaleUpFactor, 1.0/self.scaleUpFactor)  
	
	
	@pyqtSlot()
	def undoLast(self):
		"""Undo last (edit) operation.
		"""
		(w, h) = (self.prevImage.width(), self.prevImage.height())
		if (w > 0) and (h > 0):
			self.image.swap(self.prevImage)  
			self.showImageOnScene()
			self.imHead.setText(f"Previous image, (w,h) = ({w},{h})")
			self.imFile.setText("Filename: ")
	
	
	@pyqtSlot()
	def cropStart(self):
		"""Set crop active, rubber band is turned on when left mouse button is pressed
		"""
		if (not self.image.isNull()):
			self.rubberBandActive = True
			self.view.rubberBandRectGiven.connect(self.cropEnd)
			self.imHead.setText("Use mouse click-and-drag to select crop rectangle")
			self.setMenuItems()
			print("ImageFrameView.cropStart(): Use rubber band to indicate the rectangle to keep, or just click to cancel crop.")
	
	
	@pyqtSlot(QRect)
	def cropEnd(self, rectangle):
		"""Crop the current image using the input rectangle. 
		A (very) small rectangle should do nothing.
		"""
		if self.rubberBandActive:  
			self.rubberBandActive = False
			self.view.rubberBandRectGiven.disconnect(self.cropEnd)
			p2 = rectangle.topLeft()
			# p3 = rectangle.bottomRight()
			(w, h) = (rectangle.width(), rectangle.height())
			if (w > 8) and (h > 8):
				print( (f"cropEnd(): Rectangle from (x,y)=({p2.x()},{p2.y()}) and (w,h)=({w},{h})") )
				self.prevImage = self.image
				self.image = self.prevImage.copy(p2.x(), p2.y(), w, h)
				self.showImageOnScene()
				self.imHead.setText(f"Cropped image, (w,h) = ({w},{h})")
				self.imFile.setText("Filename: ")
			else: 
				self.imHead.setText(f"Image, (w,h) = ({self.image.width()},{self.image.height()})")
	
	
	@pyqtSlot()
	def resizeImage(self):
		"""Resize the current image and copy (move) it back to current
		"""
		d = ResizeDialog(parent=self)           # create object (but does not run it)
		(newWidth, newHight) = d.getValues()    # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			print(f"resizeImage(): {newWidth=},  {newHight=}")
			self.prevImage = self.image 
			self.image = self.image.scaled(newWidth, newHight, Qt_IgnoreAspectRatio, Qt_FastTransformation)
			self.showImageOnScene()
			self.imHead.setText(f"Resized image, (w,h) = ({self.image.width()},{self.image.height()})")
			self.imFile.setText("Filename: ")
	
	
	@pyqtSlot()
	def toGray(self):
		"""Convert the current color image into a gray scale image
		and copy (move) it back to current pixmap
		"""
		if (self.image.isNull()) or (self.image.format() == QImage_Format_Grayscale8):
			print( "toGray: self.image is empty or a gray scale image." )
		else:
			self.prevImage = self.image.copy() 
			self.image.convertTo(QImage_Format_Grayscale8)
			self.showImageOnScene()
			self.imHead.setText(f"Grayscale image, (w,h) = ({self.image.width()},{self.image.height()})")
			self.imFile.setText("Filename: ")
	
	
	@pyqtSlot()
	def makeHistogram(self):
		"""Make histogram of the image and include it as QChart in self.scene
		This is only done when image format is Format_Grayscale8 
		"""
		if not qtChartExist: 
			# this should not happen as qtChartExist is checked in , but to be sure:
			print(f"ImageFrameView.makeHistogram(): Just return as QChart is not installed.")
			return
		#
		if (self.image.format() == QImage_Format_Grayscale8):
			B = qimage2np(self.image) 
			if not (B.dtype == np.uint8):  
				print(f"( 816) Warning: {B.dtype=}")
				return
			#
			data = np.bincount(B.ravel(), minlength=256)
			(a,b,s,nz) = (int(np.min(data)),  int(np.max(data)),  int(np.sum(data)), np.count_nonzero(data))
			print(f"Histogram data: Min={a}, Max={b}, Sum={s}, Number of non-zeros={nz}")
			non_zeros = data[data != 0]   # Filter out non-zero elements
			mean_non_zeros = np.mean(non_zeros)  # # Compute the mean
			print(f"Mean of {len(non_zeros)} non-zero elements: {mean_non_zeros:.2f}")
			# the counts of grayscale values in each bin is in a "bar set", https://doc.qt.io/qt-6/qbarset-qtcharts.html 
			grayBins = QBarSet('Histogram', parent=self)   # label must be included 
			grayBins.append(data.tolist())
			# grayBins.append(np.log10(data+1).tolist())
			grayBins.setColor(QColor('gray'))
			grayBins.setBorderColor(QColor('gray'))
			print(f"{grayBins=}, \n{grayBins.count()=}, {int(grayBins.at(12))=}, {int(grayBins.sum())=}")
			# x-axis
			axisX = QValueAxis()
			axisX.setRange(0, 256)
			axisX.setLabelFormat("%d")
			axisX.setTickCount(9)  # Show 8 intervals (9 ticks)
			print(f"{axisX=}, \n{axisX.alignment()=}, {axisX.isVisible()=}")
			# axisX.setVisible(False)
			# y-axis 
			axisY = QValueAxis()
			axisY.setRange(0, data.max())
			# axisY.setRange(0, np.log10(data.max()+1))
			axisY.setLabelFormat("%d")
			# axisY.setTickCount(9)  # Show 8 intervals (9 ticks)
			# series, https://doc.qt.io/qt-6/qbarseries-qtcharts.html
			# and the chart
			series = QBarSeries()
			series.append(grayBins)
			c = self.chartHist = QChart()
			c.addSeries(series)       # must add series to chart, then axis 
			c.addAxis(axisX, Qt_AlignBottom)
			c.addAxis(axisY, Qt_AlignLeft)
			series.attachAxis(axisX)  # before axis is attached
			series.attachAxis(axisY)
			print(f"{series=}, {series.count()=}")
			c.setTitle(f"Image Histogram, {nz} non-zero bins of {len(data)} bins")
			c.legend().hide()
			c.setAnimationOptions(QChart_SeriesAnimations) # or NoAnimation 
			c.setGeometry(0, B.shape[0]+5, 600, 400)
			self.scene.addItem(c)
			self.scene.setSceneRect(0, 0, 600, B.shape[0]+405)
			self.view.setRenderHint(QPainter_Antialiasing)
			# self.view.show()  # ??
			#
		else:
			print(f"ImageFrameView.makeHistogram(): {self.image.format()=} is not as it should be here.")
		#
		print(f"ImageFrameView.makeHistogram(): done")
	
	
	@pyqtSlot()
	def onlyHistogram(self, hist, edges, text=''):
		"""Make histogram of supplied data and include it as QChart in self.scene
		hist:  1D numpy array of length N
		edges: 1D numpy array of length N+1 (float bin edges)
		"""
		if not qtChartExist: 
			# this should not happen as qtChartExist is checked in , but to be sure:
			print(f"ImageFrameView.onlyHistogram(): Just return as QChart is not installed.")
			return
		#
		print(f"ImageFrameView.onlyHistogram(): cleared image")
		self.clearImage()
		# print(f"Arguments     {hist.shape=}, {hist.dtype.name=}, {edges.shape=}, {edges.dtype.name=} " )
		# (a,b,s,nz) = (int(np.min(hist)),  int(np.max(hist)),  int(np.sum(hist)), np.count_nonzero(hist))
		# print(f"Histogram data: Min={a}, Max={b}, Sum={s}, Number of non-zeros={nz}")
		# print(f"Edges: {edges[0]=:8.3f}, {edges[-1]=:8.3f}, {len(edges)=}")
		# non_zeros = hist[hist != 0]   # Filter out non-zero elements
		# mean_non_zeros = np.mean(non_zeros)  # # Compute the mean
		# max_non_zeros = np.max(non_zeros)  # # Compute the max
		# print(f"Mean of {len(non_zeros)} non-zero elements: {mean_non_zeros:.2f},  {max_non_zeros=:.2f}")
		#
		nz = np.count_nonzero(hist)
		# Compute bin centers from edges
		centers = 0.5 * (edges[:-1] + edges[1:])
		# Create the line series
		series = QLineSeries()
		series.setColor(QColor("gray"))
		# Add points (x = bin center, y = count)
		for x, y in zip(centers, hist):
			series.append(float(x), float(y))
		# Create the chart
		chart = self.chartHist = QChart()
		chart.addSeries(series)
		chart.legend().hide()
		chart.setTitle(f"Supplied Histogram, {nz} non-zero bins of {len(hist)} bins")
		chart.setAnimationOptions(QChart_SeriesAnimations) # or NoAnimation 
		chart.setGeometry(0, 5, 600, 400)
		# X axis (float range)
		axisX = QValueAxis()
		(a,b) = rounded_range(edges[0], edges[-1])
		axisX.setRange(float(a),float(b))
		rangeX = float(b-a)
		if rangeX < 50:
			axisX.setLabelFormat("%.3f")
		elif rangeX < 500:
			axisX.setLabelFormat("%.1f")
		else:
			axisX.setLabelFormat("%.0f")
		axisX.setTitleText("Value")
		axisX.setTickCount(9)  # Show 8 intervals (9 ticks)
		chart.addAxis(axisX, Qt_AlignBottom)
		series.attachAxis(axisX)
		# Y axis
		axisY = QValueAxis()
		axisY.setRange(0, float(hist.max()))
		axisY.setLabelFormat("%d")
		axisY.setTitleText("Count")
		chart.addAxis(axisY, Qt_AlignLeft)
		series.attachAxis(axisY)
		#
		self.scene.addItem(chart)
		self.scene.setSceneRect(0, 0, 600, 410)
		self.view.setRenderHint(QPainter_Antialiasing)
	
	
	@pyqtSlot()
	def printImageInfo(self):
		"""Print some general (debug) information for the program and the image.
		Mainly for debug purposes.
		"""
		print(f"ImageViewFrame.printInfo(): in {_fileName}" )
		print( "Print some elements of ImageViewFrame object.")
		print( f"self.parent          = {str(self.parent())}" )
		print( f"self                 = {str(self)}" )
		print( f"  .pos()             = {str(self.pos())}" )
		print( f"  .size()            = {str(self.size())}" )
		print( f"  .rubberBandActive  = {str(self.rubberBandActive)}" )
		print( f"  .scaleUpFactor     = {str(self.scaleUpFactor)}" )
		#
		print( f"self.view()          = {str(self.view)}" )
		print( f"  .size()            = {str(self.view.size())}" )
		t = self.view.transform()
		print( f"  .transform()       = {str(t)}" )
		print( f"    .m11, .m12, .m13 = [{t.m11():5.2f}, {t.m12():5.2f}, {t.m13():5.2f}, " )
		print( f"    .m21, .m22, .m23 =  {t.m21():5.2f}, {t.m22():5.2f}, {t.m23():5.2f}, " )
		print( f"    .m31, .m32, .m33 =  {t.m31():5.2f}, {t.m32():5.2f}, {t.m33():5.2f} ]" )
		print( f"self.scene           = {str(self.scene)}" )
		print( f"  .parent()          = {str(self.scene.parent())}" )
		print( f"  .sceneRect()       = {str(self.scene.sceneRect())}" )
		print( f"  number of items    = {len(self.scene.items())}  (show only items that has no parentItem)" )
		for item in self.scene.items(Qt.SortOrder.DescendingOrder):
			if item.parentItem() == None:
				print( f"  item               = {str(item)}" )
		#
		print( f"self.prevImage       = {str(self.prevImage)}" )
		print( f"self.image           = {str(self.image)}" )
		if not self.image.isNull():
			print( f"  .size()            = {self.image.size()}" )
			print( f"  .width()           = {self.image.width()}" )
			print( f"  .height()          = {self.image.height()}" )
			print( f"  .depth()           = {self.image.depth()}" )
			print( f"  .hasAlphaChannel() = {self.image.hasAlphaChannel()}" )
			print( f"  .format()          = {self.image.format()}" )
			# print( f"  .allGray()         = {self.image.allGray()}" )
		#
		if hasattr(self, 'chartHist') and self.chartHist is not None:
			print( f"self.chartHist       = {self.chartHist}" )
			print( f"  plotArea()         = {self.chartHist.plotArea()}" )
			series = self.chartHist.series()
			for i in range(min(2,len(series))):
				print( f"  series[{i}]          = {series[i]}" )
				print( f"  mapToValue(..)     = {self.chartHist.mapToValue(QPointF(514,180), series[i]).x():.0f}" )
				if hasattr(series[i], 'barSets'):
					barSets = series[i].barSets()
					for j in range(min(2,len(barSets))):
						print( f"    barSets[{j}]       = {barSets[j]}" )
						print( f"      value at(232)  = {barSets[j].at(232):.0f}" )
	
	#end class ImageViewFrame
	
class TestWindow(QMainWindow):  
	"""TestWindow class for the ImageViewFrame class.
	"""
	
	def __init__(self, parent=None, fName=""):
		"""Initialize the test window object with title, location and size,
		A image file name 'fName' may be given as input (from command line when program is started)
		and if so this image will be opened and displayed.
		"""
		print(f"File {_fileName}: TestWindow.__init__() started" )
		super().__init__(parent) 
		self.setGeometry(150, 50, 800, 1200)  # initial window position (x,y) and size (w,h)
		#
		self.imFrame = ImageViewFrame(parent=self)
		self.initMainMenu() 
		#
		if isinstance(fName, str) and (fName != ""):
			self.imFrame.openImageFileDlg(fName)
		#
		self.imFrame.setMenuItems()
		#
		print(f"File {_fileName}: TestWindow.__init__() ended" )
		return
	
	
	def initMainMenu(self):
		"""Initialize File, Image, and Report menus."""
		print(f"File {_fileName}: TestWindow.initMainMenu() started" )
		#
		a = self.qaQuitProgram = QAction('Quit', self)
		a.setShortcut('Ctrl+Q')
		a.setToolTip('Close and quit program')
		a.triggered.connect(self.quitProgram)
		#
		# menuBar is a function in QMainWindow class, returns a QMenuBar object
		self.mainMenu = self.menuBar()  
		self.fileMenu = self.mainMenu.addMenu('&File')
		self.fileMenu.addAction(self.qaQuitProgram)
		self.fileMenu.setToolTipsVisible(True)
		#
		self.imageMenu = self.mainMenu.addMenu('&Image')   # in imView
		self.imFrame.populateImageMenu(self.imageMenu)
		#
		reportMenu = self.mainMenu.addMenu('&Report')   
		reportMenu.addAction(self.imFrame.qaPrintImageInfo)
		#
		print(f"File {_fileName}: TestWindow.initMainMenu() ended" )
		return
	
	
	def mousePressEvent(self, event):
		"""Just print which mouse button has been pressed in test window.
		Note that the frame catches most mouse events, so this does only happen
		when mouse is on the bottom of the test window
		Normally we are fine if this function does nothing.
		"""
		if (event.button() == Qt_LeftButton):
			print("TestWindow: LeftButton pressed at:  " + str(event.pos()))
		if (event.button() == Qt_RightButton):
			print("TestWindow: RightButton pressed at: " + str(event.pos()))
		return
	
	
	def resizeEvent(self, arg1):
		"""Make the size of the frame follow any changes in the size of the test window.
		This method is a 'slot' that is called whenever the size of the test window changes.
		"""
		self.imFrame.setGeometry( 10, 30, self.width()-20, self.height()-40 ) 
		return
	
	
	@pyqtSlot()
	def quitProgram(self):
		"""Quit program."""
		print( "Close the test window and quit program." )
		self.close()   # the correct way to quit, is as (upper right) window frame symbol "X" 
		return
	
#end class TestWindow


if __name__ == '__main__':
	print( f"{_fileName}: (version {_version}) and using Qt {QT_VERSION_STR}" )
	testApp = QApplication(sys.argv)
	if (len(sys.argv) >= 2):
		fn = sys.argv[1]
		testWin = TestWindow(fName=fn)
	else:
		testWin = TestWindow()
	testWin.show()
	if qt6Exist:
		sys.exit(testApp.exec())
	else:
		sys.exit(testApp.exec_())
