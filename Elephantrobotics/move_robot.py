import time
import platform
from pymycobot.ultraArm import ultraArm
import serial
import serial.tools.list_ports
import sys,os,cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from CameraLocationTest import TestPictureFile
from Elephantrobotics import TestRandom,move_sliderbar,move_zero,settings
from Elephantrobotics import send_data_to_machine
import recognition_aprilTag
from CameraLocationTest import TestServer
#print(move_sliderbar.GoToMachineByIndex("6"))
#degrees: a list of coords value(List[float]).
    # x : -260 ~ 300 mm
    # y : -300 ~ 300 mm 
    # z : -70 ~ 135 mm
#speed : (int) 0-200 mm/s
comName = 'USB-SERIAL CH340'
deviceName = ''
key_x = 0
key_y = 0
moveX = 0
moveY = 0
def GetXY():
    result = False
    for i in range(0,5):
        result = get_color_location.getColor()
        if result :
            global key_x
            global key_y
            (key_x,key_y,w,h,ratio_pic) = result
            key_cx = key_x + w/2 
            key_cy = key_y + h/2
            posx = (key_cx - c_x) / ratio_pic
            posy = (key_cy - c_y) / ratio_pic
            return (posx,posy)
    if result == False:
        print("Failed")
      
def move_to_key(key_name,setOffset):
    result = TestPictureFile.GetKeyLocation(key_name,machine_id)
    global moveX
    global moveY

    if result != None:
        key_x,key_y,key_w,key_h = result
        print(result)
    else:
        return
    if setOffset :
        move_w = 0
        if key_w != h_w:
            move_w = key_w - h_w
        offset_x = ((key_x) - (h_x)) / ratio + move_w/2 / ratio
        move_h = 0
        if key_h != h_h:
            move_h = key_h - h_h
        offset_y = ((key_y) - (h_y)) / ratio - move_h/2 / ratio
    else:
        offset_x = 0
        offset_y = 0
    #print("Key offset {}".format((offset_x,offset_y)))
    offset_moveX = moveX - offset_y
    offset_moveY = moveY + offset_x
    moveCoords_key = [offset_moveX,offset_moveY,-70]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    #print("Set {} Key Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX,offset_moveY,-85]
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key, 40)

def getDeviceName():
    global deviceName
    # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if comName in str(com):
            deviceName = com.device

machine_id = "6"
if __name__=="__main__":
    #move_sliderbar.ScanAllMachines()
    for machine_id in ["5"]:
        time.sleep(2)   
        move_sliderbar.GoToMachineByIndex(machine_id)
        if settings.Camera == None:
            settings.Camera = cv2.VideoCapture(1)  # 打开USB摄像头
        # 自动选择系统并连接机械臂
        if platform.system() == "Windows":
            if settings.SmartArm == None:
                getDeviceName()
                settings.SmartArm = ultraArm(deviceName, 115200)
                settings.SmartArm.go_zero()
                ZERO = [235.55, 14, 130.0, 0.0]
                settings.SmartArm.set_coords(ZERO, 40)
        elif platform.system() == "Linux":
            settings.SmartArm = ultraArm('/dev/ttyUSB0', 115200)
            settings.SmartArm.go_zero()
        time.sleep(0.5)

        coords = settings.SmartArm.get_coords_info()
        time.sleep(0.5)
        print(coords)

        c_x = 320
        c_y = 240
        key_offset = 0
        PictureData  = ''
        caprial = recognition_aprilTag.GetCalibration()
        #machineIndex = caprial[0].tag_id
        machine_code = settings.Machine_Code_Dic.get(machine_id)
        #TestServer.GetMachineIndex(machine_id, machine_code)
        h_x,h_y,h_w,h_h = TestPictureFile.GetKeyLocation("h",machine_id)
        print("Get Calibration {} ".format((caprial[0].center[0],caprial[1].center[0])))
        ratio = abs((caprial[1].center[0]-caprial[0].center[0])/180)
        print('The ratio is :' + str(ratio))
        posx,posy = GetXY()
        if coords:
            moveX = coords[0] - posy
            moveY = coords[1] - posx
        settings.SmartArm.set_coords([moveX,moveY,-70], 80)
        time.sleep(3)
        coords = settings.SmartArm.get_coords_info()
        print("Before Set Robot the coords is :")
        print(coords)
        move_zero.SetRobot()
        time.sleep(0.5)
        coords = settings.SmartArm.get_coords_info()
        moveX = coords[0]
        moveY = coords[1]
        move_to_key("h", False)
        coords = settings.SmartArm.get_coords_info()
        moveX = coords[0]
        moveY = coords[1]

        print("Color Target Move: {} ".format((moveX,moveY)))
        typeStr = TestRandom.GetRandomWorld().lower()
        ip = settings.TestMachine_ips.get(machine_id)
        send_data_to_machine.SendDataToMachine(ip,"Will Press: \'" +typeStr +"\'")
        time.sleep(0.5)
        print(typeStr)
        for key in typeStr:
            if " " == key:
                key = "[SPACE]"
            move_to_key(key,True)
        move_to_key("[ENTER]",True)

        time.sleep(2)
        ZERO = [235.55, 14, 130.0, 0.0]
        settings.SmartArm.set_coords(ZERO, 40) 
        time.sleep(10)
    print("CSW QA Smart Arm Automation Test!")
