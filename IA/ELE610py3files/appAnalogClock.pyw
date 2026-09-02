#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appAnalogClock.pyw	
# from https://doc.qt.io/qt-5.10/qtwidgets-widgets-analogclock-example.html 
# Karl Skretting, UiS, March 2018	(added seconds too)
# KS, August 2024  made file work for both Qt6 and Qt5
# KS, April 2026   use mySystem to import Qt (from different installations)

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> pythonw appAnalogClock.pyw   # ignore print
# (py38) C:\..\py3> python appAnalogClock.pyw    # print

import sys 

# Qt
from mySystem import QT_BINDING, qt5Exist as PyQt5isUsed, qt6Exist as PyQt6isUsed
if QT_BINDING == "None":
	print("Importing Qt failed.")
	raise ImportError(f"{_fileName}: Requires PyQt6, PySide6 or PyQt5")
else: # ok
	from mySystem import (Qt, QApplication, QColor, QPainter, QPen, QPolygon, QPoint, 
	  QTimer, QTime, QWidget, QPainter_Antialiasing, Qt_NoPen)

class AnalogClock(QWidget):
 
	def __init__(self, parent = None):
		super().__init__(parent)  # or
		# super(AnalogClock, self).__init__(parent)   # what is the difference, if any?
		# see: https://python-course.eu/python3_inheritance.php
		self.setWindowTitle('Analog Clock')
		self.setGeometry(500, 100, 400, 400)
		timer = QTimer(parent = self)
		timer.timeout.connect(self.update)
		timer.start(1000)  # [ms]
		#
		self.hourHand = QPolygon( [QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)] )
		self.minuteHand = QPolygon( [ QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70) ] )
		self.secondHand = QPolygon( [ QPoint(5, 6), QPoint(-5, 6), QPoint(0, -80) ] )
		self.hourColor = QColor(127, 0, 127)
		self.minuteColor = QColor(0, 127, 127, 191)   #  75% opaque
		self.secondColor = QColor(180, 180, 0, 132)   #  50% opaque
 
	def paintEvent(self, qpe):
		# implement the QWidget protected function, done when repaint() or update() is invoked
		# or whenever needed. Here timer invoke update() every 1000 ms.
		# the QPaintEvent qpe argument is ignored here
		side = min(self.width(), self.height())
		time = QTime.currentTime()
		pen = QPen()
		
		painter = QPainter(self)
		painter.translate(self.width()/2, self.height()/2)
		painter.scale(side/200.0, side/200.0)
		painter.setRenderHint(QPainter_Antialiasing)
		pen.setStyle(Qt_NoPen)   # invisible pen used for the hands
		#
		# hour hand with brush only
		painter.setPen(pen)
		painter.setBrush(self.hourColor)
		painter.save()
		painter.rotate(30.0*((time.hour()+time.minute()/60.0)))
		painter.drawConvexPolygon(self.hourHand)
		painter.restore()
		#
		# hour marks
		painter.setPen(self.hourColor)
		for i in range(12):
			painter.drawLine(88, 0, 96, 0)
			painter.rotate(30.0)
		#
		# minute hand with brush only
		painter.setPen(pen)
		painter.setBrush(self.minuteColor)
		painter.save()
		painter.rotate(6.0*(time.minute() + time.second()/60.0))
		painter.drawConvexPolygon(self.minuteHand)
		painter.restore()
		#
		# minute marks
		painter.setPen(self.minuteColor)
		for j in range(60):
			if ((j % 5) != 0):
				painter.drawLine(92, 0, 96, 0)
			painter.rotate(6.0)
		#
		# second hand with brush only
		painter.setPen(pen)
		painter.setBrush(self.secondColor)
		painter.save()
		painter.rotate(6.0*time.second())
		painter.drawConvexPolygon(self.secondHand)
		painter.restore()

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	clock = AnalogClock()
	clock.show()
	sys.exit(app.exec())
	
#
# CoPilot can make Python program from C-code example:
# Prompt:
# Can you convert the example in https://doc.qt.io/qt-5.10/qtwidgets-widgets-analogclock-example.html into Python code?
# Can you also include a Second hand? 
# Result:
"""
	import sys
	from PyQt5.QtCore import Qt, QTimer, QTime, QPoint
	from PyQt5.QtGui import QColor, QPainter
	from PyQt5.QtWidgets import QWidget, QApplication


	class AnalogClock(QWidget):
		def __init__(self, parent=None):
			super().__init__(parent)

			timer = QTimer(self)
			timer.timeout.connect(self.update)
			timer.start(1000)  # update every second

			self.setWindowTitle("Analog Clock")
			self.resize(200, 200)

			# Hour and minute hands (same as before)
			self.hourHand = [
				QPoint(7, 8),
				QPoint(-7, 8),
				QPoint(0, -40)
			]

			self.minuteHand = [
				QPoint(7, 8),
				QPoint(-7, 8),
				QPoint(0, -70)
			]

			# NEW: second hand (thin, long)
			self.secondHand = [
				QPoint(2, 8),
				QPoint(-2, 8),
				QPoint(0, -90)
			]

			self.hourColor = QColor(127, 0, 127)
			self.minuteColor = QColor(0, 127, 127, 191)
			self.secondColor = QColor(200, 0, 0)  # red

		def paintEvent(self, event):
			side = min(self.width(), self.height())
			time = QTime.currentTime()

			painter = QPainter(self)
			painter.setRenderHint(QPainter.Antialiasing)

			painter.translate(self.width() / 2, self.height() / 2)
			painter.scale(side / 200.0, side / 200.0)

			# --- Hour hand ---
			painter.setPen(Qt.NoPen)
			painter.setBrush(self.hourColor)

			painter.save()
			painter.rotate(30.0 * (time.hour() + time.minute() / 60.0))
			painter.drawConvexPolygon(*self.hourHand)
			painter.restore()

			painter.setPen(self.hourColor)
			for i in range(12):
				painter.drawLine(88, 0, 96, 0)
				painter.rotate(30.0)

			# --- Minute hand ---
			painter.setPen(Qt.NoPen)
			painter.setBrush(self.minuteColor)

			painter.save()
			painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
			painter.drawConvexPolygon(*self.minuteHand)
			painter.restore()

			painter.setPen(self.minuteColor)
			for j in range(60):
				if j % 5 != 0:
					painter.drawLine(92, 0, 96, 0)
				painter.rotate(6.0)

			# --- Second hand (NEW) ---
			painter.setPen(Qt.NoPen)
			painter.setBrush(self.secondColor)

			painter.save()
			painter.rotate(6.0 * time.second())
			painter.drawConvexPolygon(*self.secondHand)
			painter.restore()


	if __name__ == "__main__":
		app = QApplication(sys.argv)
		clock = AnalogClock()
		clock.show()
		sys.exit(app.exec_())
"""