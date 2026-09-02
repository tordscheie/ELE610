from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg
from myImage import imageContainer
import cv2


class Histogram(QWidget):
    def __init__(self, img : imageContainer ):
        super().__init__()
        self.btn_back = QPushButton("Back")
        self.img = img
        self.hist = img.getHistogram()
        print(self.hist)
        layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget()
        layout.addStretch()
        layout.addWidget(self.plot)
        layout.addWidget(self.btn_back)
        self.plot.plot(self.hist)

    def update_histogram(self, img : imageContainer):
        self.hist = img.getHistogram()
        self.plot.clear()
        print(self.hist)
        self.plot.plot(self.hist)

    