import sys
from time import sleep

# CV
import cv2
from PyQt6.QtCore import Qt

## QT imports
from PyQt6.QtGui import QAction, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
)
from pyueye import ueye

from myImage import imageContainer

# From my own
from pyueye_example_camera import Camera
from pyueye_example_utils import uEyeException
from video import CameraWorker
from widgets import Canvas, Histogram, Image, MenuBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELE610 App")
        self.resize(800, 600)
        self.videoworker = None

        MenuBar(self)
        # INIT Image
        self.img = imageContainer()
        self.camOn = False
        self.cam = Camera()
        self.canvas = Canvas()

        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))
        self.histogram = Histogram(self.img)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.canvas)
        self.stack.addWidget(self.histogram)
        self.setCentralWidget(self.stack)

        self.canvas.btn_hist.clicked.connect(
            lambda: (
                self.stack.setCurrentWidget(self.histogram),
                self.histogram.update_histogram(self.img),
            )
        )
        self.canvas.btn_hist.setShortcut("Meta+H")

        self.histogram.btn_back.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.canvas)
        )
        self.histogram.btn_back.setShortcut("Meta+Z")

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.img = imageContainer(file_name=file_name)
            self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def print_image_info(self):
        self.img.printImageInfo()

    def convert_to_grayscale(self):
        self.img.convertToGrayscale()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def convert_to_edges(self):
        self.img.convertToEdges()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def convert_to_binary(self):
        self.img.convertToBinary()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def show_hough_lines(self):
        self.img.showHoughLines()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def open_camera(self):
        try:
            self.camOn = True
            print(f"cameraOn() Camera started ok")
        except uEyeException as e:
            print(f"cameraOn() Caught camera error: {e}")
            print(
                "  Typically gives error 212 when camera is not connected (not present)"
            )
            self.camOn = False
        #

    def print_camera_info(self):
        self.cam.printInfo()

    def take_picture(self):
        img = self.cam.takePicture()
        for i in range(25):
            img = self.cam.takePicture()
        self.img.cv2image = img
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def start_video(self):
        if self.videoworker is None or not self.videoworker.isRunning():
            self.videoworker = CameraWorker(self.cam)
            self.videoworker.frame_received.connect(self.video)
            self.videoworker.start()

    def video(self, cv_img):
        self.img.cv2image = cv_img
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def stop_video(self):
        if self.videoworker or self.videoworker.isRunning():
            self.videoworker.stop()
            self.videoworker = None

    def find_dots(self):
        self.img.find_dots()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def show_histogram(self):
        pass

    def reset(self):
        self.img.reset()
        self.canvas.update_image(self.img.getPixmap(self.img.getQimage()))

    def closeEvent(self, event):
        # Ensure smooth shutdown so Python or the SDK daemon doesn't crash on exit
        cv2.imwrite("last_image.jpg", self.img.original)
        event.accept()


def startup():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    startup()
