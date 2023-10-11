import serial,time,math,os,sys
import serial,settings
import serial.tools.list_ports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Elephantrobotics import recognition_aprilTag,send_data_to_machine

SlideBarDeviceDes = "Prolific PL2303GT USB Serial COM Port"
deviceName = ''
stopRun = "CJXRp"
continueRun = "CJXRr"
method = "FindEveryPC"
#1400
SlideTotalLength = -1050
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
    COMM = serial.Serial(serial_port, 115200, timeout=0.01)
    if COMM.isOpen():
        return 0
    else:
        print("open failed")
        return 255
# 关闭串口
def serial_close():
    global COMM
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
    sendStr = "CJXCGX{0}F8000$".format(distance)
    COMM.write(sendStr.encode())
    moveTime = abs(distance / 100) * 2 + 2
    time.sleep(moveTime)
    data = com_receive()
    print(data)
    serial_close()
    time.sleep(0.5)
    return None

def ScanAllMachines():
    currentDistance = 0
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
    if COMM == None:
        serial_open()    
    moveStepDistance = -10
    sendPreID = -1
    while abs(moveLength) < abs(SlideTotalLength):
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
        if len(machineAprilTags) > 0:
            aprilTagLocation = machineAprilTags
            aprilTag_center_x = round(aprilTagLocation[0].center[0]) # x_center
            tag_id = aprilTagLocation[0].tag_id
            if aprilTag_center_x > 400:
               if str(tag_id) not in MachinesDistance:
                   xMove = aprilTag_center_x - 220
                   moveStepDistance = -10 #(xMove * moveDirection)/2
                   willMoveTotalLen = abs(moveStepDistance + moveLength)
                   if willMoveTotalLen >abs(SlideTotalLength):
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
                saveMachineValue = str(tag_id) +":" + str(moveLength)
                with open(SlideBarDistanceFile, 'a') as file:
                    file.write(str(saveMachineValue))
                    file.write("\r\n")
                if str(tag_id) not in MachinesDistance:
                    MachinesDistance[str(tag_id)] = str(moveLength)
                    target_ip = settings.TestMachine_ips.get(str(tag_id))
                    sendMoveLength = round(moveLength)
                    sendStr = "MachineID:" + str(tag_id) +", Location:" + str(sendMoveLength) +'\n'
                    send_data_to_machine.SendDataToMachine(str(target_ip),sendStr)
                else:
                    print((tag_id,moveLength))
                    MachinesDistance[str(tag_id)] = str(moveLength)
        else:
            moveStepDistance = -10
            needMoveHigh = False
        COMM.write(continueRun.encode()) 
    serial_close()
#扫描机器 从左到右进行扫描

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
            return
        MoveSlideByCode(targetLength)
        currentLength = str(machinesLength[machineIndex])
        with open(CurrentSlideBarDistanceFile, 'w') as file:
            file.write(currentLength)
        return targetLength
    
if __name__=='__main__':
    ScanAllMachines()
