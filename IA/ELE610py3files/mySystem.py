#!/usr/bin/env python3
# -*- coding: utf-8 -*-  (no Byte Order Mark, BOM)
#
# ../ELE610/py3/mySystem.py 
#
# This file defines variables to reflect (my) PC setup and (my) Python setup.
# In particular it should identify which Qt binding and version to use depending on
# what is installed in running environment. Priority is PyQt6, PySide6, and PyQt5 
#
# Other variables indicate which Python packages that are available, i.e. Numpy, OpenCV
# This may vary with the Anaconda environment activated (and the computer). 
# Variables are now, after March 2026:
#   npExist, cv2Exist, qt5Exist, qt6Exist, qtChartExist, QT_BINDING

# This file also contains some function:  
#   findMyDropbox, findMyImageFile
# and some other variables that indicate where (my) files are stored locally: 
#   gpxPath, imagePath        ###  OBS:  heime er jeg ikke 2900780 !!  Må endre på slutten her
#
# Karl Skretting, UiS
# October 2025 (KS): made file based on myTools.py, copied to  myTools.Okt25
# January 2026 (KS): minor corrections
# March 2026 (KS): Change how Qt is handled
#
# Example on how to use file:
#   >>> from mySystem import QT_BINDING, qt5Exist, qt6Exist, qtChartExist, imagePath 
#   >>> from mySystem import findMyDropbox, findMyImageFile
# Test:
#   ..\py3>python mySystem.py Kåre Ørn    # a simple test

_fileName = "mySystem.py"
_author = "Karl Skretting, UiS" 
_version = "2026.06.02"      # "yyyy.mm.dd"

import sys
import os    # ex: os.name is used
import re 
from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 

print(f"\n** {_fileName}: versjon {_version},  {_author}")
# 
try:
	import numpy as np
	npExist = True
except ImportError:
	npExist = False
#
try:
	import cv2
	cv2Exist = True    
except ImportError:
	cv2Exist = False
#
# mplExist      ? for matplotlib
# scipyExist    ? for scipy
print(f"Python {sys.version} on {sys.platform}\n{npExist=}, {cv2Exist=}")

# now check Qt  #  Qt6 documentation: https://doc.qt.io/qt-6/classes.html 
# Perhaps rather check for 'PyQt6' (or 'PyQt5' or other) module in sys.modules, ex: 'PyQt6' in sys.modules
# All Qt classes I use should be imported here, then program that need Qt import what is needed from this file
# ex: from mySystem import QApplication, QWidget, pyqtSignal, pyqtSlot, QRect, qt6Exist, QT_BINDING
#     from mySystem import QT_BINDING, qt5Exist, qt6Exist, qtChartExist
try:
	from PyQt6.QtCore import (Qt, QFileInfo, QObject, QPoint, QPointF, QRect, 
	  pyqtSignal, QSize, pyqtSlot, QThread, QTime, QTimer, QUrl, QT_VERSION_STR)
	from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QBoxLayout, 
	  QButtonGroup, QColorDialog, QComboBox, QCheckBox, 
	  QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame,
	  QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGridLayout, QHBoxLayout, 
	  QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMdiArea, QMessageBox, 
	  QProgressDialog, QPushButton, QRadioButton, QRubberBand, QSizePolicy, QSlider, QSpinBox, QSplitter, 
	  QTableWidget, QTableWidgetItem, QTextBrowser, QTextEdit, QVBoxLayout, QWidget)
	from PyQt6.QtGui import (QAction, QBrush, QColor, QFont, QIcon, QImage, QImageReader, QKeySequence, 
	  QPainter, QPainterPath, QPen, QPixmap, QPolygon, QTransform, QValidator)
	QT_BINDING = "PyQt6"
	qt6Exist = True 
except ImportError:
	qt6Exist = False

if not qt6Exist:  
	try:
		from PySide6.QtCore import (Qt, QFileInfo, QObject, QPoint, QPointF, QRect, 
		  Signal as pyqtSignal, QSize, Slot as pyqtSlot, 
		  QThread, QTime, QTimer, QUrl, __version__ as QT_VERSION_STR)
		from PySide6.QtWidgets import (QAbstractItemView, QApplication, QBoxLayout, 
		  QButtonGroup, QColorDialog, QComboBox, QCheckBox, 
		  QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, 
		  QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGridLayout, QHBoxLayout, 
		  QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMdiArea, QMessageBox, 
		  QProgressDialog, QPushButton, QRadioButton, QRubberBand, QSizePolicy, QSlider, QSpinBox, QSplitter, 
		  QTableWidget, QTableWidgetItem, QTextBrowser, QTextEdit, QVBoxLayout, QWidget)
		from PySide6.QtGui import (QAction, QBrush, QColor, QFont, QIcon, QImage, QImageReader, QKeySequence, 
		  QPainter, QPainterPath, QPen, QPixmap, QPolygon, QTransform, QValidator)
		QT_BINDING = "PySide6"
		qt6Exist = True 
	except ImportError:
		qt6Exist = False

if not qt6Exist:   # i.e. neither PyQt6 nor PySide6
	try:           # thus try PyQt5 
		from PyQt5.QtCore import (Qt, QFileInfo, QObject, QPoint, QPointF, QRect, 
		  pyqtSignal, QSize, pyqtSlot, QThread, QTimer, QUrl, QT_VERSION_STR)
		from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication, QBoxLayout, 
		  QButtonGroup, QColorDialog, QComboBox, QCheckBox, 
		  QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, 
		  QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGridLayout, QHBoxLayout, 
		  QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMdiArea, QMessageBox, 
		  QProgressDialog, QPushButton, QRadioButton, QRubberBand, QSizePolicy, QSlider, QSpinBox, QSplitter, 
		  QTableWidget, QTableWidgetItem, QTextBrowser, QTextEdit, QVBoxLayout, QWidget)
		from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QImage, QImageReader, QKeySequence, 
		  QPainter, QPainterPath, QPen, QPixmap, QTransform, QValidator)
		QT_BINDING = "PyQt5"
		qt5Exist = True 
	except ImportError:
		QT_BINDING = "None"
		qt5Exist = False
		print("Importing Qt failed.")
		# don't raise any error, this file may be used also when Qt is not needed (wanted)
else:
	qt5Exist = False     # it may exist, but as qt6 is used, we set this as if it doesn't exist

# also check for QtChart
qtChartExist = False
if QT_BINDING == "PyQt6":
	try: # 
		from PyQt6.QtCharts import (QBarSeries, QBarSet, QBarCategoryAxis, QChart, 
				QChartView, QLineSeries, QScatterSeries, QValueAxis)
		qtChartExist = True
	except ImportError:
		pass

if QT_BINDING == "PySide6":
	try:
		from PySide6.QtCharts import (QBarSeries, QBarSet, QBarCategoryAxis, QChart, 
				QChartView, QLineSeries, QScatterSeries, QValueAxis)
		qtChartExist = True
	except ImportError:
		pass

if QT_BINDING == "PyQt5":
	try:
		from PyQt5.QtCharts import (QBarSeries, QBarSet, QBarCategoryAxis, QChart, 
				QChartView, QLineSeries, QScatterSeries, QValueAxis)
		qtChartExist = True
	except ImportError:
		pass

# enums are different in qt5 and qt6, variable names with underline may be used instead
# some are in the end of this file
if qt6Exist:
	QAbstractItemView_NoEditTriggers = QAbstractItemView.EditTrigger.NoEditTriggers
	QAbstractItemView_DoubleClicked = QAbstractItemView.EditTrigger.DoubleClicked 
	QAbstractItemView_SelectedClicked = QAbstractItemView.EditTrigger.SelectedClicked
	QAbstractItemView_SelectRows = QAbstractItemView.SelectionBehavior.SelectRows
	QAbstractItemView_SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
	QBoxLayout_LeftToRight = QBoxLayout.Direction.LeftToRight
	QBoxLayout_RightToLeft = QBoxLayout.Direction.RightToLeft
	QBoxLayout_TopToBottom = QBoxLayout.Direction.TopToBottom
	QDialogButtonBox_Apply = QDialogButtonBox.StandardButton.Apply
	QDialogButtonBox_ApplyRole = QDialogButtonBox.ButtonRole.ApplyRole
	QDialogButtonBox_Cancel = QDialogButtonBox.StandardButton.Cancel
	QDialogButtonBox_Ok = QDialogButtonBox.StandardButton.Ok
	QFileDialog_DontUseNativeDialog = QFileDialog.Option.DontUseNativeDialog
	QFileDialog_HideNameFilterDetails = QFileDialog.Option.HideNameFilterDetails
	QFrame_Box = QFrame.Shape.Box
	QFrame_HLine = QFrame.Shape.HLine
	QFrame_Panel = QFrame.Shape.Panel
	QFrame_Sunken = QFrame.Shadow.Sunken
	QHeaderView_Fixed = QHeaderView.ResizeMode.Fixed
	QHeaderView_ResizeToContents = QHeaderView.ResizeMode.ResizeToContents
	QHeaderView_Stretch = QHeaderView.ResizeMode.Stretch
	QImage_Format_Indexed8 = QImage.Format.Format_Indexed8
	QImage_Format_Grayscale8 = QImage.Format.Format_Grayscale8
	QImage_Format_RGB32 = QImage.Format.Format_RGB32
	QKeySequence_Delete = QKeySequence.StandardKey.Delete
	QMessageBox_Yes = QMessageBox.StandardButton.Yes
	QMessageBox_No = QMessageBox.StandardButton.No
	QMessageBox_Cancel = QMessageBox.StandardButton.Cancel
	QPainter_Antialiasing = QPainter.RenderHint.Antialiasing
	QRubberBand_Rectangle = QRubberBand.Shape.Rectangle
	QSizePolicy_Expanding = QSizePolicy.Policy.Expanding
	QSizePolicy_Fixed = QSizePolicy.Policy.Fixed
	Qt_AlignCenter = Qt.AlignmentFlag.AlignCenter
	Qt_AlignLeft = Qt.AlignmentFlag.AlignLeft
	Qt_AlignRight = Qt.AlignmentFlag.AlignRight
	Qt_AlignHCenter = Qt.AlignmentFlag.AlignHCenter
	Qt_AlignVCenter = Qt.AlignmentFlag.AlignVCenter
	Qt_AlignTop = Qt.AlignmentFlag.AlignTop
	Qt_AlignBottom = Qt.AlignmentFlag.AlignBottom
	Qt_AscendingOrder = Qt.SortOrder.AscendingOrder
	Qt_Checked = Qt.CheckState.Checked 
	Qt_DescendingOrder = Qt.SortOrder.DescendingOrder 
	Qt_FastTransformation = Qt.TransformationMode.FastTransformation
	Qt_Horizontal = Qt.Orientation.Horizontal
	Qt_IgnoreAspectRatio = Qt.AspectRatioMode.IgnoreAspectRatio
	Qt_ItemIsEditable = Qt.ItemFlag.ItemIsEditable
	Qt_LeftButton = Qt.MouseButton.LeftButton
	Qt_NoPen = Qt.PenStyle.NoPen
	Qt_RightButton = Qt.MouseButton.RightButton
	Qt_SolidPattern = Qt.BrushStyle.SolidPattern
	Qt_Unchecked = Qt.CheckState.Unchecked 
	Qt_white = Qt.GlobalColor.white
	Qt_WindowModal = Qt.WindowModality.WindowModal
	QValidator_Acceptable = QValidator.State.Acceptable
	if qtChartExist:
		QChart_NoAnimation = QChart.AnimationOption.NoAnimation
		QChart_SeriesAnimations = QChart.AnimationOption.SeriesAnimations
		QScatterSeries_MarkerShapeRectangle = QScatterSeries.MarkerShape.MarkerShapeRectangle
elif qt5Exist:
	QAbstractItemView_NoEditTriggers = QAbstractItemView.NoEditTriggers
	QAbstractItemView_SelectRows = QAbstractItemView.SelectRows
	QAbstractItemView_DoubleClicked = QAbstractItemView.DoubleClicked 
	QAbstractItemView_SelectedClicked = QAbstractItemView.SelectedClicked
	QAbstractItemView_SingleSelection = QAbstractItemView.SingleSelection
	QBoxLayout_LeftToRight = QBoxLayout.LeftToRight
	QBoxLayout_RightToLeft = QBoxLayout.RightToLeft
	QBoxLayout_TopToBottom = QBoxLayout.TopToBottom
	QDialogButtonBox_Apply = QDialogButtonBox.Apply
	QDialogButtonBox_ApplyRole = QDialogButtonBox.ApplyRole
	QDialogButtonBox_Cancel = QDialogButtonBox.Cancel
	QDialogButtonBox_Ok = QDialogButtonBox.Ok
	QFileDialog_DontUseNativeDialog = QFileDialog.DontUseNativeDialog
	QFileDialog_HideNameFilterDetails = QFileDialog.HideNameFilterDetails
	QFrame_Box = QFrame.Box
	QFrame_HLine = QFrame.HLine
	QFrame_Panel = QFrame.Panel
	QFrame_Sunken = QFrame.Sunken
	QHeaderView_Fixed = QHeaderView.Fixed
	QHeaderView_ResizeToContents = QHeaderView.ResizeToContents
	QHeaderView_Stretch = QHeaderView.Stretch
	QImage_Format_Indexed8 = QImage.Format_Indexed8
	QImage_Format_Grayscale8 = QImage.Format_Grayscale8
	QImage_Format_RGB32 = QImage.Format_RGB32
	QKeySequence_Delete = QKeySequence.Delete
	QMessageBox_Yes = QMessageBox.Yes
	QMessageBox_No = QMessageBox.No
	QMessageBox_Cancel = QMessageBox.Cancel
	QPainter_Antialiasing = QPainter.Antialiasing
	QRubberBand_Rectangle = QRubberBand.Rectangle
	QSizePolicy_Expanding = QSizePolicy.Expanding
	QSizePolicy_Fixed = QSizePolicy.Fixed
	Qt_AlignCenter = Qt.AlignCenter
	Qt_AlignLeft = Qt.AlignLeft
	Qt_AlignRight = Qt.AlignRight
	Qt_AlignHCenter = Qt.AlignHCenter
	Qt_AlignVCenter = Qt.AlignVCenter
	Qt_AlignTop = Qt.AlignTop
	Qt_AlignBottom = Qt.AlignBottom
	Qt_AscendingOrder = Qt.AscendingOrder
	Qt_Checked = Qt.Checked 
	Qt_DescendingOrder = Qt.DescendingOrder 
	Qt_IgnoreAspectRatio = Qt.IgnoreAspectRatio
	Qt_ItemIsEditable = Qt.ItemIsEditable
	Qt_FastTransformation = Qt.FastTransformation
	Qt_Horizontal = Qt.Horizontal
	Qt_LeftButton = Qt.LeftButton
	Qt_NoPen = Qt.NoPen
	Qt_RightButton = Qt.RightButton
	Qt_SolidPattern = Qt.SolidPattern
	Qt_Unchecked = Qt.Unchecked 
	Qt_white = Qt.white
	Qt_WindowModal = Qt.WindowModal
	QValidator_Acceptable = QValidator.Acceptable
	if qtChartExist:
		QChart_NoAnimation = QChart.NoAnimation
		QChart_SeriesAnimations = QChart.SeriesAnimations
		QScatterSeries_MarkerShapeRectangle = QScatterSeries.MarkerShapeRectangle

print(f"Qt6 versions: {('PySide6' in sys.modules)=}, {('PyQt6' in sys.modules)=}")
print(f"Qt5 version: {('PyQt5' in sys.modules)=} and {qtChartExist=}, --> {QT_BINDING=}")


# Functions for file locations 
def DBpath( navn='' ):
	"""This function is depreciated, rather use: findMyDropbox
	Now, from October 2025, this function just do: return findMyDropbox(subdir=navn)
	"""
	return findMyDropbox(subdir=navn)
	
def findMyDropbox(subdir=''):
	"""Returns the path to my personal Dropbox directory as a Path object.
	If a string argument is given, this may be a subdirectory in my Dropbox.
	Some 'short names' can be used as well: 
	  'm610' (Matlab-files for ELE610)
	  'm620' (Matlab-files for ELE620)
	  'py' or 'py3' (Python-files for ELE610)
	  'l610' or 'ele610' (LaTeX-files for ELE610)
	The directory is returned as a Path object.
	If the subdirectory is not found the Dropbox directory is returned,
	if my Dropbox is not found Path.cwd() is returned.
	
	Examples:
	  p = findMyDropbox() 
	  p = findMyDropbox( 'Matlab/ele610' )   or   
	  p = findMyDropbox( 'Matlab\\ele610' ) 
	"""
	if (len(subdir) >= 2):  # replace short name by subdir
		if   subdir.lower() == 'turkart': subdir = 'TurKart'
		elif subdir.lower() == 'm610':    subdir = 'Matlab/ele610'
		elif subdir.lower() == 'm620':    subdir = 'Matlab/ele620'
		elif subdir[:2].lower() == 'py':  subdir = 'ELE610/py3'
		elif subdir.lower() == 'l610':    subdir = 'ELE610/2026'
		elif subdir.lower() == 'ele610':  subdir = 'ELE610/2026'
		elif subdir.lower() == 'l310':    subdir = 'ELE310/2025'
		elif subdir.lower() == 'ele310':  subdir = 'ELE310/2025'
	#
	# check if location is ../Dropbox/..  
	pD = [a for a in Path.cwd().parents if str(a)[-7:] == 'Dropbox']
	if not len(pD): 
		pD = [a for a in Path.home().iterdir() if a.is_dir() and str(a)[-7:] == 'Dropbox']
	if not len(pD):
		print( "findMyDropbox(): Can't locate Dropbox directory, try Documents" )
		pD = [a for a in Path.cwd().parents if str(a)[-9:] == 'Documents']
	if not len(pD):
		pD = [a for a in Path.home().iterdir() if a.is_dir() and str(a)[-9:] == 'Documents']
	#
	if len(pD):   # assume pD[0] is my Dropbox directory (or Documents)
		if len(subdir) and (pD[0] / subdir).is_dir():   
			myPath = pD[0] / subdir
		else:
			myPath = pD[0]
		# 
		if not myPath.is_dir():  
			print( f"findMyDropbox(): {subdir} not found as a directory in my Dropbox." )
			myPath = pD[0] 
	else:
		myPath = Path.cwd()
		print( "findMyDropbox(): Can't locate Dropbox or Documents, returns " + str(myPath) )
	#
	return myPath

def findMyImageFile(fn: str | Path) -> Path:
	"""Look for file as given by fn, a string or Path object, in some directories
	where images may be stored. Don't check if the file is actually an image, 
	nor that the file name has a suffix common for image files.
	If the file is not found, i.e. not fn.is_file(), fn (as a Path object) is returned anyway.
	"""
	if isinstance(fn, str): fn = Path(fn) 
	if not isinstance(fn, Path): 
		fn = Path.cwd()   
		return fn
	#
	if not fn.exists(): # not an existing file or directory 
		dList = [Path.cwd(), imagePath, Path.home(), findMyDropbox('ELE610/fig')]
		dList.extend([d for d in imagePath.iterdir() if d.is_dir()])  
		# to find thousands of images, directory below should be searched recursively (KarlsBilder.rglob)
		KarlsBilder = Path("C:\\Karl\\Bilder")
		if KarlsBilder.is_dir():
			dList.extend([d for d in KarlsBilder.iterdir() if d.is_dir()]) 
		name = fn.name 
		for d in dList:
			if (d / name).is_file():
				fn = d / name
				break
			if (d / fn).is_file():
				fn = (d / fn).resolve()
				break
	#
	return fn

dbPath = findMyDropbox()
if Path("C:/Users/2900780").exists() or ((dbPath / 'TurKart').is_dir() and (dbPath / 'ELE610').is_dir()):  
	# UiS User Karl or at least my DropBox is available
	try:
		imagePath = Path("\\\\FIL03\\emp01\\2900780\\Documents\\My Pictures")
		if not imagePath.exists():   # may give PermissionError
			imagePath = Path.cwd()
	except:
		imagePath = Path.cwd()
	#
	print(f"Some image files may be in directory: imagePath = {str(imagePath)}")
	#
	try:
		gpxPath = findMyDropbox('turkart')  # Dropbox path where my gpx-files are stored 
		if not gpxPath.exists(): 
			gpxPath = Path.cwd()
	except:
		gpxPath = Path.cwd()
	#		
	print(f"My gpx-files may be in directory: gpxPath = {str(gpxPath)}\n")
else:  # all other users (any student)
	imagePath = Path.cwd()
	gpxPath = Path.cwd()
#
# imagePath is used in myOpenImageFile(), in funImageTool.py
# gpxPath in my map, track and gpx app: appMyTrack.py (i.e. files used in that app)



# *********************** TEST functions ************************* #

def test01(arg):
	print("test01(): arguments passed to test function, and print of 'æøåÆØÅ'" )
	name = 'Karl'
	print( 'Hei og hopp', name )
	for name in arg[1:]:
		print( 'Hei også til', name )
	return
	
if __name__ == '__main__':
	test01(sys.argv)
	pass


"""
All (?) enums changes:
Qt5 → Qt6 ENUM CHANGES (compact cheat‑sheet)

QFrame:
QFrame.Box → QFrame.Shape.Box
QFrame.Panel → QFrame.Shape.Panel
QFrame.StyledPanel → QFrame.Shape.StyledPanel
QFrame.HLine → QFrame.Shape.HLine
QFrame.VLine → QFrame.Shape.VLine
QFrame.Raised → QFrame.Shadow.Raised
QFrame.Sunken → QFrame.Shadow.Sunken

Qt.WindowFlags:
Qt.Window → Qt.WindowType.Window
Qt.Dialog → Qt.WindowType.Dialog
Qt.Tool → Qt.WindowType.Tool
Qt.Popup → Qt.WindowType.Popup
Qt.FramelessWindowHint → Qt.WindowType.FramelessWindowHint
Qt.WindowStaysOnTopHint → Qt.WindowType.WindowStaysOnTopHint

Qt.Alignment:
Qt.AlignLeft → Qt.AlignmentFlag.AlignLeft
Qt.AlignRight → Qt.AlignmentFlag.AlignRight
Qt.AlignHCenter → Qt.AlignmentFlag.AlignHCenter
Qt.AlignVCenter → Qt.AlignmentFlag.AlignVCenter
Qt.AlignCenter → Qt.AlignmentFlag.AlignCenter
Qt.AlignTop → Qt.AlignmentFlag.AlignTop
Qt.AlignBottom → Qt.AlignmentFlag.AlignBottom

Qt.MouseButtons:
Qt.LeftButton → Qt.MouseButton.LeftButton
Qt.RightButton → Qt.MouseButton.RightButton
Qt.MiddleButton → Qt.MouseButton.MiddleButton

Qt.KeyboardModifiers:
Qt.ShiftModifier → Qt.KeyboardModifier.ShiftModifier
Qt.ControlModifier → Qt.KeyboardModifier.ControlModifier
Qt.AltModifier → Qt.KeyboardModifier.AltModifier
Qt.MetaModifier → Qt.KeyboardModifier.MetaModifier

Qt.Orientation:
Qt.Horizontal → Qt.Orientation.Horizontal
Qt.Vertical → Qt.Orientation.Vertical

Qt.ItemFlags:
Qt.ItemIsEnabled → Qt.ItemFlag.ItemIsEnabled
Qt.ItemIsSelectable → Qt.ItemFlag.ItemIsSelectable
Qt.ItemIsEditable → Qt.ItemFlag.ItemIsEditable
Qt.ItemIsDragEnabled → Qt.ItemFlag.ItemIsDragEnabled
Qt.ItemIsDropEnabled → Qt.ItemFlag.ItemIsDropEnabled

QAbstractItemView:
QAbstractItemView.SingleSelection → QAbstractItemView.SelectionMode.SingleSelection
QAbstractItemView.MultiSelection → QAbstractItemView.SelectionMode.MultiSelection
QAbstractItemView.ExtendedSelection → QAbstractItemView.SelectionMode.ExtendedSelection

Qt.CursorShape:
Qt.ArrowCursor → Qt.CursorShape.ArrowCursor
Qt.WaitCursor → Qt.CursorShape.WaitCursor
Qt.CrossCursor → Qt.CursorShape.CrossCursor
Qt.IBeamCursor → Qt.CursorShape.IBeamCursor

Qt.ScrollBarPolicy:
Qt.ScrollBarAlwaysOn → Qt.ScrollBarPolicy.ScrollBarAlwaysOn
Qt.ScrollBarAlwaysOff → Qt.ScrollBarPolicy.ScrollBarAlwaysOff
Qt.ScrollBarAsNeeded → Qt.ScrollBarPolicy.ScrollBarAsNeeded

Qt.FocusPolicy:
Qt.NoFocus → Qt.FocusPolicy.NoFocus
Qt.TabFocus → Qt.FocusPolicy.TabFocus
Qt.ClickFocus → Qt.FocusPolicy.ClickFocus
Qt.StrongFocus → Qt.FocusPolicy.StrongFocus

QDialog:
QDialog.Accepted → QDialog.DialogCode.Accepted
QDialog.Rejected → QDialog.DialogCode.Rejected

Qt5 → Qt6 (QImage formats)
QImage.Format_Invalid → QImage.Format.Format_Invalid
QImage.Format_Mono → QImage.Format.Format_Mono
QImage.Format_MonoLSB → QImage.Format.Format_MonoLSB
QImage.Format_Indexed8 → QImage.Format.Format_Indexed8
QImage.Format_RGB32 → QImage.Format.Format_RGB32
QImage.Format_ARGB32 → QImage.Format.Format_ARGB32
QImage.Format_ARGB32_Premultiplied → QImage.Format.Format_ARGB32_Premultiplied
QImage.Format_RGB888 → QImage.Format.Format_RGB888
QImage.Format_RGBX8888 → QImage.Format.Format_RGBX8888
QImage.Format_RGBA8888 → QImage.Format.Format_RGBA8888
QImage.Format_RGBA8888_Premultiplied → QImage.Format.Format_RGBA8888_Premultiplied
and more:

Qt5 → Qt6 (QRubberBand)
QRubberBand.Line → QRubberBand.Shape.Line
QRubberBand.Rectangle → QRubberBand.Shape.Rectangle

Qt5 → Qt6 (Mouse buttons)
Qt.LeftButton → Qt.MouseButton.LeftButton
Qt.RightButton → Qt.MouseButton.RightButton
Qt.MiddleButton → Qt.MouseButton.MiddleButton
Qt.BackButton → Qt.MouseButton.BackButton
Qt.ForwardButton → Qt.MouseButton.ForwardButton
Qt.TaskButton → Qt.MouseButton.TaskButton

Qt5 → Qt6 (Qt.AlignmentFlag)
Qt.AlignLeft → Qt.AlignmentFlag.AlignLeft
Qt.AlignRight → Qt.AlignmentFlag.AlignRight
Qt.AlignHCenter → Qt.AlignmentFlag.AlignHCenter
Qt.AlignVCenter → Qt.AlignmentFlag.AlignVCenter
Qt.AlignCenter → Qt.AlignmentFlag.AlignCenter
Qt.AlignTop → Qt.AlignmentFlag.AlignTop
Qt.AlignBottom → Qt.AlignmentFlag.AlignBottom
Qt.AlignJustify → Qt.AlignmentFlag.AlignJustify
Qt.AlignAbsolute → Qt.AlignmentFlag.AlignAbsolute
Qt.AlignLeading → Qt.AlignmentFlag.AlignLeading
Qt.AlignTrailing → Qt.AlignmentFlag.AlignTrailing
Qt.AlignHorizontal_Mask → Qt.AlignmentFlag.AlignHorizontal_Mask
Qt.AlignVertical_Mask → Qt.AlignmentFlag.AlignVertical_Mask

Qt5 → Qt6 (QFileDialog.Option)
QFileDialog.ShowDirsOnly → QFileDialog.Option.ShowDirsOnly
QFileDialog.DontResolveSymlinks → QFileDialog.Option.DontResolveSymlinks
QFileDialog.DontConfirmOverwrite → QFileDialog.Option.DontConfirmOverwrite
QFileDialog.DontUseSheet → QFileDialog.Option.DontUseSheet
QFileDialog.DontUseNativeDialog → QFileDialog.Option.DontUseNativeDialog
QFileDialog.ReadOnly → QFileDialog.Option.ReadOnly
QFileDialog.HideNameFilterDetails → QFileDialog.Option.HideNameFilterDetails
QFileDialog.DontUseCustomDirectoryIcons → QFileDialog.Option.DontUseCustomDirectoryIcons
QFileDialog.DontUseNativeMenuBar → QFileDialog.Option.DontUseNativeMenuBar

Qt5 → Qt6 (QChart enums)

QChart.ChartTypeCartesian → QChart.ChartType.ChartTypeCartesian
QChart.ChartTypePolar → QChart.ChartType.ChartTypePolar

QChart.NoAnimation → QChart.AnimationOption.NoAnimation
QChart.GridAxisAnimations → QChart.AnimationOption.GridAxisAnimations
QChart.SeriesAnimations → QChart.AnimationOption.SeriesAnimations
QChart.AllAnimations → QChart.AnimationOption.AllAnimations
QChart.NoLegend → QChart.LegendMarkerType.NoLegend
QChart.LegendMarkers → QChart.LegendMarkerType.LegendMarkers
QChart.ChartThemeLight → QChart.ChartTheme.ChartThemeLight
QChart.ChartThemeBlueCerulean → QChart.ChartTheme.ChartThemeBlueCerulean
QChart.ChartThemeDark → QChart.ChartTheme.ChartThemeDark
QChart.ChartThemeBrownSand → QChart.ChartTheme.ChartThemeBrownSand
QChart.ChartThemeBlueNcs → QChart.ChartTheme.ChartThemeBlueNcs
QChart.ChartThemeHighContrast → QChart.ChartTheme.ChartThemeHighContrast
QChart.ChartThemeBlueIcy → QChart.ChartTheme.ChartThemeBlueIcy
QChart.ChartThemeQt → QChart.ChartTheme.ChartThemeQt
"""
