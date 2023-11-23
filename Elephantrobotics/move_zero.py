import time
import platform
from pymycobot.ultraArm import ultraArm
import serial
import serial.tools.list_ports
import time,cv2
import sys,os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location,Get_AprilTag_36h11
from Elephantrobotics import settings,recognition_aprilTag

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
ZERO = [235.55, 18, 130.0, 0.0]
#degrees: a list of coords value(List[float]).
    # x : -260 ~ 300 mm 
    # y : -300 ~ 300 mm 
    # z : -70 ~ 135 mm
#speed : (int) 0-200 mm/s
move_down_distance = 135
comName = 'USB-SERIAL CH340'
deviceName = ''
def getDeviceName():
    global deviceName
    # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if comName in str(com):
            deviceName = com.device
            print('robot com Name {}'.format(deviceName))
    return deviceName

#1280 * 720
def SetRobotForLongKey():
    target_x = 0
    target_y = 0
    global move_down_distance
    if settings.SmartArm == None:
        getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    time.sleep(1.5)
    print('Set Green X Location: ')
    preTargetY = 0
    for i in range(0,15):
        result = get_color_location.getColor()
        x,y,w,h,ratio = result
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
        move_location = [coords[0]-target_y,coords[1],coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location,60)
        time.sleep(1.5)
        # current_distance = get_distance_byport.GetCurrentDistance()
        # if int(current_distance) < int(move_down_distance):
        #     move_down_distance = int(current_distance)
        # print(current_distance)

    print('Set Green Y Location: ')
    for i in range(0,15):
        result = get_color_location.getColor()
        x,y,w,h,ratio = result
        if x < 840:
            target_x = 3
        elif x > 860:
            target_x = -3
        else :
            target_x = 0
            break

        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0],coords[1]-target_x,coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)
        # current_distance = get_distance_byport.GetCurrentDistance()
        # if int(current_distance) < int(move_down_distance):
        #     move_down_distance = int(current_distance)
        # print(current_distance)

def SetRobot():
    target_x = 0
    target_y = 0

    if settings.SmartArm == None:
        getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    
    print('Get Green Location: ')
    for i in range(0,15):
        result = get_color_location.getColor()
        x,y,w,h,ratio = result
        if y <= 180:
            target_y = -3
        elif y >= 220:
            target_y = 3
        else:
            target_y = 0
        target_x = 0
        if target_x == 0 and target_y == 0:
            break
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0]-target_y,coords[1],coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)

    print('Get Green Location: ')
    for i in range(0,15):
        result = get_color_location.getColor()
        x,y,w,h,ratio = result
        if x < 470:
            target_x = 3
        elif x > 500:
            if abs(x-485) < 3:
                target_x = 0
            else:
                target_x = -3
        else :
            target_x = 0
        if target_x == 0 and target_y == 0:
            break
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0],coords[1]-target_x,coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location,60)
        time.sleep(1.5)
        
def SetRobotByAprilTag(tagId):
    target_x = 0
    target_y = 0
    if settings.SmartArm == None:
        getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    
    print('Get AprilTag Location: ')
    for i in range(0,15):
        result = Get_AprilTag_36h11.GetAprilTag36h11(tagId)
        x,y,w,h,ratio = result
        if y <= 180:
            target_y = -3
        elif y >= 220:
            target_y = 3
        else:
            target_y = 0
        target_x = 0
        if target_x == 0 and target_y == 0:
            break
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0]-target_y,coords[1],coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)

    print('Get AprilTag Location: ')
    for i in range(0,15):
        result = Get_AprilTag_36h11.GetAprilTag36h11(tagId)
        x,y,w,h,ratio = result
        if x < 470:
            target_x = 3
        elif x > 500:
            if abs(x-485) < 3:
                target_x = 0
            else:
                target_x = -3
        else :
            target_x = 0
        if target_x == 0 and target_y == 0:
            break
        coords = settings.SmartArm.get_coords_info()
        move_location = [coords[0],coords[1]-target_x,coords[2],coords[3]]
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)

def TryRobot():
    getDeviceName()
    try:
        serial_port = serial.Serial()
        serial_port.port = deviceName
        serial_port.baudrate = 115200
        serial_port.timeout = 0.1
        serial_port.write_timeout = 0.1
        serial_port.rts = True
        serial_port.dtr = True
        if serial_port.is_open:
            serial_port.close()
        serial_port.open()
        # 清空输入缓存
        while serial_port.read():
            pass

        # 清空输出缓存
        serial_port.write(b'')
        GET_CURRENT_COORD_INFO = "M114"
        END = "\r"
        """Try Get current Cartesian coordinate information."""
        command = GET_CURRENT_COORD_INFO + END
        serial_port.write(command.encode())
        serial_port.flush()
        rx_buf = serial_port.read()  # 转化为整型数字
        if rx_buf != b'':
            time.sleep(0.01)
            rx_buf = rx_buf + serial_port.read_all()
            result = rx_buf.decode("gb2312") 
        print(result)
        if result == b'':
            return False
        else:
            return True
    except:
        return False
    #debug(command)

def GoToZero(guiling=True):
    # if TryRobot() == False:
    #     return False
    if settings.SmartArm == None:
        getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
        if guiling:
            settings.SmartArm.go_zero()
        settings.SmartArm.set_coords(ZERO, 40)
    time.sleep(0.5)
        
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
            now_f = "{}.jpg".format(time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())))                
            if os.path.exists(now_f):
                os.remove(now_f)
                cv2.imwrite(now_f,frame) #保存图片

    result = (MaxX, MaxY, MaxW, MaxH)
    print('\'{}\' color location {}'.format(colorType,result))
    return result

def SetRobotForCutLongKey():
    target_x = 0
    target_y = 0
    global move_down_distance
    if settings.SmartArm == None:
        deviceName = getDeviceName()
        settings.SmartArm = ultraArm(deviceName, 115200)
    time.sleep(1.5)

    haveMoveLeft = 0
    haveMoveRight = 0

    print('Set Green Y Location: ')
    for i in range(0, 15):
        result = get_Color('Green')
        get_Color("Red")
        x, y, w, h = result
        if x < 900:
            target_x = 3
            haveMoveLeft = haveMoveLeft + 1
            if haveMoveRight > 2:
                break
        elif x > 930:
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

# J1	-150° ~ +170°
# J2	-20° ~ +90°
# J3	-5° ~ +70°

if __name__=="__main__":
    #SetRobot()
    GoToZero()
    # if settings.SmartArm == None:
    #         getDeviceName()
    #         settings.SmartArm = ultraArm(deviceName, 115200)
    #         settings.SmartArm.set_coords([180.78, 19.69, 2.0])
    # elif platform.system() == "Linux":
    #         settings.SmartArm = ultraArm('/dev/ttyUSB0', 115200)
    #         settings.SmartArm.go_zero()
    # time.sleep(0.5)
    # radians_info = settings.SmartArm.get_radians_info()
    # getanglesinfo = settings.SmartArm.get_angles_info()
    # print(getanglesinfo)
    # print(radians_info)
    # print(settings.SmartArm.get_switch_state())
    # time.sleep(0.5)
    # result = settings.SmartArm.get_coords_info()
    # settings.SmartArm.set_coords([result[0], -120, -35])
