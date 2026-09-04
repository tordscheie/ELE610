from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import pyqtgraph as pg
from myImage import imageContainer
import cv2


class Histogram(QWidget):
    def __init__(self, img : imageContainer ):
        super().__init__()
        self.btn_back = QPushButton("Back ( CNTRL+Z )")
        self.hist = img.getHistogram()

        self.fig, self.ax = plt.subplots(figsize=(10,10))
        self.ax.plot(self.hist,color='red')
        self.ax.set_title('Histogram')
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('Number of Pixels')

        self.canvas = FigureCanvasQTAgg(self.fig)
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.canvas)
        layout.addWidget(self.btn_back)

    def update_histogram(self, img : imageContainer):
        self.ax.clear()
        self.hist = img.getHistogram()
        self.ax.plot(self.hist, color='red')
        self.canvas.draw()

    