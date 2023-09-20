#!/usr/bin/env python
# coding: UTF-8
#import apriltag
import pupil_apriltags as apriltag
import cv2
import numpy as np
import sys
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
flag = cap.isOpened()
while flag:
    ret, frame = cap.read()
    img = frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 创建一个apriltag检测器
    at_detector = apriltag.Detector(families='tag36h11') 
    # at_detector = apriltag.Detector(families='tag36h11 tag25h9')  #for windows
    # 进行apriltag检测，得到检测到的apriltag的列表
    tags = at_detector.detect(gray)
    print("%d apriltags have been detected."%len(tags))
    for tag in tags:
        cv2.circle(img, tuple(tag.corners[0].astype(int)), 4,(255,0,0), 1) # left-top
        cv2.circle(img, tuple(tag.corners[1].astype(int)), 4,(255,0,0), 1) # right-top
        cv2.circle(img, tuple(tag.corners[2].astype(int)), 4,(255,0,0), 1) # right-bottom
        cv2.circle(img, tuple(tag.corners[3].astype(int)), 4,(255,0,0), 1) # left-bottom
        a = (tuple(tag.corners[3].astype(int))[0], tuple(tag.corners[3].astype(int))[1])
        cv2.putText(img, str(tag.tag_id)+","+str(tag.center), (a[0]-100, a[1]- 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("apriltag_test",img)
    k = cv2.waitKey(1000)
    if k == 27:    # Esc key to stop
        break
