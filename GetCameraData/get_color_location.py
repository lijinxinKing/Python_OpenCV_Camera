import numpy as np
import cv2
font = cv2.FONT_HERSHEY_SIMPLEX
lower_red = np.array([0, 127, 128])  # 红色低阈值
upper_red = np.array([5, 255, 255])  # 红色高阈值
lower_blue = np.array([35, 43, 46])  # 蓝色低阈值
upper_blue = np.array([77, 255, 255])  # 蓝色高阈值
lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

cap = cv2.VideoCapture(1)  # 打开USB摄像头
if (cap.isOpened()):  # 视频打开成功
    flag = 1
else:
    flag = 0
num = 0
#cv2.undistortPoints()

print(flag)
def getColor():
        ret, frame = cap.read()  # 读取一帧
        if ret == False:  # 读取帧失败
            return False
        y = int(frame.shape[0] / 2)
        x = int(frame.shape[1] / 2)
        #print((x,y))
        point_size = 1
        point_color = (0, 0, 255)  # BGR
        thickness = 2
        # 画点
        point = (x, y)  # 点的坐标。画点实际上就是画半径很小的实心圆。
        cv2.circle(frame, point, point_size, point_color, thickness)
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)# 根据颜色范围删选
        #mask_red = cv2.inRange(hsv_img, lower_red, upper_red)
        mask_blue = cv2.inRange(hsv_img, lower_blue, upper_blue)
        #mask_red = cv2.medianBlur(mask_red, 7)        # 中值滤波
        mask_blue = cv2.medianBlur(mask_blue, 7) 
        #mask = cv2.bitwise_or(mask_red, mask_blue,)  # 检测轮廓
        #contours2, hierarchy2 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours3, hierarchy3 = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # for cnt2 in contours2:
        #     (x, y, w, h) = cv2.boundingRect(cnt2)  # 该函数返回矩阵四个点
        #     a = x + w / 2
        #     b = y + h / 2
        #     print("red:", a, b)
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
        #     cv2.putText(frame, 'red', (x, y - 5), font, 0.7, (0, 0, 255), 2)
        for cnt3 in contours3:
            (x3, y3, w3, h3) = cv2.boundingRect(cnt3)
            piex = (w3 + h3) / 2
            piex_distance = piex / 15
            print((x3, y3, w3, h3,piex_distance))
            return ((x3, y3, w3, h3,piex_distance))
            cv2.rectangle(frame, (x3, y3), (x3 + w3, y3 + h3), (0, 255, 0), 1)
            cv2.putText(frame, "Green", (x3, y3 - 5), font, 0.3, (0, 255, 0), 1)
        global num
        num = num + 1
        cv2.imshow("dection", frame)
        cv2.imwrite("imgs/%d.jpg" % num, frame)#照片写入，注释后不保存图片，但未注释的需要建imgs
        if cv2.waitKey(20) & 0xFF == 27:
            return False
# if (flag):
#     while (True):
#         if getColor() == False:
#             break
getColor()

#cv2.waitKey(0)
#cv2.destroyAllWindows()

# -*- coding: utf-8 -*-
 