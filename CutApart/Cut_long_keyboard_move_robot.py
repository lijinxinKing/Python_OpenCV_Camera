import time
from pymycobot.ultraArm import ultraArm
import socket
import pupil_apriltags as apriltag
import serial.tools.list_ports
import sys,os,cv2,math
import redis,uuid,base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Elephantrobotics import move_zero
from Elephantrobotics import settings,move_sliderbar,recognition_aprilTag,move_robot
from CameraLocationTest import TestPictureFile
from GetDistance import get_distance_byport
from get_ip import IP
import numpy as np
import requests,json,time
import ManageSmartFingure,RedisManage

c_x = settings.resolutionRatio_Width/2
c_y = settings.resolutionRatio_Height/2
font = cv2.FONT_HERSHEY_SIMPLEX
key_cx = 0
key_cy = 0

CurrentSlideBarDistanceFile = "C:\\CurrentSlideBarDistanceFile.txt"
SlideBarDistanceFile = "C:\\SlideBarDistanceFile.txt"
SlideTotalLength = 500
green_moveX = 0
green_moveY = 0
move_down = 0


lower_red = np.array([0, 43, 46])  # 红色低阈值
upper_red = np.array([10, 255, 255])  # 红色高阈值

lower_blue = np.array([100, 43, 46])  # 蓝色低阈值
upper_blue = np.array([124, 255, 255])  # 蓝色高阈值

lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

lower_yellow = np.array([26, 43, 46])
upper_yellow = np.array([34, 255, 255])

ZERO = [235.55, 18, 130.0, 0.0]
#紫色
lower_purple = np.array([125, 43, 46])
upper_purple = np.array([155, 255, 255])
resultMsg = ""

def GetAprilTag(allAprilTag: [], tag_id):
    for tag in allAprilTag:
        if str(tag.tag_id) == str(tag_id):
            return tag

def GetAllAprilTag(aprilTag_count=2):
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        flag = settings.Camera.isOpened()
        if flag == False:
            recognition_aprilTag.start_exe()
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            flag = settings.Camera.isOpened()
            if flag == False:
                return
    settings.Camera.set(3, settings.resolutionRatio_Width)  # 设置分辨率
    settings.Camera.set(4, settings.resolutionRatio_Height)
    checkTinmes: int = 10
    maxLen = -1
    allAprilTags = []

    while checkTinmes > 0:
        ret, frame = settings.Camera.read()
        img = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        at_detector = apriltag.Detector(families='tag36h11')
        tags = at_detector.detect(gray)
        if len(tags) > maxLen:
            maxLen = len(tags)
            print("%d apriltags have been detected." % len(tags))
            allAprilTags = []
            for tag in tags:
                cv2.circle(img, tuple(tag.corners[0].astype(
                    int)), 4, (255, 0, 0), 1)  # left-top
                cv2.circle(img, tuple(tag.corners[1].astype(
                    int)), 4, (255, 0, 0), 1)  # right-top
                cv2.circle(img, tuple(tag.corners[2].astype(
                    int)), 4, (255, 0, 0), 1)  # right-bottom
                cv2.circle(img, tuple(tag.corners[3].astype(
                    int)), 4, (255, 0, 0), 1)  # left-bottom
                a = (tuple(tag.corners[3].astype(int))[
                     0], tuple(tag.corners[3].astype(int))[1])
                cv2.putText(img, str(tag.tag_id)+","+str(tag.center),
                            (a[0]-100, a[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                print("  tag id {}".format(tag.tag_id))
                allAprilTags.append(tag)
        if len(allAprilTags) == aprilTag_count:
            checkTinmes = checkTinmes - 1
        cv2.waitKey(100)
    return allAprilTags

def GetAprilTagByID(tagID):
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    settings.Camera.set(3, settings.resolutionRatio_Width)  # 设置分辨率
    settings.Camera.set(4, settings.resolutionRatio_Height)
    checkTinmes: int = 10
    maxLen = -1
    allAprilTags = []

    flag = settings.Camera.isOpened()
    while flag and checkTinmes > 0:
        ret, frame = settings.Camera.read()
        img = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        at_detector = apriltag.Detector(families='tag36h11')
        tags = at_detector.detect(gray)
        print("%d apriltags have been detected." % len(tags))
        if len(tags) > maxLen:
            maxLen = len(tags)
            allAprilTags = []
            for tag in tags:
                cv2.circle(img, tuple(tag.corners[0].astype(
                    int)), 4, (255, 0, 0), 1)  # left-top
                cv2.circle(img, tuple(tag.corners[1].astype(
                    int)), 4, (255, 0, 0), 1)  # right-top
                cv2.circle(img, tuple(tag.corners[2].astype(
                    int)), 4, (255, 0, 0), 1)  # right-bottom
                cv2.circle(img, tuple(tag.corners[3].astype(
                    int)), 4, (255, 0, 0), 1)  # left-bottom
                a = (tuple(tag.corners[3].astype(int))[
                     0], tuple(tag.corners[3].astype(int))[1])
                cv2.putText(img, str(tag.tag_id)+","+str(tag.center),
                            (a[0]-100, a[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                if tag.tag_id == tagID:
                    allAprilTags.append(tag)
        checkTinmes = checkTinmes - 1
        cv2.waitKey(1000)
    return allAprilTags

def GetKeyboardLocation(machineIndex, keyboardCode):
    frame = None
    for i in range(0, 5):
        if settings.Camera == None:
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            settings.Camera.set(3, settings.resolutionRatio_Width)
            settings.Camera.set(4, settings.resolutionRatio_Height)
            cv2.waitKey(100)
            ret, frame = settings.Camera.read()
        else:   
            ret, frame = settings.Camera.read()
            if ret == False:
                settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                cv2.waitKey(100)
                ret, frame = settings.Camera.read()
                if ret != False:
                    break
            else:
                break
    target_path = 'KeyboardLayout\\Keyboard_layout_{}.jpg'.format(str(machine_id))
    if os.path.exists(target_path):
        os.remove(target_path)

    cv2.imwrite(target_path, frame)
    data = None
    with open(target_path, "rb") as f:
        tk = f.read()
        image = base64.b64encode(tk)
        data ={"image": image.decode("utf-8")}
    try:
        jsonFileName = "KeyboardLayout\\data_{}_temp.json".format(machineIndex)
        url = "http://10.119.96.106:58083/"
        print('{} Get Keyboard Location'.format(keyboardCode))
        resp = requests.post(url+"image/segment?code={}&keyboard=1&show=1&name=keyboard&async=1".format(keyboardCode), json=data)
        print("Request url is " + str(resp))
        json_data = json.loads(resp.text)
        getLocation = url+json_data['taskid']
        print(getLocation)
        while True:
            resp = requests.get(getLocation)
            print(resp.status_code)
            if resp.status_code != 404:
                print(resp.text)
                with open(jsonFileName, 'w') as f:
                    f.write(resp.text)
                print("Finished")
                break
            print(resp.text)
            time.sleep(5)
        return True
    except:
        print('发送请求失败')
        return False

def GetMachineIndex1(machineIndex, keyboardCode):
    global taskUUID
    frame = None
    for i in range(0, 5):
        if settings.Camera == None:
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            settings.Camera.set(3, settings.resolutionRatio_Width)
            settings.Camera.set(4, settings.resolutionRatio_Height)
            ret, frame = settings.Camera.read()  # 读取一帧
        else:   
            ret, frame = settings.Camera.read()
            if ret == False:
                settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                ret, frame = settings.Camera.read()  # 读取一帧
                if ret != False:
                    break

    cv2.imwrite(target_path, frame)  # 保存按下空格键时摄像头视频中的图像
    pool = redis.ConnectionPool(
        host='10.119.96.35', port=6379, password='', db=1)
    #实现一个连接池
    r = redis.Redis(connection_pool=pool)
    # 清空第二个数据库
    r.flushdb()
    with open(target_path, "rb") as f:
        tk = f.read()
        image = base64.b64encode(tk)
        data = image.decode("utf-8")
        #分段存入
        data_len = len(data)
        first_len = int(data_len / 2)
        data_1 = data[0:first_len]
        data_2 = data[first_len:data_len]
        taskUUID = uuid.uuid1()
        print("Set Location Task to redis: ")
        r.set(str(taskUUID)+":1", str(data_1))
        r.set(str(taskUUID)+":2", str(data_2))
        r.set(str(taskUUID)+":code", keyboardCode)
    finished = []
    jsonFileName = "KeyboardLayout\\data_{}_temp.json".format(machineIndex)
    while True:
        finished = r.get(str(taskUUID)+":Finished")
        if finished != None:
            iamgeResult = finished.decode("utf-8")
            with open(jsonFileName, "w") as file:
                file.write(iamgeResult)
            print("Get Location Task to redis Finished!")
            break
        else:
            time.sleep(5)

def ClickTagKey(target_tag, moveX, moveY, tagID=None):
    if target_tag != None:
        target_x = target_tag.corners[0][0]
        target_y = target_tag.center[1]
        print(target_tag)

        offset_x = (target_x - key_cx) / ratio
        offset_y = (target_y - key_cy) / ratio

        offset_moveX = moveX - offset_y
        offset_moveY = moveY + offset_x
        moveCoords_key = [offset_moveX, offset_moveY, -66]
        settings.SmartArm.set_coords(moveCoords_key, 85)
        print("The Key is  {}, Target Move offset: {} ".format(
            target_tag.tag_id, (offset_moveX, offset_moveY)))
        press_moveCoords_key = [offset_moveX, offset_moveY, -85]
        settings.SmartArm.set_coords(press_moveCoords_key, 40)
        time.sleep(0.1)
        settings.SmartArm.set_coords(moveCoords_key, 40)

def ScanAllMachines():
    currentDistance = 0
    if os.path.exists(CurrentSlideBarDistanceFile):
        with open(CurrentSlideBarDistanceFile) as f:
            content = f.read()
            currentDistance = content
    distance = 0 - round(float(currentDistance))
    if distance != 0:  # 归零
        result = move_sliderbar.MoveSlideByCode(distance)
        if result:
            if os.path.exists(CurrentSlideBarDistanceFile):
                os.remove(CurrentSlideBarDistanceFile)
        else:
            print("The Slider is not Launch")
            return settings.SliderNotLaunch
    if os.path.exists(SlideBarDistanceFile):
        os.remove(SlideBarDistanceFile)

    moveLength = 0
    needMoveHigh = False
    MachinesDistance = {}
    move_sliderbar.serial_open()
    moveStepDistance = -10
    sendPreID = -1
    while abs(moveLength) < abs(SlideTotalLength):
        sendStr = "CJXCGX{}F6000$".format(moveStepDistance)
        move_sliderbar.COMM.write(sendStr.encode())
        waitTime = abs(moveStepDistance / 15) + 1
        time.sleep(waitTime)
        move_sliderbar.COMM.write(move_sliderbar.stopRun.encode())
        moveLength = moveLength + moveStepDistance
        with open(CurrentSlideBarDistanceFile, 'w') as file:
            file.write(str(moveLength))
        moveDirection = -1
        machineAprilTags = recognition_aprilTag.GetMachineAprilTag()
        if len(machineAprilTags) > 0:
            aprilTagLocation = machineAprilTags
            aprilTag_center_x = round(
                aprilTagLocation[0].center[0])  # x_center
            tag_id = aprilTagLocation[0].tag_id
            if aprilTag_center_x > 400:
               if str(tag_id) not in MachinesDistance:
                   xMove = aprilTag_center_x - 220
                   moveStepDistance = -10  # (xMove * moveDirection)/2
                   willMoveTotalLen = abs(moveStepDistance + moveLength)
                   if willMoveTotalLen > abs(SlideTotalLength):
                       break
            elif aprilTag_center_x < 50:
                if str(tag_id) in MachinesDistance:
                    moveStepDistance = (220 * moveDirection)/2
                    willMoveTotalLen = abs(moveStepDistance + moveLength)
                    if willMoveTotalLen > abs(SlideTotalLength):
                        break
            else:
                moveStepDistance = -10
            if aprilTag_center_x > 170 and aprilTag_center_x <= 190:
                saveMachineValue = str(tag_id) + ":" + str(moveLength)
                with open(SlideBarDistanceFile, 'a') as file:
                    file.write(str(saveMachineValue))
                    file.write("\r\n")
                if str(tag_id) not in MachinesDistance:
                    MachinesDistance[str(tag_id)] = str(moveLength)
                    target_ip = settings.TestMachine_ips.get(str(tag_id))
                    sendMoveLength = round(moveLength)
                    sendStr = "MachineID:" + \
                        str(tag_id) + ", Location:" + \
                        str(sendMoveLength) + '\n'
                else:
                    print((tag_id, moveLength))
                    MachinesDistance[str(tag_id)] = str(moveLength)
        else:
            moveStepDistance = -10
            needMoveHigh = False
        move_sliderbar.COMM.write(move_sliderbar.continueRun.encode())
    move_sliderbar.serial_close()
    return settings.ScanMachineFinished

def get_Color(colorType):
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        ret, frame = settings.Camera.read()  # 读取一帧
        settings.Camera.set(3, settings.resolutionRatio_Width)
        settings.Camera.set(4, settings.resolutionRatio_Height)
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
    settings.Camera.set(3, settings.resolutionRatio_Width)
    settings.Camera.set(4, settings.resolutionRatio_Height)
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
            cv2.putText(frame, setStr, (x3-w3, y3 + h3),
                        font, 0.3, (255, 255, 0), 1)
            now_f = "KeyboardLayout\\{}\\{}.jpg".format(colorType,time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())))                
            if os.path.exists(now_f):
                os.remove(now_f)
            cv2.imwrite(now_f,frame) #保存图片

    result = (MaxX, MaxY, MaxW, MaxH)
    print('\'{}\' color location {}'.format(colorType,result))
    return result

def get_min_keyboard_rowcol(key_name):
    row = 0
    col = 0
    for keys in settings.min_keyboard:
        col = 0
        for key in keys:
            if key == key_name:
                print((row, col))
                return (row, col)
            col = col + 1
        row = row + 1

    pass

def move_to_key_for_min_keyboard(key_name):
    if str(key_name) == "":
        return
    print("################# Begin Press Min KeyBoard #######################")
    print('Press min keyboard key name is \'{}\''.format(key_name))
    yellow_key_row_col = [2, 0]
    (min_keyboard_row, min_keyboard_col) = get_min_keyboard_rowcol(key_name)
    row_offset = (min_keyboard_row - yellow_key_row_col[0]) * 18
    col_ossfet = (min_keyboard_col - yellow_key_row_col[1]) * 18

    if min_key_location != None:
        print("The Key is {}, Location is : {} ".format(
            key_name, min_key_location))
        print("The center Key is {}".format((green_key_cx, green_key_cy)))
        yellow_key_x, yellow_key_y, yellow_key_w, yellow_key_h = min_key_location
    else:
        return

    if min_keyboard_row == 4:
        row_offset = row_offset + 5

    move_w = 0
    if yellow_key_w != center_Key_w:
        move_w = yellow_key_w - center_Key_w
    else:
        (yellow_key_w)
    offset_x = (yellow_key_x + yellow_key_w/2 - center_Key_x) / ratio
    move_h = 0
    if yellow_key_h != center_Key_h:
        move_h = yellow_key_h - center_Key_h
    else:
        (yellow_key_h)
    offset_y = (yellow_key_y + yellow_key_h/2 - center_Key_y) / ratio

    offset_moveX = green_moveX - offset_y - row_offset
    offset_moveY = green_moveY + offset_x + col_ossfet

    moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    print("The Target Key is {}, Target Move offset: {} ".format(key_name, (offset_moveX, offset_moveY)))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX, offset_moveY, down_green_moveZ]

    print('Click Key location is {}'.format(press_moveCoords_key))
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key, 40)

def move_to_key_for_long_keyboard(key_name, setOffset):
    result = TestPictureFile.GetKeyLocation(key_name, machine_id)
    key_x, key_y, key_w, key_h = result
    center_Key_i, center_Key_j = TestPictureFile.GetRowColByKeyName(center_Key, layoutId)
    target_Key_i = 0
    target_Key_j = 0
    target_key_row_col =  TestPictureFile.GetRowColByKeyName(key_name, layoutId)
    if target_key_row_col != None:
        target_Key_i = target_key_row_col[0]
        target_Key_j = target_key_row_col[1]

    same_row_key_name = TestPictureFile.GetKeyNameRowCol(target_Key_i, center_Key_j, layoutId)
    same_row_result = TestPictureFile.GetKeyLocation(same_row_key_name, machine_id)

    global green_moveX
    global green_moveY
    global haveMoveSlider

    print("################# Step Final #######################")
    if result != None:
        print("The Key is {}, Location is : {} ".format(key_name, result))
        print("The center Key is {}".format((green_key_cx, green_key_cy)))
    else:
        return
    if setOffset:
        move_w = 0
        if key_w != center_Key_w:
            move_w = key_w - center_Key_w
        else:
            (key_w)
        #long keyboard
        offset_x = (key_x - center_Key_x) / ratio
        # pc
        #offset_x = ((key_x) - (center_Key_x)) / ratio + move_w/2 / ratio
        if target_Key_j > center_Key_j + 1:
            offset_x = offset_x + key_w/3/ratio
        move_h = 0
        if key_h != center_Key_h:
            move_h = key_h - center_Key_h
        else:
            (key_h)
        offset_y = (key_y - center_Key_y) / ratio + move_h/2 / ratio

    else:
        offset_x = 0
        offset_y = 0

    offset_moveX = green_moveX - offset_y
    offset_moveY = round(green_moveY + offset_x,2)
    compensate = 0
    #if target_Key_i < center_Key_i:
    compensate_x = (key_x - same_row_result[0])/200 * 3
    offset_moveX = round(offset_moveX - compensate_x,2)
    if target_Key_i == 5 and target_Key_j < 4:
        offset_moveY = offset_moveY - 5

    moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
    result = math.sqrt(offset_moveX**2+offset_moveY**2+down_green_moveZ**2)
    if result > 340 :
        offset_moveY = offset_moveY + 3
        offset_moveX = offset_moveX - 3
        moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
    if offset_moveX < 186 : #and machine_id == '91'
        offset_moveX = 186.5
        if offset_moveY > 20:
            offset_moveX = 184
        moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
        radians_info = settings.SmartArm.get_radians_info()
        getanglesinfo = settings.SmartArm.get_angles_info()
        print(" 获取机械臂当前角度 Get Angles info {} ".format(getanglesinfo))
        print(" 获取机械臂当前弧度值 Get Radians info {}".format(radians_info))
        print(" 获取限位开关状态 Get Switch State {}".format(settings.SmartArm.get_switch_state()))

    if target_Key_i > 3:
        settings.SmartArm.set_coords(moveCoords_key)
    else:
        settings.SmartArm.set_coords(moveCoords_key,75)

    print("The Target Key is {}, Target Move : {} ".format(key_name, moveCoords_key))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX, offset_moveY, down_green_moveZ]
    print('The Target Key click location is {} '.format(press_moveCoords_key))
    settings.SmartArm.set_coords(press_moveCoords_key)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key)

def move_to_key(key_name, setOffset):
    result = TestPictureFile.GetKeyLocation(key_name, machine_id)
    global green_moveX
    global green_moveY
    global haveMoveSlider

    if result != None:
        key_x, key_y, key_w, key_h = result
        print("The Key is {}, Location is {}".format(key_name, result))
    else:
        return
    if setOffset:
        move_w = 0
        if key_w != center_Key_w:
            move_w = key_w - center_Key_w
        else:
            print(key_w)
        offset_x = ((key_x+key_w/2) - (center_Key_x)) / ratio
        move_h = 0
        if key_h != center_Key_h:
            move_h = key_h - center_Key_h
        else:
            print(key_h)
        offset_y = ((key_y-key_h/2) - (center_Key_y)) / ratio
    else:
        offset_x = 0
        offset_y = 0
    #print("Key offset {}".format((offset_x,offset_y)))
    offset_moveX = green_moveX - offset_y
    offset_moveY = green_moveY + offset_x
    moveCoords_key = [offset_moveX, offset_moveY, -30]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    print("The Second The Key is {}, Target Move offset: {} ".format(
        key_name, (offset_moveX, offset_moveY)))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX, offset_moveY, down_green_moveZ]
    print('Click Key location is'.format((press_moveCoords_key)))
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key, 40)

def MoveRobotByCode():
    move_zero.GoToZero()
    if settings.SmartArm == None:
        settings.SmartArm = ultraArm(move_zero.getDeviceName(), 115200)
        settings.SmartArm.set_coords(ZERO, 60)
        time.sleep(1.5)
    allAprilTag = GetAllAprilTag()
    left_tag = GetAprilTag(allAprilTag, 586)
    right_tag = GetAprilTag(allAprilTag, 90)
    ratio = abs((left_tag.center[0]-right_tag.center[0])/170)
    coords = settings.SmartArm.get_coords_info()
    posx = (right_tag.center[0] - c_x) / ratio
    posy = (right_tag.center[1] - c_y) / ratio

    if coords:
        green_moveX = coords[0] - posy
        green_moveY = coords[1] + posx
    befor_distance = get_distance_byport.GetCurrentDistance()
    print('Before move distance {}'.format(befor_distance))
    settings.SmartArm.set_coords([green_moveX, green_moveY, -35], 60)
    time.sleep(1)
    coords = settings.SmartArm.get_coords_info()
    settings.SmartArm.set_coords([green_moveX, green_moveY-30, -35], 60)
    time.sleep(1)

    allAprilTag = GetAllAprilTag()
    left_tag = GetAprilTag(allAprilTag, 586)
    right_tag = GetAprilTag(allAprilTag, 90)

def SetRobotForLongKey():
    target_x = 0
    target_y = 0
    global move_down_distance
    if settings.SmartArm == None:
        deviceName = move_zero.getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    time.sleep(1.5)
    print('Set Green X Location: ')
    preTargetY = 0
    for i in range(0, 15):
        result = get_Color('Green')
        x, y, w, h, ratio = result
        #need_move_y = preY - y
        if y <= 320:
            target_y = -3
        elif y >= 340:
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
        settings.SmartArm.set_coords(move_location, 60)
        time.sleep(1.5)
        # current_distance = get_distance_byport.GetCurrentDistance()
        # if int(current_distance) < int(move_down_distance):
        #     move_down_distance = int(current_distance)
        # print(current_distance)

    print('Set Green Y Location: ')
    for i in range(0, 15):
        result = get_Color('Green')
        x, y, w, h, ratio = result
        if x < 840:
            target_x = 3
        elif x > 860:
            target_x = -3
        else:
            target_x = 0
            break

        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0], coords[1]-target_x, coords[2], coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)

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

    min_x = 900
    max_x = 930
    min_y = 0
    max_y = 20
    if long_keyboard_flag == True:
        min_x = 850
        max_x = 870
    print('Set Green Y Location: ')
    for i in range(0, 25):
        result = get_Color('Green')
        #get_Color("Red")
        x, y, w, h = result
        if x <= min_x:
            target_x = 3
            haveMoveLeft = haveMoveLeft + 1
            if haveMoveRight > 2:
                break
        elif x > max_x:
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
        #get_Color("Red")
        x, y, w, h = result
        if y < 20:
            break
        if y < min_y:
            target_y = -3
        elif y > max_y:
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

def PressKey(keyName,SaveLocation = False):
    global resultMsg
    try:
        if settings.SmartArm == None:
            settings.SmartArm = ultraArm(move_zero.getDeviceName(), 115200)
            settings.SmartArm.set_coords(ZERO)
            time.sleep(1.5)
    except:
        resultMsg = 'Smart Arm Set to Zero failed'
        return False
    coords = settings.SmartArm.get_coords_info()
    print(coords)
    # step 1, get april tag
    time.sleep(3)
    keyId = 0
    # step 2, calculate the ratio
    layoutId = settings.Machine_Code_Dic.get(machine_id)
    center_Key = settings.Machines_center.get(machine_id)
    center_Key_location = RedisManage.GetKeyLocationFromRedis(PlanId,deviceName,center_Key)
    
    if center_Key_location == None:
        if layoutId == None:
            layoutId = machine_id
        min_key_location = None
        long_keyboard_flag = False
        if int(machine_id) >= 90:
            min_key_location = get_Color('Yellow')
            long_keyboard_flag = True
        allAprilTag = GetAllAprilTag()
        left_tag = GetAprilTag(allAprilTag, 586)
        right_tag = GetAprilTag(allAprilTag, machine_id)
        machine_AprilTag_Len = settings.machine_len.get(machine_id)
        ratio = abs((left_tag.center[0]-right_tag.center[0])/machine_AprilTag_Len)
        (Green_MaxX, Green_MaxY, Green_MaxW,Green_MaxH) = get_Color('Green')
        green_key_cx = Green_MaxX + Green_MaxW/2
        green_key_cy = Green_MaxY - Green_MaxH/2
        posx = (green_key_cx - c_x) / ratio
        posy = (green_key_cy - c_y) / ratio
        print("key_cx = {}, key_cy = {}".format(green_key_cx, green_key_cy))
        if coords:
            green_moveX = coords[0] - posy
            green_moveY = coords[1] + posx
        before_distance = get_distance_byport.GetCurrentDistance()
        print('Machine id {}, Before move distance {}'.format(machine_id ,before_distance))
        before_move_down = 130 - (before_distance - settings.end_high_distance)
        settings.SmartArm.set_coords([green_moveX-settings.end_up_distance,green_moveY-settings.end_left_distance, before_move_down], 60)
        time.sleep(1)
        before_move_down = before_move_down + 16
        SetRobotForCutLongKey()
        time.sleep(2)
        #current_distance = get_distance_byport.GetCurrentDistance()
        coords = settings.SmartArm.get_coords_info()
        green_moveX = coords[0]
        green_moveY = coords[1]
        press_key_distance = get_distance_byport.GetCurrentDistance()
        print('Press key distance {}'.format(press_key_distance))
        green_moveZ = coords[2]
        down_green_moveZ = green_moveZ - (press_key_distance - settings.Offset_Z) - 5
        center_press_moveCoords_key = [green_moveX, green_moveY, down_green_moveZ]
        print('Press key: {}'.format(center_press_moveCoords_key))
    else:
        center_press_moveCoords_key = [center_Key_location[0], center_Key_location[1], center_Key_location[2]]
    #settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    target_Key_location = RedisManage.GetKeyLocationFromRedis(PlanId,deviceName,keyName)
    if target_Key_location != None:
        moveCoords_key = [target_Key_location[0],target_Key_location[1],float(target_Key_location[2]) + 10]
        if SaveLocation == False:
            settings.SmartArm.set_coords(moveCoords_key,70)
            settings.SmartArm.set_coords(target_Key_location,70)
            time.sleep(0.1)
            moveCoords_key = [target_Key_location[0],target_Key_location[1],float(target_Key_location[2]) + 10]
        #if SaveLocation:
            settings.SmartArm.set_coords(moveCoords_key,70)
            time.sleep(0.5)
            settings.SmartArm.set_coords(ZERO, 40)
        return 'Press {} Successful'.format(keyName)
    
    if SaveLocation:
        moveCoords_key = [green_moveX, green_moveY, before_move_down]
        settings.SmartArm.set_coords(moveCoords_key, 40)
    
    center_Key_x, center_Key_y, center_Key_w, center_Key_h = Green_MaxX, Green_MaxY, Green_MaxW, Green_MaxH
    TestPictureFile.machineIndex = machine_id
    #sendKeys = ['SPACE','ALT_R','WIN_R','Wight','CTRL_R']
    #sendKeys = TestPictureFile.GetAllKeysLocation()
    #for key in sendKeys:
    #move_to_key_for_long_keyboard(keyName,True)
    result = TestPictureFile.GetKeyLocation(keyName, machine_id)
    key_x, key_y, key_w, key_h = result
    center_Key_i, center_Key_j = TestPictureFile.GetRowColByKeyName(center_Key, layoutId)
    target_Key_i = 0
    target_Key_j = 0
    target_key_row_col =  TestPictureFile.GetRowColByKeyName(keyName, layoutId)
    if target_key_row_col != None:
        target_Key_i = target_key_row_col[0]
        target_Key_j = target_key_row_col[1]

    same_row_key_name = TestPictureFile.GetKeyNameRowCol(target_Key_i, center_Key_j, layoutId)
    same_row_result = TestPictureFile.GetKeyLocation(same_row_key_name, machine_id)

    # global green_moveX
    # global green_moveY
    global haveMoveSlider

    print("################# Step Final #######################")
    if result != None:
        print("The Key is {}, Location is : {} ".format(keyName, result))
        print("The center Key is {}".format((green_key_cx, green_key_cy)))
    else:
        return
    setOffset = True
    if setOffset:
        move_w = 0
        if key_w != center_Key_w:
            move_w = key_w - center_Key_w
        else:
            (key_w)
        #long keyboard
        offset_x = (key_x - center_Key_x) / ratio
        # pc
        #offset_x = ((key_x) - (center_Key_x)) / ratio + move_w/2 / ratio
        if target_Key_j > center_Key_j + 1:
            offset_x = offset_x + key_w/3/ratio
        move_h = 0
        if key_h != center_Key_h:
            move_h = key_h - center_Key_h
        else:
            (key_h)
        offset_y = (key_y - center_Key_y) / ratio + move_h/2 / ratio

    else:
        offset_x = 0
        offset_y = 0

    offset_moveX = green_moveX - offset_y
    offset_moveY = round(green_moveY + offset_x,2)
    compensate = 0
    #if target_Key_i < center_Key_i:
    compensate_x = (key_x - same_row_result[0])/200 * 3
    offset_moveX = round(offset_moveX - compensate_x,2)
    if target_Key_i == 5 and target_Key_j < 4:
        offset_moveY = offset_moveY - 5

    moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
    result = math.sqrt(offset_moveX**2+offset_moveY**2+down_green_moveZ**2)
    if result > 340 :
        offset_moveY = offset_moveY + 3
        offset_moveX = offset_moveX - 3
        moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
    if offset_moveX < 186 : #and machine_id == '91'
        offset_moveX = 186.5
        if offset_moveY > 20:
            offset_moveX = 184
        moveCoords_key = [offset_moveX, offset_moveY, before_move_down]
        radians_info = settings.SmartArm.get_radians_info()
        getanglesinfo = settings.SmartArm.get_angles_info()
        print(" 获取机械臂当前角度 Get Angles info {} ".format(getanglesinfo))
        print(" 获取机械臂当前弧度值 Get Radians info {}".format(radians_info))
        print(" 获取限位开关状态 Get Switch State {}".format(settings.SmartArm.get_switch_state()))
    

    if SaveLocation != True:
        if target_Key_i > 3:
            settings.SmartArm.set_coords(moveCoords_key)
        else:
            settings.SmartArm.set_coords(moveCoords_key,75)
        print("The Target Key is {}, Target Move : {} ".format(keyName, moveCoords_key))
        time.sleep(2)
        press_moveCoords_key = [offset_moveX, offset_moveY, down_green_moveZ]
        print('The Target Key click location is {} '.format(press_moveCoords_key))
        settings.SmartArm.set_coords(press_moveCoords_key)
        time.sleep(0.1)
        settings.SmartArm.set_coords(moveCoords_key)
    # if int(machine_id) >= 90: 
    #     for keys in settings.min_keyboard:
    #         min_keyboard_col = 0
    #         for key_name in keys:
    #             move_to_key_for_min_keyboard(key_name)
    if SaveLocation:
        pool = redis.ConnectionPool(host='10.119.96.35',port=6379,password='',db=4)  
        #实现一个连接池
        r = redis.Redis(connection_pool=pool)
        setCenterValue = PlanId+":"+deviceName+":"+center_Key
        json_data = json.dumps(center_press_moveCoords_key)
        r.set(setCenterValue, json_data)
        setTargetKeyValue = PlanId+":"+deviceName+":"+keyName
        json_data = json.dumps(press_moveCoords_key)
        r.set(setTargetKeyValue, json_data)
        r.close()
    
    settings.SmartArm.set_coords(ZERO, 40)
    return 'Press {} Successful'.format(keyName)

if __name__ == "__main__":
    print("CSW QA Smart Arm Automation Test!")
    server = socket.socket()
    ip = IP.get_ip_local()
    port = 15555
    server.bind ((ip, port))
    server.listen()
    BUFFER_SIZE = 1024
    down_green_moveZ = 0
    center_Key_x = 0; center_Key_y = 0; center_Key_w = 0; center_Key_h = 0
    center_Key = None
    green_key_cx = 0
    green_key_cy = 0
    PlanId = 0
    ratio = 0
    before_move_down = 0
    long_keyboard_flag = False
    deviceName = ""
    while True:
        conn, addr = server.accept()
        print('Test Machine IP：', addr)
        data = conn.recv(BUFFER_SIZE)
        recvData = str(data,encoding='utf-8')
        move_zero.GoToZero()
        if ',' in recvData:
            deviceName = recvData.split(',')[1]
        if recvData == 'ScanMachines':
            move_zero.GoToZero()
            resultMsg = ScanAllMachines()          
        elif 'GoToMachine' in recvData:
            machine_id = settings.SmartArmMachine.get(deviceName)
            gotoMachineReuslt = True # move_sliderbar.GoToMachineByIndex(machine_id)
            if gotoMachineReuslt == True:
                time.sleep(1)
                #进行图片上传分割
                layoutId = settings.Machine_Code_Dic.get(machine_id)
                if layoutId == None:
                    layoutId = machine_id
                target_path = 'KeyboardLayout\\Keyboard_layout_{}.jpg'.format(str(machine_id))
                sendImageResult = GetKeyboardLocation(machine_id,layoutId)
                if sendImageResult:
                    resultMsg = 'Send Image Result Successful'
                else:
                    resultMsg = 'Send Image Result Failed'               
            elif gotoMachineReuslt == False:
                resultMsg = 'Go To Machine Failed'
        elif 'GetImageLayout' in recvData:
                target_path = 'KeyboardLayout\\Keyboard_layout_{}.jpg'.format(str(machine_id))
                sendImageResult = GetKeyboardLocation(machine_id,layoutId)
                if sendImageResult:
                    resultMsg = 'Send Image Result Successful'
                else:
                    resultMsg = 'Send Image Result Failed'
        elif 'SavePressKeys' in recvData:
            Keys = recvData.split(':')[1].split('#')[0]
            PlanId = recvData.split('#')[1].split(',')[0]
            firstKey = Keys[0]
            machine_id = settings.SmartArmMachine.get(deviceName)
            PressKey(firstKey,True)
        elif 'PressKey' in recvData:
            #"PressKeys:" + p0 + "*" + p1 + "#" + StatisticalData.PlanId + "," + machineName;
            # PressKeys:Fn Q ,SMARTAUTOSECOND
            Keys = recvData.split(':')[1].split('#')[0].split('*')
            PlanId = recvData.split('#')[1].split(',')[0]
            firstKey = Keys[0]
            fingure_displayName = settings.SmartFingureMachine.get(deviceName)
            ManageSmartFingure.PressSmartFingure(fingure_displayName)
            secondKey = Keys[1]
            time.sleep(0.5)
            machine_id = settings.SmartArmMachine.get(deviceName)
            resultMsg = PressKey(secondKey)
            time.sleep(5)
            ManageSmartFingure.ReleaseSmartFingure(fingure_displayName)
            time.sleep(1)
        msg = '{} commd is finished, return message is {} '.format(recvData,resultMsg)
        print(msg)
        conn.send(msg.encode('utf-8'))
        conn.close()