import time
import platform
from pymycobot.ultraArm import ultraArm
import serial
import serial.tools.list_ports
import sys,os,cv2,redis,uuid,base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from CameraLocationTest import TestPictureFile
from Elephantrobotics import TestRandom,move_sliderbar,move_zero,settings
from Elephantrobotics import send_data_to_machine
import recognition_aprilTag
from CameraLocationTest import TestServer
from PIL import Image
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
        print("The Key is {}, Location is {}".format(key_name,result))
    else:
        return
    if setOffset :
        move_w = 0
        if key_w != h_w:
            move_w = key_w - h_w
        else:
            print(key_w)
        offset_x = ((key_x) - (h_x)) / ratio + move_w/2 / ratio
        move_h = 0
        if key_h != h_h:
            move_h = key_h - h_h
        else:
            print(key_h)
        offset_y = ((key_y) - (h_y)) / ratio - move_h/2 / ratio
    else:
        offset_x = 0
        offset_y = 0
    #print("Key offset {}".format((offset_x,offset_y)))
    offset_moveX = moveX - offset_y
    offset_moveY = moveY + offset_x
    moveCoords_key = [offset_moveX,offset_moveY,-70]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    print("The Key is  {}, Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
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

def compare_images(image1_path, image2_path):
    # 打开两张图片
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    
    # 比较图片尺寸
    if image1.size != image2.size:
        return False
    
    # 比较每个像素的值
    for i in range(image1.width):
        for j in range(image1.height):
            pixel1 = image1.getpixel((i, j))
            pixel2 = image2.getpixel((i, j))
            
            # 比较每个通道的像素值
            for k in range(len(pixel1)):
                if pixel1[k] != pixel2[k]:
                    return False
    return True

def GetMachineIndex(machineIndex,keyboardCode):
    global taskUUID
    frame = None
    for i in range(0,5):
        if settings.Camera == None:
            settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)       
            ret, frame = settings.Camera.read()  # 读取一帧
        else:
            ret, frame = settings.Camera.read()
            if ret == False:
                settings.Camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)       
                ret, frame = settings.Camera.read()  # 读取一帧
                if ret != False:
                    break

    cv2.imwrite(target_path, frame) # 保存按下空格键时摄像头视频中的图像 
       
    
    # if os.path.exists(target_path) and os.path.exists(new_target_path):
    #     result = compare_images(target_path, new_target_path)
    #     if result:
    #         return
    #     else:
    #         os.remove(target_path)

    pool = redis.ConnectionPool(host='10.119.96.35',port=6379,password='',db=1)  
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
        r.set(str(taskUUID)+":1",str(data_1))
        r.set(str(taskUUID)+":2",str(data_2))
        r.set(str(taskUUID)+":code",keyboardCode)
    finished = []
    jsonFileName = "data_{}_temp.json".format(machineIndex)
    while True:
        finished = r.get(str(taskUUID)+":Finished")
        if finished != None:
            iamgeResult = finished.decode("utf-8")
            with open(jsonFileName,"w") as file:
                file.write(iamgeResult)
            print("Get Location Task to redis Finished!")
            break
        else:
            time.sleep(5)

machine_id = "6"
if __name__=="__main__":
    #move_sliderbar.ScanAllMachines()
    for machine_id in ["5"]:
        #move_sliderbar.GoToMachineByIndex(machine_id)
        time.sleep(1)
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

        target_path = 'Temp_{}.jpg'.format(str(machine_id))
        new_target_path =  'Temp_{}_1.jpg'.format(str(machine_id))

        caprial = recognition_aprilTag.GetCalibration()
        #machineIndex = caprial[0].tag_id
        machine_code = settings.Machine_Code_Dic.get(machine_id)
        #GetMachineIndex(machine_id, machine_code)
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
        #move_to_key("h", False)

        print("Color Target Move: {} ".format((moveX,moveY)))
        
        typeStr = TestRandom.GetRandomWorld().lower()

        #ip = settings.TestMachine_ips.get(machine_id)
        #send_data_to_machine.SendDataToMachine(ip,"Will Press: \'" +typeStr +"\'")
        # time.sleep(0.5)
        # for key in TestPictureFile.GetAllKeysLocation():
        #     move_to_key(key,True)

        # print(typeStr)
        # ip = settings.TestMachine_ips.get(machine_id)
        # send_data_to_machine.SendDataToMachine(ip,"Will press random str: \'" +typeStr +"\'")
        # for key in typeStr:
        #     if " " == key:
        #         key = "[SPACE]"
        #     move_to_key(key,True)
        move_to_key("[ESC]",True)

        time.sleep(2)
        ZERO = [235.55, 14, 130.0, 0.0]
        settings.SmartArm.set_coords(ZERO, 40) 
        time.sleep(10)
    print("CSW QA Smart Arm Automation Test!")
