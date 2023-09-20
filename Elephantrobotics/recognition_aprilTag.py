import pupil_apriltags as apriltag
import cv2
import numpy as np
import time
import subprocess
from Elephantrobotics import settings
getAllTags = []
getMachineAprilTag = []
import os
def GetMachineAprilTag():
    i = 0
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    flag = cap.isOpened()
    getAllTags = []
    while i < 10:
        try:
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                at_detector = apriltag.Detector(families='tag36h11') # 创建一个apriltag检测器
                tags = at_detector.detect(gray)
                if len(tags) > 0:
                    for tag in tags:
                        if tag.tag_id != 586:
                            getAllTags.append(tag)
                else:
                    time.sleep(0.1)
                if len(getAllTags) > 0:
                    cap.release()
                    break
            i = i + 1
        except:
            print("Error")
    cap.release()
    return getAllTags
exe_path = ""
def start_exe():
    # 定义exe文件路径和名称
    # 执行exe文件
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    print(desktop_path)
    exe_path = desktop_path + "\\" + "Camera.exe"
    subprocess.Popen(exe_path)
    time.sleep(3)
    os.system("c:\\windows\\System32\\taskkill /F /IM Camera.exe")

def GetAprilTagByTagId(tagId):
    i = 0
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    flag = cap.isOpened()
    getAllTags = []
    while i < 10:
        ret, frame = cap.read()       
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 创建一个apriltag检测器
            at_detector = apriltag.Detector(families='tag36h11') 
            tags = at_detector.detect(gray)
            if len(tags) >= 0:
                for tag in tags:
                    print(tag.tag_id)
                    if tag.tag_id == tagId:
                        print(tag)
                        x = tag.corners[0][0]
                        y = tag.corners[0][1]
                        w = abs(tag.corners[0][0] - tag.corners[2][0])
                        h = abs(tag.corners[0][1] - tag.corners[1][1])
                        ratio = (float(w+h)/2)/9
                        return (x,y,w,h,ratio)
                        getAllTags.append(tag)
            else:
                time.sleep(0.1)
            if len(getAllTags) >= 1:
                cap.release()
                break
            elif len(getAllTags) == 0:
                cap.release()
                start_exe()
                time.sleep(1)
                cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                time.sleep(1)
        i = i + 1
    cap.release()
    return None

def GetCalibration():
    i = 0
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    while i < 10:
        ret, frame = settings.Camera.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 创建一个apriltag检测器
            at_detector = apriltag.Detector(families='tag36h11') 
            tags = at_detector.detect(gray)
            if len(tags) > 1:
                for tag in tags:
                    if tag.tag_id != 0:
                        getAllTags.append(tag)
            else:
                time.sleep(0.1)
            if len(getAllTags) >= 2:
                #cap.release()
                break
            elif len(getAllTags) == 0:
                settings.Camera.release()
                start_exe()
                settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                time.sleep(1)
        else:
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            ret, frame = settings.Camera.read()
        i = i + 1
    return getAllTags

if __name__=="__main__":
    GetAprilTagByTagId(1)