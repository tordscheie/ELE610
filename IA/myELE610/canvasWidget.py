from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.btn_hist = QPushButton("Histogram")
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.btn_hist)


    def set_image(self, pixmap):
        self.pixmap = pixmap
        self.update()
    
    def paintEvent(self, event):
        if not self.pixmap:
            return
        
        scaled = self.pixmap.scaled(
            self.width(),
            self.height() - 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2

        painter = QPainter(self)
        painter.drawPixmap(x, y, scaled)

if __name__ == '__main__':
    pass