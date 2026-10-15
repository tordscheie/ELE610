import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from pyueye import ueye


class CameraWorker(QThread):
    frame_received = pyqtSignal(np.ndarray)

    def __init__(self, cam_instance):
        super().__init__()
        self.cam = cam_instance
        self.is_running = True

    def run(self):
        ueye.is_CaptureVideo(self.cam.h_cam, ueye.IS_DONT_WAIT)

        while self.is_running:
            frame = self.cam.getcv2image()
            if frame is not None:
                with_dots = self.find_dots(frame)
                self.frame_received.emit(with_dots)
            self.msleep(66)  # Match target framerate (~15 FPS)

        self.cam.stopLiveVideo()

    def find_dots(self, frame):
        temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            cv2.GaussianBlur(temp, (3, 3), 0),
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=25,
            param1=70,
            param2=15,
            minRadius=5,
            maxRadius=35,
        )
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # Draw the outer circle (green)
                cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # Draw the center of the circle (red dot)
                cv2.circle(frame, (i[0], i[1]), 2, (0, 255, 0), 3)
        return frame

    def stop(self):
        self.is_running = False
        self.wait()
