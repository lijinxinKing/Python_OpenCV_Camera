import cv2,os
import numpy as np
cap = cv2.VideoCapture(1)#打开内置摄像机
flag = 1 
f = 'Temp_4.jpg'
count = 0; #记录照相的次数
if cap.isOpened(): #当摄像头打开时
    ret,frame=cap.read() #读取当前摄像头画面
    cv2.imshow('img',frame) #显示当前摄像头画面
    if os.path.exists(f):
        os.remove(f)
    cv2.imwrite(f,frame) #保存图片
    cv2.waitKey(1000)
cv2.destroyAllWindows() #关闭所有窗口
cap.release() #释放摄像头