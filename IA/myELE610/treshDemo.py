import cv2
import numpy as np
from matplotlib import pyplot as plt
img = cv2.imread('pictures/checkboard_new.jpg', cv2.IMREAD_GRAYSCALE)

# If image is null
if img is None:
    raise ValueError('Cannot read the image')

ret,thresh2 = cv2.threshold(img,190,255,cv2.THRESH_TOZERO)
ret, thresh1 = cv2.threshold(img,120,255,cv2.THRESH_BINARY)
cv2.imshow('thresh',thresh1)
cv2.waitKey(0)
cv2.destroyAllWindows()