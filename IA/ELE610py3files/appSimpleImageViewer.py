77#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/appSimpleImageViewer.py
#
#  Simple program that uses Qt to display an image, only basic options.
#    File menu: Open File, and Quit
#    Scale menu: Scale Up, and Scale down
#
#  This example is basically an even more simple version of the Qt documentation example, in C++, 
#  at https://doc.qt.io/qt-5/qtwidgets-widgets-imageviewer-example.html, Here 'translated' to Python.
#
# Karl Skretting (KS), UiS, September - November 2018, November 2021, June 2022, November 2025
# KS, August 2024 May use either PyQt6 (preferred) or PyQt5
# KS, November 2025 Use mySystem.py and some other minor changes
# KS, March 2026 import Qt via mySystem

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3>activate py12
# (py12) C:\..\py3>python appSimpleImageViewer.py

_fileName = "appSimpleImageViewer"
_author = "Karl Skretting, UiS" 
_version = "2026.03.13"     # yyyy.mm.dd

import sys
#
# Qt
from mySystem import QT_BINDING, qt5Exist, qt6Exist, imagePath
if QT_BINDING == "None":
	print("Importing Qt failed.")
	raise ImportError(f"{_fileName}: Requires PyQt6, PySide6 or PyQt5")
else: # ok
	from mySystem import (QT_VERSION_STR, QAction, QPixmap, QTransform, pyqtSlot, 
	  QApplication, QGraphicsScene, QGraphicsView, QFileDialog, QMainWindow, 
	  QFileDialog_DontUseNativeDialog, QFileDialog_HideNameFilterDetails)


class MainWindow(QMainWindow):
	"""MainWindow class for a simple image viewer.
	"""
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setWindowTitle("Simple Image Viewer")
		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene, parent=self)
		self.setGeometry(150, 50, 1200, 800)  # initial window position and size
		#
		# Set up the menu for main window: File with Open and Quit, Scale with + and -
		qaOpenFile = QAction('openFile', self)
		qaOpenFile.setShortcut('Ctrl+O')
		qaOpenFile.setStatusTip('Open (image) File using dialog box')
		qaOpenFile.triggered.connect(self.openFile)
		qaQuitProgram = QAction('quitProgram', self)
		qaQuitProgram.setShortcut('Ctrl+Q')
		qaQuitProgram.setStatusTip('Close and quit program')
		qaQuitProgram.triggered.connect(self.quitProgram)
		qaScaleUp = QAction('scaleUp', self)
		qaScaleUp.setShortcut('Ctrl++')
		qaScaleUp.triggered.connect(self.scaleUp)
		qaScaleDown = QAction('scaleDown', self)
		qaScaleDown.setShortcut('Ctrl+-')
		qaScaleDown.triggered.connect(self.scaleDown)
		#
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(qaOpenFile)
		fileMenu.addAction(qaQuitProgram)
		scaleMenu = mainMenu.addMenu('&Scale')
		scaleMenu.addAction(qaScaleUp)
		scaleMenu.addAction(qaScaleDown)
	
	
	def resizeEvent(self, arg1):
		"""Make the size of the view follow any changes in the size of the main window.
		"""
		self.view.setGeometry( 0, 20, self.width(), self.height()-20 ) 
	
	
	@pyqtSlot()
	def openFile(self):   
		"""Use the Qt file open dialog to select an image to open as a pixmap, 
		The pixmap is added as an item to the graphics scene which is shown in the graphics view.
		The view is scaled to unity.
		"""
		fName, used_filter = QFileDialog.getOpenFileName(
				parent=self, 
				caption="Open image file", 
				directory=str(imagePath), 
				filter="JPG files (*.jpg);;BMP files (*.bmp);;PNG files (*.png);;All files (*)", 
				options=QFileDialog_DontUseNativeDialog  # | QFileDialog_HideNameFilterDetails
		)
		#
		if (fName != ""):
			pixmap = QPixmap()
			pixmap.load(fName)
			# If the file does not exist or is of an unknown format, the pixmap becomes a null pixmap.
			if pixmap.isNull():
				self.setWindowTitle( f"Image Viewer (error for file {fName})" )
			else: # ok
				for item in self.scene.items():      # remove all items in scene
					if item.parentItem() is None:    # skip child items
						self.scene.removeItem(item)  # as this also removes child items
				#
				self.scene.addPixmap(pixmap)    
				self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
				self.setWindowTitle('Simple Image Viewer: ' + fName)
				self.view.setTransform(QTransform())  # identity (for scale)
	
	
	@pyqtSlot()
	def quitProgram(self):            
		"""Quit program, actually not needed as qaQuitProgram could be connected directly to self.close
		"""
		print("Close the main window and quit program.")
		self.close()   
	
	
	@pyqtSlot()
	def scaleUp(self):
		"""Scale up the view by factor 2
		"""
		self.view.scale(2,2)  
	
	
	@pyqtSlot()
	def scaleDown(self):
		"""Scale down the view by factor 0.5
		"""
		self.view.scale(0.5,0.5)  
	
#end class MainWindow
		
if __name__ == '__main__':
	print( f"{_fileName}: (version {_version}), using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	if qt6Exist:
		sys.exit(mainApp.exec())
	else:
		sys.exit(mainApp.exec_())
	
