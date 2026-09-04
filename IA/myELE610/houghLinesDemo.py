import math

import cv2
import numpy as np
from matplotlib import pyplot as plt
img = cv2.imread('pictures/checkboard_new.jpg', cv2.IMREAD_GRAYSCALE)

# If image is null
if img is None:
    raise ValueError('Cannot read the image')

blurred  = cv2.GaussianBlur(img, (5,5), 0)
edges = cv2.Canny(blurred,100,200)

lines = cv2.HoughLines(blurred, 1, np.pi/180, 150, None, 0, 0)
cdst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
# draw lines
if lines is not None:
    for i in range(0,len(lines)):
        rho =  lines[i][0][0]
        theta = lines[i][0][1]
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a*rho
        y0 = b*rho

        pt1 = int(x0 + 3000*(-b)), int(y0 + 3000*(a))
        pt2 = int(x0 - 3000*(-b)), int(y0 - 3000*(a))

        cv2.line(cdst,pt1,pt2,(0,0,255),3, cv2.LINE_AA)

cv2.imshow("With red lines", cdst)
cv2.waitKey(0)
cv2.destroyAllWindows()