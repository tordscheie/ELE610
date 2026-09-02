import sys
## QT imports
from PyQt6.QtGui import QAction, QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel

# From my own
from menuBar import myMenuBar
from canvas import Canvas
from myImage import imageContainer

# CV
import cv2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELE610 App")
        self.resize(800,600)
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.img = None
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