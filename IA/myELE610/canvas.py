from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None

    def set_image(self, pixmap):
        self.pixmap = pixmap
        self.update()
    
    def paintEvent(self, event):
        if not self.pixmap:
            return
        
        scaled = self.pixmap.scaled(
            self.size(),
            Qt. AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height()- scaled.height()) // 2

        painter = QPainter(self)
        painter.drawPixmap(x, y, scaled)

if __name__ == '__main__':
    pass