import cv2
import numpy as np

# Load image
img = cv2.imread('pictures/checkboard.jpg', cv2.IMREAD_GRAYSCALE)

# If image is null
if img is None:
    raise ValueError('Cannot read the image')
# Blur to reduce background noice
blurred  = cv2.GaussianBlur(img, (3,3), 0)

# calculates gradients cv2.sobel(bilde, ddepth, dx, dy, kernel size
# The ddepth needs to be a CV_64F because a change from black to white hives a negaive value wich uint8 cant do
sobel_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)

# convert back to uint8
abs_sobel_x = cv2.convertScaleAbs(sobel_x)
abs_sobel_y = cv2.convertScaleAbs(sobel_y)

sobel_combined = cv2.addWeighted(abs_sobel_x, 0.5, abs_sobel_y, 0.5, 0)
cv2.imshow('Test',sobel_combined)
cv2.waitKey(0)
cv2.destroyAllWindows()