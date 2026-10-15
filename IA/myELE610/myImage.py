import math

import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap


class imageContainer:
    def __init__(self, file_name="./pictures/demo.jpg"):
        self.filename = file_name
        self.cv2image = cv2.imread(file_name)

    def getPixmap(self, qimage: QImage):
        img = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2RGB)
        return QPixmap.fromImage(qimage)

    def getQimage(self):
        if len(self.cv2image.shape) == 2:
            qimage = QImage(
                self.cv2image.data.tobytes(),
                self.cv2image.shape[1],  # width
                self.cv2image.shape[0],  # height
                self.cv2image.strides[0],
                QImage.Format.Format_Grayscale8,
            )
        else:
            img = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2RGB)
            height, width, channels = img.shape
            bytes_per_line = channels * width
            qimage = QImage(
                img.data.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
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
        if len(self.cv2image.shape) == 3:
            self.cv2image = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)
        else:
            print("Image already converted to grayscale")

    def getHistogram(self):
        hist = cv2.calcHist([self.cv2image], [0], None, [256], [0, 256])
        return hist

    def convertToEdges(self):
        if self.cv2image is None:
            raise ValueError("No image")
        # Blur to reduce background noice
        blurred = cv2.GaussianBlur(self.cv2image, (3, 3), 0)

        # calculates gradients cv2.sobel(bilde, ddepth, dx, dy, kernel size
        # The ddepth needs to be a CV_64F because a change from black to white hives a negaive value wich uint8 cant do
        sobel_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, 3)  # type: ignore
        sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, 3)  # type: ignore

        # convert back to uint8
        abs_sobel_x = cv2.convertScaleAbs(sobel_x)
        abs_sobel_y = cv2.convertScaleAbs(sobel_y)

        self.cv2image = cv2.addWeighted(abs_sobel_x, 0.5, abs_sobel_y, 0.5, 0)

    def convertToBinary(self):
        if self.cv2image is None:
            raise ValueError("No image")
        ret, thresh = cv2.threshold(self.cv2image, 120, 255, cv2.THRESH_BINARY)

        self.cv2image = thresh

    def showHoughLines(self):

        if self.cv2image is None:
            raise ValueError("Cannot read the image")

        if len(self.cv2image.shape) == 3:
            self.cv2image = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(self.cv2image, (5, 5), 0)
        edges = cv2.Canny(blurred, 100, 200)

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 150, None, 0, 0)
        cdst = cv2.cvtColor(self.cv2image, cv2.COLOR_GRAY2BGR)
        # draw lines
        if lines is not None:
            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho

                pt1 = int(x0 + 3000 * (-b)), int(y0 + 3000 * (a))
                pt2 = int(x0 - 3000 * (-b)), int(y0 - 3000 * (a))

                cv2.line(cdst, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)
            self.cv2image = cdst

    def reset(self):
        self.cv2image = cv2.imread(self.filename)


def BGR2RGB(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def RGB2GRAY(image: np.ndarray):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


if __name__ == "__main__":
    pass

