from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

class imageContainer:
    def __init__(self, file_name):
        self.cv2image = cv2.imread(file_name)
        self.rgb = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2RGB)
        self.gray = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)
        self.qimage = None
        self.pixmap = None

        self.pixmapCreate()
        self.qimageCreate()
      
    def pixmapCreate(self):
        qimage = None
        if len(self.cv2image) == 2:
            qimage = QImage(
            self.cv2image.data,
            self.cv2image.shape[1],  # width
            self.cv2image.shape[0],  # height
            self.cv2image.strides[0],
            QImage.Format.Format_Grayscale8
        ) 
        else:
            height, width, channels = self.cv2image.shape
            bytes_per_line = channels*width
            qimage = QImage(
                self.cv2image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
        self.pixmap = QPixmap.fromImage(qimage)

    def qimageCreate(self):
        qimage = None
        if len(self.cv2image) == 2:
            qimage = QImage(
            self.cv2image.data,
            self.cv2image.shape[1],  # width
            self.cv2image.shape[0],  # height
            self.cv2image.strides[0],
            QImage.Format.Format_Grayscale8
        ) 
        else:
            height, width, channels = self.cv2image.shape
            bytes_per_line = channels*width
            qimage = QImage(
                self.cv2image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
        self.qimage = qimage
    def printImageInfo(self):
        """Print some general (debug) information for the program and the image.
        Mainly for debug purposes.
        """
        img = self.qimage
        # Size
        print("Width:", img.width())
        print("Height:", img.height())
        # Image rerpresentation
        print(img.format())

    def setGrayImage(self):
        qimage = None
        qimage = QImage(
            self.gray.data,
            self.gray.shape[1],  # width
            self.gray.shape[0],  # height
            self.gray.strides[0],
            QImage.Format.Format_Grayscale8
        ) 
        self.pixmap = QPixmap.fromImage(qimage)
        self.qimage = qimage
    
    def setNormal(self):
        self.qimageCreate()
        self.pixmapCreate()






def BGR2RGB(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def RGB2GRAY(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


if __name__ == '__main__':
    pass