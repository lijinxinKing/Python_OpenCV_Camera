#import settings,recognition_aprilTag

import numpy as np
import cv2
import os
import sys,time
from pymycobot.ultraArm import ultraArm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Elephantrobotics import settings,move_zero,recognition_aprilTag

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
font = cv2.FONT_HERSHEY_SIMPLEX
lower_red = np.array([156, 43, 46])  # 红色低阈值
upper_red = np.array([180, 255, 255])  # 红色高阈值

lower_blue = np.array([100, 43, 46])  # 蓝色低阈值
upper_blue = np.array([124, 255, 255])  # 蓝色高阈值

lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

lower_yellow = np.array([26, 43, 46])
upper_yellow = np.array([34, 255, 255])

#紫色
lower_purple = np.array([125, 43, 46])
upper_purple = np.array([155, 255, 255])

# cap = cv2.VideoCapture(1)  # 打开USB摄像头
# if (cap.isOpened()):  # 视频打开成功
#     flag = 1
# else:
#     flag = 0
# num = 0

# calculate the coords between cube and ultraArm P340
# 计算立方体和 mycobot 之间的坐标

"""
    Calibrate the camera according to the calibration parameters.
    Enlarge the video pixel by 1.5 times, which means enlarge the video size by 1.5 times.
    If two ARuco values have been calculated, clip the video.
"""


def transform_frame(self, frame):
    # enlarge the image by 1.5 times
    fx = 1.5
    fy = 1.5
    frame = cv2.resize(frame, (0, 0), fx=fx, fy=fy,
                       interpolation=cv2.INTER_CUBIC)
    if self.x1 != self.x2:
        # the cutting ratio here is adjusted according to the actual situation
        frame = frame[int(self.y2*0.6):int(self.y1*1.1),
                      int(self.x1*0.82):int(self.x2*1.08)]
    return frame


def get_position(self, x, y):
    return ((y - self.c_y)*self.ratio + self.camera_x), ((x - self.c_x)*self.ratio + self.camera_y)


# get points of two aruco 获得两个 aruco 的点位
def get_calculate_params(self, img):
    # Convert the image to a gray image 将图像转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect ArUco marker.
    corners, ids, rejectImaPoint = cv2.aruco.detectMarkers(
        gray, self.aruco_dict, parameters=self.aruco_params
    )

    """
        Two Arucos must be present in the picture and in the same order.
        There are two Arucos in the Corners, and each aruco contains the pixels of its four corners.
        Determine the center of the aruco by the four corners of the aruco.
        """
    if len(corners) > 0:
        if ids is not None:
            if len(corners) <= 1 or ids[0] == 1:
                return None
            x1 = x2 = y1 = y2 = 0
            point_11, point_21, point_31, point_41 = corners[0][0]
            x1, y1 = int((point_11[0] + point_21[0] + point_31[0] + point_41[0]) / 4.0), int(
                (point_11[1] + point_21[1] + point_31[1] + point_41[1]) / 4.0)
            point_1, point_2, point_3, point_4 = corners[1][0]
            x2, y2 = int((point_1[0] + point_2[0] + point_3[0] + point_4[0]) / 4.0), int(
                (point_1[1] + point_2[1] + point_3[1] + point_4[1]) / 4.0)

            return x1, x2, y1, y2
    return None


def color_detect():
    # set the arrangement of color'HSV
    x = y = 0
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()  # 读取一帧
        if ret == False:  # 读取帧失败
            cap = cv2.VideoCapture(1)
            ret, frame = cap.read()
            if ret == False:
                return False
        color = -1
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_location = {}
        HSV = {
            # "yellow": [np.array([11, 85, 70]), np.array([59, 255, 245])],
            # "red": [np.array([0, 43, 46]), np.array([8, 255, 255])],
            "green": [np.array([35, 43, 35]), np.array([90, 255, 255])],
            # "blue": [np.array([100, 43, 46]), np.array([124, 255, 255])],
            # "cyan": [np.array([78, 43, 46]), np.array([99, 255, 255])],
        }
        for mycolor, item in HSV.items():
            # print("mycolor:",mycolor)
            redLower = np.array(item[0])
            redUpper = np.array(item[1])
            # transfrom the img to model of gray 将图像转换为灰度模型
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # print("hsv",hsv)
            # wipe off all color expect color in range 擦掉所有颜色期望范围内的颜色
            mask = cv2.inRange(hsv, item[0], item[1])
            # a etching operation on a picture to remove edge roughness
            # 对图片进行蚀刻操作以去除边缘粗糙度
            erosion = cv2.erode(mask, np.ones((1, 1), np.uint8), iterations=2)
            # the image for expansion operation, its role is to deepen the color depth in the picture
            # 用于扩展操作的图像，其作用是加深图片中的颜色深度
            dilation = cv2.dilate(erosion, np.ones(
                (1, 1), np.uint8), iterations=2)
            # adds pixels to the image 向图像添加像素
            target = cv2.bitwise_and(img, img, mask=dilation)
            # the filtered image is transformed into a binary image and placed in binary
            # 将过滤后的图像转换为二值图像并放入二值
            ret, binary = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)
            # get the contour coordinates of the image, where contours is the coordinate value, here only the contour is detected
            # 获取图像的轮廓坐标，其中contours为坐标值，这里只检测轮廓
            contours, hierarchy = cv2.findContours(
                dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                # do something about misidentification
                boxes = [
                    box
                    for box in [cv2.boundingRect(c) for c in contours]
                    if min(img.shape[0], img.shape[1]) / 10
                    < min(box[2], box[3])
                    < min(img.shape[0], img.shape[1]) / 1
                ]
                if boxes:
                    for box in boxes:
                        x, y, w, h = box
                    # find the largest object that fits the requirements 找到符合要求的最大对象
                    c = max(contours, key=cv2.contourArea)
                    # get the lower left and upper right points of the positioning object
                    # 获取定位对象的左下和右上点
                    x, y, w, h = cv2.boundingRect(c)
                    # locate the target by drawing rectangle 通过绘制矩形来定位目标
                    # cv2.rectangle(img, (x, y), (x+w, y+h), (153, 153, 0), 2) (0, 255, 0), 1)
                    cv2.rectangle(img, (x, y), (x+w, y+h), (153, 153, 0), 1)
                    #cv2.rectangle(frame, (x, y), (x + w, y + h), (153, 153, 0), 1)

                    #cv2.putText(frame,setStr,(x, y - 5),font,0.3,(153, 153, 0), 1)
                    # calculate the rectangle center 计算矩形中心
                    x, y = (x*2+w)/2, (y*2+h)/2
                    # calculate the real coordinates of ultraArm P340 relative to the target
                    #  计算 mycobot 相对于目标的真实坐标
                    # if mycolor  == "yellow":
                    #     color = 3
                    # elif mycolor == "red":
                    #     color = 0
                    if mycolor == "green":
                        color = 1
                        # if color_location.get(color) == None:
                        #     color_location[color]=(x,y,w,h)
                        # if len(color_location) >= 1:
                        #     print (color_location)
                        #result = (x3, y3, w3, h3,piex_distance)
                        piex = round(w/2, 2)
                        piex_distance = round(piex / 15, 2)

                        return (x, y, w, h, piex_distance)
        # cv2.imshow("dection", frame)
        # if cv2.waitKey(1000) & 0xFF == 27:
        #      return False
        # 判断是否正常识别
        # if abs(x) + abs(y) > 0:
        #     return x, y
        # else:
        #     return None


def GetRealTime(colorType):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # 打开USB摄像头
    cap.set(3, 1280)  # 设置分辨率
    cap.set(4, 720)

    match str(colorType).lower():
        case 'yellow':
            lower_color = lower_yellow
            upper_color = upper_yellow
            pass
        case 'green':
            lower_color = lower_green
            upper_color = upper_green
            pass
        case 'red':
            lower_color = lower_red
            upper_color = upper_red
            pass
        case 'blue':
            lower_color = lower_blue
            upper_color = upper_blue
            pass
        case 'purple':
            lower_color = lower_purple
            upper_color = upper_purple
            pass

    while True:
        ret, frame = cap.read()  # 读取一帧
        if ret == False:  # 读取帧失败
            return False
        y = int(frame.shape[0] / 2)
        x = int(frame.shape[1] / 2)
        point_size = 1
        point_color = (0, 0, 255)  # BGR
        thickness = 2
        point = (x, y)

        getCurrentHigh = 101  # get_distance_byport.GetCurrentDistance()
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_ = cv2.inRange(hsv_img, lower_color, upper_color)
        mask_ = cv2.medianBlur(mask_, 7)
        contours3, hierarchy3 = cv2.findContours(
            mask_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt3 in contours3:
            (x3, y3, w3, h3) = cv2.boundingRect(cnt3)
            piex = w3 * h3
            if piex < 400:
                continue
            cv2.rectangle(frame, (x3, y3), (x3 + w3, y3 + h3),
                          (255, 255, 255), 1)
            setStr = "["+str(x3)+" "+str(y3)+" "+" "+str(w3)+" "+str(h3) + "]"
            print(setStr)
            cv2.putText(frame, setStr, (x3-w3, y3 + 2*h3),
                        font, 0.3, (255, 255, 255), 1)
            now_f = "KeyboardLayout\\{}\\{}.jpg".format(colorType,time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())))                
            if os.path.exists(now_f):
                os.remove(now_f)
            cv2.imwrite(now_f,frame) #保存图片
        cv2.imshow("dection", frame)
        if cv2.waitKey(500) & 0xFF == 27:
            return False
    # detect cube color

def get_Color(colorType):
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        settings.Camera.set(3, 1280)
        settings.Camera.set(4, 720)
        ret, frame = settings.Camera.read()  # 读取一帧
        if ret == False:
            recognition_aprilTag.start_exe()
    else:
        ret, frame = settings.Camera.read()
        if ret == False:
            recognition_aprilTag.start_exe()
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            ret, frame = settings.Camera.read()  # 读取一帧
            if ret:
                return False
    y = int(frame.shape[0] / 2)
    x = int(frame.shape[1] / 2)
    point_size = 1
    point_color = (0, 0, 255)  # BGR
    thickness = 2
    lower_color = None
    upper_color = None
    # 画点
    match str(colorType).lower():
        case 'yellow':
            lower_color = lower_yellow
            upper_color = upper_yellow
            pass
        case 'green':
            lower_color = lower_green
            upper_color = upper_green
            pass
        case 'red':
            lower_color = lower_red
            upper_color = upper_red
            pass
        case 'blue':
            lower_color = lower_blue
            upper_color = upper_blue
            pass
        case 'purple':
            lower_color = lower_purple
            upper_color = upper_purple
            pass
    
    point = (x, y)  # 点的坐标。画点实际上就是画半径很小的实心圆。
    cv2.circle(frame, point, point_size, point_color, thickness)
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # 根据颜色范围删选
    mask_ = cv2.inRange(hsv_img, lower_color, upper_color)
    mask_ = cv2.medianBlur(mask_, 7)
    contours3, hierarchy3 = cv2.findContours(
        mask_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    MaxBox = 0
    MaxX = 0
    MaxY = 0
    MaxW = 0
    MaxH = 0
    for cnt3 in contours3:
        (x3, y3, w3, h3) = cv2.boundingRect(cnt3)
        currentBox = w3 * h3
        if currentBox > MaxBox:
            MaxBox = currentBox
            MaxX = x3
            MaxY = y3
            MaxW = w3
            MaxH = h3
            setStr = "["+str(x3)+" "+str(y3)+" "+" "+str(w3)+" "+str(h3) + "]"
            cv2.rectangle(frame, (x3, y3), (x3 + w3, y3 + h3),(255, 255, 255), 1)
            cv2.putText(frame, setStr, (x3-w3, y3 + h3),font, 0.8, (255, 255, 255), 1)
            now_f = "GetRealPictures\\{}\\{}.jpg".format(colorType,time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())))                
            if os.path.exists(now_f):
                os.remove(now_f)
            cv2.imwrite(now_f,frame)
    result = (MaxX, MaxY, MaxW, MaxH)
    print('\'{}\' color location {}'.format(colorType,result))
    return result

def SetRobotForCutLongKey():
    target_x = 0
    target_y = 0
    global move_down_distance
    if settings.SmartArm == None:
        deviceName = move_zero.getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    time.sleep(1.5)

    haveMoveLeft = 0
    haveMoveRight = 0

    print('Set Green Y Location: ')
    for i in range(0, 15):
        result = get_Color('Green')
        red_location = get_Color("Red")
        x, y, w, h = result
        red_x,red_y,red_w,red_h = red_location
        green_center_x = x + w/2
        green_center_y = y + h/2
        red_end_x = red_x + red_h
        red_end_y = red_y

        if abs(x - red_end_x) > 110:
            target_x = 3
            haveMoveLeft = haveMoveLeft + 1
            if haveMoveRight > 2:
                break
        elif x + w > red_end_x:
            target_x = -3
            haveMoveRight = haveMoveRight + 1
            if haveMoveLeft > 2:
                break
        else:
            target_x = 0
            break
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0], coords[1]-target_x, coords[2], coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)

    print('Set Green X Location: ')
    preTargetY = 0
    for i in range(0, 15):
        result = get_Color('Green')
        get_Color("Red")
        x, y, w, h = result
        if y < 30:
            break
        if y < 100:
            target_y = -3
        elif y > 120:
            target_y = 3
        else:
            target_y = 0
            break
        if preTargetY != 0 and preTargetY != target_y:
            break
        else:
            preTargetY = target_y
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0]-target_y, coords[1], coords[2], coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)


if __name__ == "__main__":
   GetRealTime("Green")
