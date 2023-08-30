#!/usr/bin/env python
# coding: UTF-8
#import apriltag
import pupil_apriltags as apriltag     # for windows
import cv2
import numpy as np
import sys
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
flag = cap.isOpened()

while flag:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 创建一个apriltag检测器，然后检测AprilTags
    options = apriltag.Detector(families='tag36h11 tag36h10')  # windows
    tags = options.detect(gray)
    print(tags)
    print("%d apriltags have been detected."%len(tags))
    for tag in tags:
        # cv2.circle(img, tuple(tag.corners[0].astype(int)), 4,(255,0,0), 2) # left-top
        # cv2.circle(img, tuple(tag.corners[1].astype(int)), 4,(255,0,0), 2) # right-top
        # cv2.circle(img, tuple(tag.corners[2].astype(int)), 4,(255,0,0), 2) # right-bottom
        # cv2.circle(img, tuple(tag.corners[3].astype(int)), 4,(255,0,0), 2) # left-bottom
        print(tag)
        cv2.imshow("apriltag_test",img)  
        r = tag
        b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
        c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
        d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
        a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])

    # # 绘制检测到的AprilTag的框
        cv2.line(img, a, b, (255, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.line(img, b, c, (255, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.line(img, c, d, (255, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.line(img, d, a, (255, 0, 255), 2, lineType=cv2.LINE_AA)

    # 绘制 AprilTag 的中心坐标
        (cX, cY) = (int(r.center[0]), int(r.center[1]))
        cv2.circle(img, (cX, cY), 5, (0, 0, 255), -1)

    # 在图像上绘制标文本
        tagFamily = r.tag_family.decode("utf-8")
        cv2.putText(img, tagFamily, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite('image%s.png'%str(r.tag_id), img)
    cv2.waitKey(1000)
cap.release() # 释放摄像头
cv2.destroyAllWindows()# 释放并销毁窗口