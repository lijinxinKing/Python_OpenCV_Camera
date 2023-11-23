import serial,time,math,os,sys
import serial
import sys,os,cv2,math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Elephantrobotics import settings
import platform
from pymycobot.ultraArm import ultraArm
import serial.tools.list_ports
from Elephantrobotics import recognition_aprilTag,send_data_to_machine
from CutApart import Cut_long_keyboard_move_robot

SlideBarDeviceDes = "Prolific PL2303GT USB Serial COM Port"
deviceName = ''
stopRun = "CJXRp"
continueRun = "CJXRr"
method = "FindEveryPC"
#1400
SlideTotalLength = -1400
CurrentSlideBarDistanceFile = "C:\\CurrentSlideBarDistanceFile.txt"
SlideBarDistanceFile = "C:\\SlideBarDistanceFile.txt"
MachinesDistance  = {}
#setDistance = 10
#cmd = "CJXCGX{}F1000$".format(setDistance)
COMM = None
def getDeviceName():
    global deviceName
    # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if SlideBarDeviceDes in str(com):
            deviceName = com.device

def serial_open():
    global deviceName
    getDeviceName() # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if SlideBarDeviceDes in str(com):
            deviceName = com.device
    global COMM
    serial_port = deviceName
    if COMM == None:
        COMM = serial.Serial(serial_port, 115200, timeout=0.01)
    else:
        print(COMM)
    # if COMM.isOpen():
    #     return 0
    # else:
    #     print("open failed")
    #     return 255
# 关闭串口
def serial_close():
    global COMM
    if COMM != None:
        COMM.close()
    COMM = None

def com_receive():
        try:
            rx_buf = ''
            rx_buf = COMM.read()  # 转化为整型数字
            if rx_buf != b'':
                time.sleep(0.01)
                rx_buf = rx_buf + COMM.read_all()
                return rx_buf.decode("gb2312")
            else:
                return None
        except:
            pass

def MoveSlideByCode(distance):
    serial_open()
    # CJXSA:查询当前坐标,速度等信息
    search_data = "CJXSA"
    COMM.write(search_data.encode())
    time.sleep(0.5)
    data = com_receive()
    if data == None:
        return False
    
    sendStr = "CJXCGX{0}F8000$".format(distance)
    COMM.write(sendStr.encode())
    moveTime = abs(distance / 100) * 2 + 2
    time.sleep(moveTime)
    data = com_receive()
    print(data)
    serial_close()
    time.sleep(0.5)
    return True

def ScanAllMachines():
    currentDistance = 0
    # 判断滑轨是否通电
    serial_close()
    serial_open()
    # CJXSA:查询当前坐标,速度等信息
    search_data = "CJXSA"
    COMM.write(search_data.encode())
    time.sleep(0.5)
    data = com_receive()
    if data == None: #未通电
        return
    serial_close()

    if os.path.exists(CurrentSlideBarDistanceFile):
        with open(CurrentSlideBarDistanceFile) as f:
            content = f.read()    
            currentDistance = content
    distance = 0 - round(float(currentDistance))
    if distance != 0: #归零
        MoveSlideByCode(distance)
    if os.path.exists(CurrentSlideBarDistanceFile):
        os.remove(CurrentSlideBarDistanceFile)
    else:
        print("The file does not exist")
    if os.path.exists(SlideBarDistanceFile):
        os.remove(SlideBarDistanceFile)
    ScanMachine()
    time.sleep(2)

def ScanMachine():
    moveLength = 0
    needMoveHigh = False
    slider_ratio = 2.7
    if COMM == None:
        serial_open()    
    moveStepDistance = -10
    sendPreID = -1
    while abs(moveLength) < abs(SlideTotalLength):
        # => 尝试 先拍一张图片，计算距离，步长二分 
        sendStr = "CJXCGX{}F6000$".format(moveStepDistance)
        COMM.write(sendStr.encode())
        waitTime = abs(moveStepDistance / 15) + 1
        time.sleep(waitTime)
        COMM.write(stopRun.encode())
        moveLength = moveLength + moveStepDistance
        with open(CurrentSlideBarDistanceFile, 'w') as file:
            file.write(str(moveLength))
        moveDirection = -1         
        machineAprilTags = recognition_aprilTag.GetMachineAprilTag()
        machine_id = 0
        willScanMachine = None
        if len(machineAprilTags) > 0:
            aprilTagLocation = machineAprilTags
            for machine in machineAprilTags:
                if MachinesDistance.get(str(machine.tag_id)) == None:
                    willScanMachine = machine
                else:
                    moveStepDistance = -100
                    break
            if willScanMachine != None:
                aprilTag_center_x = round(willScanMachine.center[0]) # x_center
                machine_id = willScanMachine.tag_id
                if int(machine_id) >= 190:
                    slider_ratio = 2.8
                    long_keyboard_flag = True
                    min_keyboard_color = Cut_long_keyboard_move_robot.get_Color("Yellow")
                    if min_keyboard_color != None:
                        min_color_x,min_color_y,min_color_w,min_color_h = min_keyboard_color
                        if willScanMachine.center[0] < min_color_x and abs(willScanMachine.center[1] - min_color_y) < 20:
                            if int(min_color_w) >= 44:
                                print(min_keyboard_color)
                            else:
                                moveStepDistance = -10
                else:
                    print('识别小键盘！！！可以同时识别到两个二维码，判断二维码所在位置')
                    allAprilTag = Cut_long_keyboard_move_robot.GetAllAprilTag()
                    right_tag = Cut_long_keyboard_move_robot.GetAprilTag(allAprilTag, 586)
                    left_tag = Cut_long_keyboard_move_robot.GetAprilTag(allAprilTag, machine_id)
                    if left_tag != None :
                        print('left  tag center x {}'.format(left_tag.center[0]))   
                        if int(machine_id) >= 90:                
                            moveStepDistance = -round((left_tag.center[0]-450) / slider_ratio)
                        else:
                            moveStepDistance = -round((left_tag.center[0]-370) / slider_ratio)
                        print('Move Step Distance: {}'.format(moveStepDistance))
                        if str(machine_id) in MachinesDistance:
                            moveStepDistance = -100
                        elif str(machine_id) not in MachinesDistance:
                            saveMachineValue = str(machine_id) +":" + str(moveLength + moveStepDistance)
                            MachinesDistance[str(machine_id)] = str(moveLength + moveStepDistance)
                            with open(SlideBarDistanceFile, 'a') as file:
                                file.write(str(saveMachineValue))
                                file.write("\r\n")
                        if abs(int(moveStepDistance)) < 18:
                            moveStepDistance = -100
                        willMoveTotalLen = abs(moveStepDistance + moveLength)
                        if willMoveTotalLen > abs(SlideTotalLength):
                            break

                    if right_tag != None :
                        print('right tag center x {}'.format(right_tag.center[0]))

                    if left_tag != None and right_tag != None:
                        print('left tag center x {}'.format(left_tag.center[0]))


        #     return
        #     if aprilTag_center_x > 400:
        #        if str(machine_id) not in MachinesDistance:
        #            moveStepDistance = -10 #(xMove * moveDirection)/2
        #            willMoveTotalLen = abs(moveStepDistance + moveLength)
        #            if willMoveTotalLen >abs(SlideTotalLength):
        #                break
        #     elif aprilTag_center_x < 50:
        #         if str(machine_id) in MachinesDistance:
        #             moveStepDistance = (220 * moveDirection)/2
        #             willMoveTotalLen = abs(moveStepDistance + moveLength)
        #             if willMoveTotalLen > abs(SlideTotalLength):
        #                 break
        #     else:
        #         moveStepDistance = -10
        #     if aprilTag_center_x > 280 and aprilTag_center_x <= 310: # => 不同的layout , 配置不同距离
        #         saveMachineValue = str(machine_id) +":" + str(moveLength)
        #         with open(SlideBarDistanceFile, 'a') as file:
        #             file.write(str(saveMachineValue))
        #             file.write("\r\n")
        #         if str(machine_id) not in MachinesDistance:
        #             MachinesDistance[str(machine_id)] = str(moveLength)
        #             target_ip = settings.TestMachine_ips.get(str(machine_id))
        #             sendMoveLength = round(moveLength)
        #             sendStr = "MachineID:" + str(machine_id) +", Location:" + str(sendMoveLength) +'\n'
        #             send_data_to_machine.SendDataToMachine(str(target_ip),sendStr)
        #         else:
        #             print((machine_id,moveLength))
        #             MachinesDistance[str(machine_id)] = str(moveLength)
        else:
             moveStepDistance = -20
        COMM.write(continueRun.encode()) 
    serial_close()
#扫描机器 从左到右进行扫描

def GoToZero():
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

def GoToMachineByIndex(machineIndex):
    allMachinseLength = []
    currentLength = 0
    targetLength = 0
    machinesLength = {}
    with open(CurrentSlideBarDistanceFile, 'r') as file:
        currentLength = float(file.read())

    with open(SlideBarDistanceFile, 'r') as file:
        allMachinseLength = file.readlines()
    for line in allMachinseLength:
        if line != "" and line != '\n' and line != '\r':
            id,length = line.replace('\n',"").split(":")
            machinesLength[str(id)] = float(length)
       
    if machineIndex in machinesLength:
        targetLength = float(machinesLength[machineIndex]) - currentLength
        if float(targetLength) == 0.0:
            print('The Current Loaction is Target location, donot need move')
            return True
        movesliderResult = MoveSlideByCode(targetLength)
        if movesliderResult:
            currentLength = str(machinesLength[machineIndex])
            with open(CurrentSlideBarDistanceFile, 'w') as file:
                file.write(currentLength)
            print('Move the slide Succeed!')
            return True
        else:
            print('Move the slide Failed!')
            return False
    else:
        print('The Machine {} is not in the List!'.format(machineIndex))
        return False
    
if __name__=='__main__':
    ScanAllMachines()
    #ScanMachine()
    #GoToMachineByIndex('5')