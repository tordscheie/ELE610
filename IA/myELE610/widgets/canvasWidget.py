from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import Qt
from .imageWidget import Image 

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.btn_hist = QPushButton("Hist ( CNTRL+H )")
        self.image = Image()

        layout = QVBoxLayout(self)
        layout.addWidget(self.image)
        layout.addWidget(self.btn_hist)

    def update_image(self, pixmap):
        self.image.set_image(pixmap)
         

        

if __name__ == '__main__':
    pass