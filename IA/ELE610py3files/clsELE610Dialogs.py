#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/clsELE610Dialogs.py 
#
#  The classes:  EdgeDialog, FilterDialog, ResizeDialog, ThresholdDialog
#  For test:     MainWindow 
#
# Karl Skretting, UiS, February 2019, June 2022, January 2024
#   March 2026, collect several dialogs in one file and one test
#   CoPilot helped to make methods more 'Phytonic' and according to Qt good practice

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3>activate py12
#   (py12) C:\..\py3>python clsELE610Dialogs.py
#   .../ELE610/py3$ python3 clsELE610Dialogs.py
# Example on how to use file in a python program  
#   from clsELE610Dialogs import EdgeDialog, FilterDialog

_fileName = "clsELE610Dialogs.py"
_author = "Karl Skretting, UiS" 
_version = "2026.03.19"      # "yyyy.mm.dd"

# common:
import sys 
import numpy as np

# Qt, https://doc.qt.io/qt-6/classes.html
from mySystem import QT_BINDING, qt5Exist, qt6Exist 
if QT_BINDING == "None":
	print("Importing Qt failed.")
	raise ImportError(f"{_fileName}: Requires PyQt6, PySide6 or PyQt5")
else: # ok
	from mySystem import (QT_VERSION_STR, Qt, QAction, QFont, pyqtSignal, pyqtSlot, 
	  QApplication, QButtonGroup, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame, 
	  QHBoxLayout, QLabel, QMainWindow, QPushButton, QRadioButton, QSlider, QSpinBox, QTimer, 
	  QDialogButtonBox_Cancel, QDialogButtonBox_Ok, Qt_Horizontal, QValidator_Acceptable)


# by KS
from funMyTools import printArray


# Helper: Create a row of radio buttons with a QButtonGroup
def makeRadioGroup(cls, items, default):
	row = QHBoxLayout()
	group = QButtonGroup(cls)

	for value, text in items:
		rb = QRadioButton(text)
		group.addButton(rb, value)
		row.addWidget(rb)
		if value == default:
			rb.setChecked(True)

	row.addStretch()
	return group, row


class EdgeDialog(QDialog):
	"""A modal dialog widget for giving edge values.
	Emits edgeValuesChanged(int, int) when values change and dialog is not finished.
	"""
	edgeValuesChanged = pyqtSignal(int, int) 

	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle("Edge dialog for making edge image")
		self.setGeometry(parent.x()+20, parent.y()+120, 320, 130)

		# --- Create radio buttons ---
		self.qbgK, kRow = makeRadioGroup( self, 
			[(3, "k=3"), (5, "k=5"), (7, "k=7"), (9, "k=9")], default=3 )

		self.qbgS, sRow = makeRadioGroup( self, 
			[(1, "none"), (3, "3x3"), (5, "5x5"), (7, "7x7"), (9, "9x9")], default=5 )

		# --- OK / Cancel buttons ---
		buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		# --- Layout ---
		layout = QFormLayout()
		layout.addRow(QLabel("Select k-size to use in Sobel filters."), kRow)
		layout.addRow(QLabel("Select size of separable smoothing filter."), sRow)
		layout.addRow(buttons)
		self.setLayout(layout)

		# --- Connect signals ---
		self.qbgK.buttonClicked.connect(self._emitValues)
		self.qbgS.buttonClicked.connect(self._emitValues)


	def _emitValues(self):
		valK = self.qbgK.checkedId()
		valS = self.qbgS.checkedId()
		self.edgeValuesChanged.emit(valK, valS)


	def getValues(self):
		self.exec()
		return (self.qbgK.checkedId(), self.qbgS.checkedId())
	#end class EdgeDialog


class FilterDialog(QDialog):
	"""A modal dialog widget for giving filter values.
	Emits filterValuesChanged(object, int) when values change and dialog is not finished.
	Object is usually a 2D numpy array with values for the filter.
	"""
	filterValuesChanged = pyqtSignal(object, int)

	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle("Filter dialog")
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 200)

		font = QFont("Arial", 10)
		self.vTab = [1.0, 0.75, 0.5, 0.25, 0.0, -0.25, -0.5, -0.75, -1.0]

		# --- Filter size spinbox ---
		self.qsbFiltSize = QSpinBox()
		self.qsbFiltSize.setFont(font)
		self.qsbFiltSize.setRange(1, 25)
		self.qsbFiltSize.setValue(11)
		self.qsbFiltSize.setSingleStep(2)
		self.qsbFiltSize.setMinimumWidth(60)
		self.qsbFiltSize.valueChanged.connect(self._emitValues)

		# --- Four corner combo boxes ---
		self.qcbUpperLeftValue  = self._makeCombo("Upper Left",  font, default=0)
		self.qcbUpperRightValue = self._makeCombo("Upper Right", font, default=0)
		self.qcbLowerLeftValue  = self._makeCombo("Lower Left",  font, default=len(self.vTab)-1)
		self.qcbLowerRightValue = self._makeCombo("Lower Right", font, default=len(self.vTab)-1)

		# Connect combo boxes to live update
		for cb in (self.qcbUpperLeftValue, self.qcbUpperRightValue, self.qcbLowerLeftValue, self.qcbLowerRightValue):
			cb.currentIndexChanged.connect(self._emitValues)

		# --- Smoothing filter radio buttons ---
		self.qbgS, sRow = makeRadioGroup( self,
			[(1, "none"), (3, "3x3"), (5, "5x5"), (7, "7x7"), (9, "9x9")],
			default=5
		)
		self.qbgS.buttonClicked.connect(self._emitValues)

		# --- OK / Cancel buttons ---
		buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		# --- Layout ---
		layout = QFormLayout()
		layout.addRow(QLabel("A filter options dialog, (k=1 ignores first filter)"))

		# Filter size row
		sizeRow = QHBoxLayout()
		sizeRow.addWidget(QLabel("Size of first filter k × k, k ="))
		sizeRow.addWidget(self.qsbFiltSize)
		layout.addRow(sizeRow)

		# Filter value rows
		layout.addRow(QLabel("Values for blocks in first filter"))

		upperRow = QHBoxLayout()
		upperRow.addStretch()
		upperRow.addWidget(self.qcbUpperLeftValue)
		upperRow.addWidget(self.qcbUpperRightValue)
		upperRow.addStretch()
		layout.addRow(upperRow)

		lowerRow = QHBoxLayout()
		lowerRow.addStretch()
		lowerRow.addWidget(self.qcbLowerLeftValue)
		lowerRow.addWidget(self.qcbLowerRightValue)
		lowerRow.addStretch()
		layout.addRow(lowerRow)

		# Smoothing filter row
		layout.addRow(QLabel("Size of a second separable smoothing filter"))
		layout.addRow(sRow)

		# Buttons row
		btnRow = QHBoxLayout()
		btnRow.addStretch()
		btnRow.addWidget(buttons)
		layout.addRow(btnRow)

		self.setLayout(layout)


	# Helper: Create a combo box for filter corner values
	def _makeCombo(self, label, font, default=0):
		cb = QComboBox()
		cb.setFont(font)
		for v in self.vTab:
			cb.addItem(f"{label} = {v:4.2f}")
		cb.setCurrentIndex(default)
		cb.setMinimumWidth(60)
		return cb


	def _computeValues(self):
		v = self.qsbFiltSize.value()

		if v < 3:
			H = np.array([])
		else:
			H = np.zeros((v, v))
			mid = v // 2

			H[:mid, :mid] = self.vTab[self.qcbUpperLeftValue.currentIndex()]
			H[:mid, mid+1:] = self.vTab[self.qcbUpperRightValue.currentIndex()]
			H[mid+1:, :mid] = self.vTab[self.qcbLowerLeftValue.currentIndex()]
			H[mid+1:, mid+1:] = self.vTab[self.qcbLowerRightValue.currentIndex()]

		valS = self.qbgS.checkedId()
		return H, valS


	def _emitValues(self):
		H, valS = self._computeValues()
		self.filterValuesChanged.emit(H, valS)


	def getValues(self):
		self.exec()   # modal dialog
		return self._computeValues()
	#end class FilterDialog


class ResizeDialog(QDialog):
	"""A modal dialog widget for giving new resize values.
	Emits resizeValuesChanged(int, int) when values change and dialog is not finished.
	"""
	resizeValuesChanged = pyqtSignal(int, int)

	def __init__(self, parent, curWidth=800, curHeight=600):
		super().__init__(parent)

		self.wIm, self.hIm = curWidth, curHeight

		self.setWindowTitle("Resize dialog for resizing image of size")
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 250)

		# --- Slider for percent ---
		self.slider = QSlider(Qt_Horizontal)
		self.slider.setMinimum(10)
		self.slider.setMaximum(400)
		self.slider.setSliderPosition(100)
		self.slider.sliderMoved.connect(self._sliderMoved)

		# --- Percent spinbox ---
		self.qsbPercent = QSpinBox()
		self.qsbPercent.setRange(10, 400)
		self.qsbPercent.setValue(100)
		self.qsbPercent.valueChanged.connect(self._percentChanged)

		# --- Width spinbox ---
		self.qsbWidth = QSpinBox()
		self.qsbWidth.setRange(self.wIm // 10, self.wIm * 4)
		self.qsbWidth.setValue(self.wIm)
		self.qsbWidth.valueChanged.connect(self._emitValues)

		# --- Height spinbox ---
		self.qsbHeight = QSpinBox()
		self.qsbHeight.setRange(self.hIm // 10, self.hIm * 4)
		self.qsbHeight.setValue(self.hIm)
		self.qsbHeight.valueChanged.connect(self._emitValues)

		# --- OK / Cancel buttons ---
		buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		# --- Layout ---
		layout = QFormLayout()
		layout.addRow(QLabel("Resize image and keep aspect ratio."))
		layout.addRow(QLabel(f"Current size (w x h): ({self.wIm} x {self.hIm})"))
		layout.addRow(self.slider)
		layout.addRow("Scale in percent:", self.qsbPercent)
		layout.addRow(QLabel("The values below are returned; changing these does not keep aspect ratio."))
		layout.addRow("New width:", self.qsbWidth)
		layout.addRow("New height:", self.qsbHeight)

		btnRow = QHBoxLayout()
		btnRow.addStretch()
		btnRow.addWidget(buttons)
		layout.addRow(btnRow)

		self.setLayout(layout)

	def _sliderMoved(self, val: int):
		# Slider drives percent
		self.qsbPercent.setValue(val)
		# Percent spinbox handler will update width/height and emit values


	def _percentChanged(self, val: int):
		# Update slider without triggering sliderMoved
		self.slider.blockSignals(True)
		self.slider.setSliderPosition(val)
		self.slider.blockSignals(False)

		# Update width and height without triggering their signals
		self.qsbWidth.blockSignals(True)
		self.qsbHeight.blockSignals(True)

		self.qsbWidth.setValue((self.wIm * val) // 100)
		self.qsbHeight.setValue((self.hIm * val) // 100)

		self.qsbWidth.blockSignals(False)
		self.qsbHeight.blockSignals(False)
		self._emitValues()


	def _emitValues(self):
		self.resizeValuesChanged.emit(self.qsbWidth.value(), self.qsbHeight.value())

	# -------------------------------------------------------------
	# Return final values after OK/Cancel
	def getValues(self):
		self.exec()
		return self.qsbWidth.value(), self.qsbHeight.value()
	#end class ResizeDialog


# Etter en god del flikking med QSlider og QSpinBox sine signaler kom jeg til slutt
# fram til noe som fungerer. CoPilot hjalp etter beste evne, men kom ofte med 'dårlige' råd.
# Gammal klasse er fortsatt i clsThresholdDialog.py (som en ikke bør/trenger bruke mer)
class ThresholdDialog(QDialog): 
	"""A modal dialog widget for giving threshold values (image from grayscale to binary)
	Emits thresholdValueChanged(int) when value is changed, also for slider moved!
	The value is in range 0 to 255, i.e here it is assumed that image is uint8.
	For the spinBox a 'delayed apply' strategy is used to emit signal when value is edited.
	For the slider the signal is emitted when moved or changed 
	"""
	thresholdValueChanged = pyqtSignal(int)

	def __init__(self, parent, verbose=0):
		super().__init__(parent)
		self.title = 'Thresholding dialog for making binary image'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 150)
		self.verbose = verbose  # 'undocumented' argumet
		
		# contents
		self.spinBoxThr = QSpinBox()
		self.spinBoxThr.setRange(0, 255)
		self.spinBoxThr.setValue(127)
		self.spinBoxThr.setKeyboardTracking(False)
		self.spinEditTimer = QTimer(self)
		self.spinEditTimer.setSingleShot(True)
		self.spinEditTimer.setInterval(500)  # 0.5 seconds
		# Connect to the internal line edit
		lineEd = self.spinBoxThr.lineEdit()
		lineEd.textEdited.connect(self._spinBoxTextEdited)
		self.spinBoxThr.valueChanged.connect(self._spinBoxChanged)  
		self.spinEditTimer.timeout.connect(self._spinBoxCommit)
		
		self.sliderThr = QSlider(Qt_Horizontal) 
		self.sliderThr.setMinimum(0)
		self.sliderThr.setMaximum(255)
		self.sliderThr.setTracking(False)
		self.sliderThr.setSliderPosition(127)
		
		self.sliderThr.sliderMoved.connect(self._sliderUpdate)
		self.sliderThr.valueChanged.connect(self._sliderUpdate)

		# --- OK / Cancel buttons ---
		buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		# --- Layout ---
		layout = QFormLayout()
		layout.addRow(QLabel("A value of 0 may indicate to use Otsu method to find threshold value"))
		layout.addRow('Threshold value: ', self.spinBoxThr)
		layout.addRow(self.sliderThr)

		btnRow = QHBoxLayout()
		btnRow.addStretch()
		btnRow.addWidget(buttons)
		layout.addRow(btnRow)

		self.setLayout(layout)


	def _spinBoxTextEdited(self):
		# Restart the timer on every keystroke
		self.spinEditTimer.start()

	# slot for self.spinBoxThr.valueChanged
	def _spinBoxChanged(self, val: int):
		if self.verbose: 
			print(f"_spinBoxChanged: {self.spinBoxThr.lineEdit().text()=}, {self.spinBoxThr.value()=}")
		self.sliderThr.blockSignals(True)
		self.sliderThr.setSliderPosition(val)
		self.sliderThr.blockSignals(False)
		self.spinEditTimer.start()

	# slot for QTimer (for editing text in spinBox)
	def _spinBoxCommit(self):
		# Note: self.spinBoxThr.value() is not updated here, text() is 
		if self.verbose: 
			print(f"_spinBoxCommit: {self.spinBoxThr.lineEdit().text()=}, {self.spinBoxThr.value()=}")
		# val = self.spinBoxThr.value() # is the old value   
		# val = int(self.spinBoxThr.lineEdit().text())  # is the new one, but it should be validated
		text = self.spinBoxThr.lineEdit().text()
		state = self.spinBoxThr.lineEdit().validator().validate(text, 0)[0]
		if state != QValidator_Acceptable:
			return
		val = int(text)
		# Sync slider
		self.sliderThr.blockSignals(True)
		self.sliderThr.setValue(val)
		self.sliderThr.blockSignals(False)
		self.spinBoxThr.blockSignals(True)
		self.spinBoxThr.setValue(val)   
		self.spinBoxThr.blockSignals(False)
		self.thresholdValueChanged.emit(val)

#	def _sliderMoved(self, val: int):
#	def _sliderChanged(self, val: int):
	def _sliderUpdate(self, val: int):
		# Keep spinbox synced, and emit
		self.spinBoxThr.blockSignals(True)
		self.spinBoxThr.setValue(val)
		self.spinBoxThr.blockSignals(False)
		self.thresholdValueChanged.emit(self.spinBoxThr.value()) 

	# Return final value after OK/Cancel
	def getValue(self):
		self.exec()
		# may check if the two widgets in dialog are (still) syncronized
		if self.verbose: 
			print(f"ThresholdDialog.getValue(): returns {self.sliderThr.value()=} == {self.spinBoxThr.value()=}")
		return self.spinBoxThr.value()
	#end class ThresholdDialog


class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of ELE610 dialogs")
		self.setGeometry(150, 50, 800, 600)  # initial window position and size
		#
		qaEdgeDialog = QAction('showEdgeDialog', self)
		qaEdgeDialog.setShortcut('Ctrl+E')
		qaEdgeDialog.setToolTip('Show the edge dialog')
		qaEdgeDialog.triggered.connect(self.showEdgeDialog)
		#
		qaFilterDialog = QAction('showFilterDialog', self)
		qaFilterDialog.setShortcut('Ctrl+F')
		qaFilterDialog.setToolTip('Show the filter dialog')
		qaFilterDialog.triggered.connect(self.showFilterDialog)
		#
		qaResizeDialog = QAction('showResizeDialog', self)
		qaResizeDialog.setShortcut('Ctrl+R')
		qaResizeDialog.setToolTip('Show the resize dialog')
		qaResizeDialog.triggered.connect(self.showResizeDialog)
		#
		qaThresholdDialog = QAction('showThresholdDialog', self)
		qaThresholdDialog.setShortcut('Ctrl+T')
		qaThresholdDialog.setToolTip('Show the threshold dialog')
		qaThresholdDialog.triggered.connect(self.showThresholdDialog)
		#
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&Dialogs')
		fileMenu.addAction(qaEdgeDialog)
		fileMenu.addAction(qaFilterDialog)
		fileMenu.addAction(qaResizeDialog)
		fileMenu.addAction(qaThresholdDialog)
		fileMenu.setToolTipsVisible(True)


	def showEdgeDialog(self): 
		d = EdgeDialog(parent=self)   # create object (but does not run it)
		d.edgeValuesChanged.connect(self.showEdgeValues)
		(valK,valS) = d.getValues()   # display dialog and return values
		print(f"MainWindow.showEdgeDialog(): Returned {valK=},  {valS=}, and {d.result()=}")
		d.edgeValuesChanged.disconnect(self.showEdgeValues)

	def showEdgeValues(self, valK, valS):
		print( f"MainWindow.showEdgeValues(): Signal edgeValuesChanged emitted, {valK=},  {valS=}" )

	def showFilterDialog(self):
		d = FilterDialog(parent=self)   # create dialog object
		d.filterValuesChanged.connect(self.showFilterValues)
		(H, valS) = d.getValues()       # display dialog and return values
		print(f"MainWindow.showFilterDialog(): Returned {H.shape=}, {valS=}, and {d.result()=}")
		d.filterValuesChanged.disconnect(self.showFilterValues)

	def showFilterValues(self, H, valS):
		print(f"MainWindow.showFilterValues(): Signal filterValuesChanged emitted, H.shape={H.shape}, {valS=}")
		if H.size:
			printArray(H,"Filter coefficients",format_num="%6.2f ", maxN=10)

	def showResizeDialog(self): 
		d = ResizeDialog(parent=self, curWidth=500, curHeight=300)   # create object (but does not run it)
		d.resizeValuesChanged.connect(self.showResizeValues)
		(w,h) = d.getValues()   # display dialog and return values
		print(f"MainWindow.showResizeDialog(): Returned {w=},  {h=}, and {d.result()=}")
		d.resizeValuesChanged.disconnect(self.showResizeValues)
		return

	def showResizeValues(self, w, h):
		print(f"MainWindow.showResizeValues(): Signal resizeValuesChanged emitted,  ({w=}, {h=})")

	def showThresholdDialog(self): 
		d = ThresholdDialog(parent=self, verbose=1)   # create object (but does not run it)
		d.thresholdValueChanged.connect(self.showThresholdValue)
		thr = d.getValue()   # display dialog and return values
		print(f"MainWindow.showThresholdDialog(): Returned {thr=} and {d.result()=}")
		d.thresholdValueChanged.disconnect(self.showThresholdValue)
		return

	def showThresholdValue(self, thr):
		print(f"MainWindow.showThresholdValue(): Signal thresholdValueChanged emitted, {thr=}")
	#end class MainWindow

if __name__ == '__main__':
	print( f"clsELE610Dialogs.py, Using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	if qt6Exist:
		sys.exit(mainApp.exec())
	else:
		sys.exit(mainApp.exec_())

