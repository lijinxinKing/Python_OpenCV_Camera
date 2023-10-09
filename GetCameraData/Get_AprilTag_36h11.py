#!/usr/bin/env python
# coding: UTF-8
import pupil_apriltags as apriltag
import cv2,os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

def GetAprilTag36h11(tag_id):
    while True:
        ret,img = cap.read()
        if ret:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 创建一个apriltag检测器
        detector = apriltag.Detector(families='tag36h11') # windows
        # 进行apriltag检测，得到检测到的apriltag的列表
        tags = detector.detect(gray)
        for tag in tags:
            cv2.circle(img, tuple(tag.corners[0].astype(int)), 1, (255, 0, 255), 2)  # left-top
            cv2.circle(img, tuple(tag.corners[1].astype(int)), 1, (255, 0, 255), 2)  # right-top
            cv2.circle(img, tuple(tag.corners[2].astype(int)), 1, (255, 0, 255), 2)  # right-bottom
            cv2.circle(img, tuple(tag.corners[3].astype(int)), 1, (255, 0, 255), 2)  # left-bottom
            print(tag.tag_id)
            if tag.tag_id == tag_id:
                return tag.center
        cv2.imshow("out_image", img)
        cv2.imwrite('image.png', img)
        if cv2.waitKey(500) & 0xFF == 27:
            break