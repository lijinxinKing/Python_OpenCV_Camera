#MoveRobot.py
import pupil_apriltags as apriltag
import cv2
import numpy as np
import sys
import time
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
time.sleep(1)
flag = cap.isOpened()
w=122
h=291
time.sleep(1)
ret, frame = cap.read()
img = frame
print(img.shape)
filename = 'savedImage.jpg'
# Using cv2.imwrite() method
print("Saving the image")
isWritten = cv2.imwrite(filename, img)
if isWritten:
    print('The image is successfully saved.')
else:
    print('The image is failed saved.')