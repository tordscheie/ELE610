from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

class imageContainer:
    def __init__(self, file_name='./pictures/demo.jpg'):
        self.filename = file_name
        self.cv2image = cv2.imread(file_name)
      
    def getPixmap(self, qimage:QImage):
        img = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2RGB)
        return QPixmap.fromImage(qimage)

    def getQimage(self):
        if len(self.cv2image.shape) == 2:
            qimage = QImage(
            self.cv2image.data.tobytes(),
            self.cv2image.shape[1],  # width
            self.cv2image.shape[0],  # height
            self.cv2image.strides[0],
            QImage.Format.Format_Grayscale8
        ) 
        else:
            img = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2RGB)
            height, width, channels = img.shape
            bytes_per_line = channels*width
            qimage = QImage(
                img.data.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
        return qimage
    
    def printImageInfo(self):
        """Print some general (debug) information for the program and the image.
        Mainly for debug purposes.
        """
        img = self.getQimage()
        # Size
        print("Width:", img.width())
        print("Height:", img.height())
        # Image rerpresentation
        print(img.format())

    def convertToGrayscale(self):
        self.cv2image = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)
    
    def getHistogram(self):
        hist = cv2.calcHist([self.cv2image], [0], None, [256], [0,256])
        return hist
    
    def reset(self):
        self.cv2image = cv2.imread(self.filename)





def BGR2RGB(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def RGB2GRAY(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


if __name__ == '__main__':
    pass