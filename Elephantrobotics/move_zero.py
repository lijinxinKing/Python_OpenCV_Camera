import time
import platform
from pymycobot.ultraArm import ultraArm
import serial
import serial.tools.list_ports
import time,cv2
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from Elephantrobotics import settings

#degrees: a list of coords value(List[float]).
    # x : -260 ~ 300 mm 
    # y : -300 ~ 300 mm 
    # z : -70 ~ 135 mm
#speed : (int) 0-200 mm/s
comName = 'USB-SERIAL CH340'
deviceName = ''
def getDeviceName():
    global deviceName
    # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if comName in str(com):
            deviceName = com.device

# 自动选择系统并连接机械臂
def move_zero():
    getDeviceName()
    if platform.system() == "Windows": 
        ua = ultraArm(deviceName, 115200)
        ua.go_zero()
        time.sleep(2)
        ZERO = [235.55, 14, 130.0, 0.0]
        ua.set_coords(ZERO, 40)

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
        settings.SmartArm.set_coords(move_location)
        time.sleep(1.5)
        
if __name__=="__main__":
    #SetRobot()
    move_zero()