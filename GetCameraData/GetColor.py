#2. 绿色颜色识别
#python
import cv2
import numpy as np
# 读取图片
font = cv2.FONT_HERSHEY_SIMPLEX
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
flag = cap.isOpened()
if flag:
    ret, frame = cap.read()
    img = frame
#img = cv2.imread('D:/picture/2.png')
# 转换颜色空间为HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# 定义绿色范围
    lower_green = np.array([35, 43, 46])
    upper_green = np.array([77, 255, 255])
# 创建掩膜
    mask = cv2.inRange(hsv, lower_green, upper_green)
# 进行图像处理
    res = cv2.bitwise_and(img, img, mask=mask)
    mask_red = cv2.medianBlur(mask, 7)        # 中值滤波
    mask = cv2.bitwise_or(mask_red)  # 检测轮廓
    contours2, hierarchy2 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #contours3, hierarchy3 = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt2 in contours2:
        (x, y, w, h) = cv2.boundingRect(cnt2)  # 该函数返回矩阵四个点
        a = x + w / 2
        b = y + h / 2
        print("red:", a, b)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
        cv2.putText(frame, 'red', (x, y - 5), font, 0.7, (0, 0, 255), 2)
# 显示结果
    cv2.imshow('image', img)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()