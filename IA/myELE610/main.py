import sys
## QT imports
from PyQt6.QtGui import QAction, QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel, QStackedWidget, QVBoxLayout

# From my own
from menuBar import myMenuBar
from canvasWidget import Canvas
from histogramWidget import Histogram
from myImage import imageContainer

# CV
import cv2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELE610 App")
        self.resize(800,600)
        self.img = imageContainer(file_name='/Users/tordscheie/Kode/ELE610/ELE610/IA/myELE610/grayscaledemo.png')
        self.stack = QStackedWidget()
        self.canvas = Canvas()
        self.histogram = Histogram(self.img)
        self.stack.addWidget(self.canvas)
        self.stack.addWidget(self.histogram)

        self.setCentralWidget(self.stack)

        self.canvas.btn_hist.clicked.connect(lambda: (self.stack.setCurrentWidget(self.histogram), self.histogram.update_histogram(self.img)))
        self.histogram.btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.canvas))
      
        self.canvas.set_image(self.img.getPixmap()) 
        self.setup_ui()


    def setup_ui(self):
        myMenuBar(self)
       
        
    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName (
            self, 
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.img = imageContainer(file_name=file_name)
            self.canvas.set_image(self.img.getPixmap())

    
   

    def print_image_info(self):
        self.img.printImageInfo()

    def convert_to_grayscale(self):
        self.img.convertToGrayscale()
        self.canvas.set_image(self.img.getPixmap())

    def show_histogram(self):
        pass

    def reset(self):
        self.img.reset()
        self.canvas.set_image(self.img.getPixmap())

def startup():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    shutdown(app)

def shutdown(app):
    sys.exit(app.exec())


if __name__ =='__main__':
    startup()