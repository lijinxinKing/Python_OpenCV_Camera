
import time
import platform
from pymycobot.ultraArm import ultraArm
import serial
import pupil_apriltags as apriltag
import serial.tools.list_ports
import sys,os,cv2
import redis,uuid,base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Elephantrobotics import move_zero
from Elephantrobotics import settings,move_sliderbar,recognition_aprilTag,TestRandom,move_robot
from GetCameraData import get_color_location
from CameraLocationTest import TestPictureFile
from GetDistance import get_distance_byport
c_x = settings.resolutionRatio_Width/2
c_y = settings.resolutionRatio_Height/2

key_cx = 0
key_cy = 0

CurrentSlideBarDistanceFile = "C:\\CurrentSlideBarDistanceFile.txt"
SlideBarDistanceFile = "C:\\SlideBarDistanceFile.txt"
SlideTotalLength = 500
green_moveX = 0
green_moveY = 0
move_down = 0

def GetAprilTag(allAprilTag:[],tag_id):
    for tag in allAprilTag:
        if tag.tag_id == tag_id:
            return tag

def GetAllAprilTag():
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    settings.Camera.set(3,settings.resolutionRatio_Width) #设置分辨率
    settings.Camera.set(4,settings.resolutionRatio_Height)
    checkTinmes:int = 5
    maxLen = -1
    allAprilTags = []
 
    flag = settings.Camera.isOpened()
    while flag and checkTinmes >0:
        ret, frame = settings.Camera.read()
        img = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        at_detector = apriltag.Detector(families='tag36h11') 
        tags = at_detector.detect(gray)
        print("%d apriltags have been detected."%len(tags))
        if len(tags) > maxLen:
            maxLen = len(tags)
            allAprilTags = []
            for tag in tags:
                cv2.circle(img, tuple(tag.corners[0].astype(int)), 4,(255,0,0), 1) # left-top
                cv2.circle(img, tuple(tag.corners[1].astype(int)), 4,(255,0,0), 1) # right-top
                cv2.circle(img, tuple(tag.corners[2].astype(int)), 4,(255,0,0), 1) # right-bottom
                cv2.circle(img, tuple(tag.corners[3].astype(int)), 4,(255,0,0), 1) # left-bottom
                a = (tuple(tag.corners[3].astype(int))[0], tuple(tag.corners[3].astype(int))[1])
                cv2.putText(img, str(tag.tag_id)+","+str(tag.center), (a[0]-100, a[1]- 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                allAprilTags.append(tag)
        checkTinmes = checkTinmes - 1
        cv2.waitKey(1000)
    return allAprilTags


def GetAprilTagByID(tagID):
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    settings.Camera.set(3,settings.resolutionRatio_Width) #设置分辨率
    settings.Camera.set(4,settings.resolutionRatio_Height)
    checkTinmes:int = 10
    maxLen = -1
    allAprilTags = []
 
    flag = settings.Camera.isOpened()
    while flag and checkTinmes >0:
        ret, frame = settings.Camera.read()
        img = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        at_detector = apriltag.Detector(families='tag36h11') 
        tags = at_detector.detect(gray)
        print("%d apriltags have been detected."%len(tags))
        if len(tags) > maxLen:
            maxLen = len(tags)
            allAprilTags = []
            for tag in tags:
                cv2.circle(img, tuple(tag.corners[0].astype(int)), 4,(255,0,0), 1) # left-top
                cv2.circle(img, tuple(tag.corners[1].astype(int)), 4,(255,0,0), 1) # right-top
                cv2.circle(img, tuple(tag.corners[2].astype(int)), 4,(255,0,0), 1) # right-bottom
                cv2.circle(img, tuple(tag.corners[3].astype(int)), 4,(255,0,0), 1) # left-bottom
                a = (tuple(tag.corners[3].astype(int))[0], tuple(tag.corners[3].astype(int))[1])
                cv2.putText(img, str(tag.tag_id)+","+str(tag.center), (a[0]-100, a[1]- 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                if tag.tag_id == tagID:
                    allAprilTags.append(tag)
        checkTinmes = checkTinmes - 1
        cv2.waitKey(1000)
    return allAprilTags

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

def ClickTagKey(target_tag,moveX,moveY,tagID=None):
    if target_tag != None:
        target_x = target_tag.corners[0][0]
        target_y = target_tag.center[1]
        print(target_tag)

        offset_x = (target_x - key_cx) / ratio
        offset_y = (target_y - key_cy) / ratio 

        offset_moveX = moveX - offset_y
        offset_moveY = moveY + offset_x
        moveCoords_key = [offset_moveX,offset_moveY,-66]
        settings.SmartArm.set_coords(moveCoords_key, 85)
        print("The Key is  {}, Target Move offset: {} ".format(target_tag.tag_id,(offset_moveX,offset_moveY)))
        press_moveCoords_key = [offset_moveX,offset_moveY,-85]
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
    if distance != 0: #归零
        move_sliderbar.MoveSlideByCode(distance)
    if os.path.exists(CurrentSlideBarDistanceFile):
        os.remove(CurrentSlideBarDistanceFile)
    else:
        print("The file does not exist")
    if os.path.exists(SlideBarDistanceFile):
        os.remove(SlideBarDistanceFile)

    moveLength = 0
    needMoveHigh = False
    MachinesDistance  = {}
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
                else:
                    print((tag_id,moveLength))
                    MachinesDistance[str(tag_id)] = str(moveLength)
        else:
            moveStepDistance = -10
            needMoveHigh = False
        move_sliderbar.COMM.write(move_sliderbar.continueRun.encode()) 
    move_sliderbar.serial_close()

haveMoveSlider = False

def move_to_key_for_long_keyboard(key_name,setOffset):
    result = TestPictureFile.GetKeyLocation(key_name,machine_id)
    # print(result)
    key_x,key_y,key_w,key_h = result
    center_Key_i,center_Key_j = TestPictureFile.GetRowColByKeyName(center_Key,machine_id)   
    target_Key_i,target_Key_j = TestPictureFile.GetRowColByKeyName(key_name,machine_id)
    same_row_key_name = TestPictureFile.GetKeyNameRowCol(target_Key_i,center_Key_j,machine_id)
    same_row_result = TestPictureFile.GetKeyLocation(same_row_key_name,machine_id)
    print('the same row result {}'.format(same_row_result))
   

    global green_moveX
    global green_moveY
    global haveMoveSlider

    # step 1
    if result != None:    
        print("The Key is {}, Location is : {} ".format(key_name,result))
        print("The center Key is {}".format((green_key_cx,green_key_cy)))
    else:
        return
    if setOffset :
        move_w = 0
        if key_w != center_Key_w:
            move_w = key_w - center_Key_w
        else:
            (key_w)
        offset_x = (key_x - center_Key_x) / ratio + move_w/2/ratio
        move_h = 0
        if key_h != center_Key_h:
            move_h = key_h - center_Key_h
        else:
            (key_h)
        offset_y = (key_y - center_Key_y) / ratio 
    else:
        offset_x = 0
        offset_y = 0

    # 上下移动    
    #offset_moveX = green_moveX - offset_y

    # coords = settings.SmartArm.get_coords_info()
    # # 左右移动
    # offset_moveY = green_moveY + offset_x

    # moveCoords_key = [offset_moveX,coords[1],-35]
    # # Move X
    # print(moveCoords_key)
    # settings.SmartArm.set_coords(moveCoords_key, 85)
    # print("The Fisrt The Key is {}, Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
    
    # time.sleep(2)
    # coords = settings.SmartArm.get_coords_info()
    # #Move Y
    # press_moveCoords_key = [coords[0],offset_moveY,coords[2]]
    # print(press_moveCoords_key)
    # settings.SmartArm.set_coords(press_moveCoords_key, 85)
    
    # time.sleep(2)
    # coords = settings.SmartArm.get_coords_info()
    # move_down = [coords[0],coords[1],down_green_moveZ]
    # settings.SmartArm.set_coords(move_down, 85)

    # time.sleep(0.1)
    # replease_move_down = [coords[0],coords[1],coords[2]]
    # settings.SmartArm.set_coords(replease_move_down, 85)

    # #step 2

    offset_moveX = green_moveX - offset_y
    offset_moveY = green_moveY + offset_x
    # 进行线性补偿 
    compensate = 0
    if target_Key_i == 0: # 第一行
        #compensate = (key_x - same_row_result[0])/200 * 3
        offset_moveX = offset_moveX - compensate
        #offset_moveY = offset_moveY + key_w/2/ratio
        # if target_Key_j == 0:
        #     offset_moveY = offset_moveY + key_w/2/ratio
    
    if target_Key_i == 2: # 第一行
        compensate = (key_x - same_row_result[0])/200 * 2
        #offset_moveX = offset_moveX - compensate

    # move_slider_bar_distance = 20
    # if (target_Key_i - center_Key_i) == 2 and haveMoveSlider == True and target_Key_j < 4:
    #     # 向左移动滑轨
    #     move_sliderbar.MoveSlideByCode(move_slider_bar_distance)
    #     #更新当前 slider bar 的值
    #     offset_moveY = offset_moveY + move_slider_bar_distance
    #     haveMoveSlider = False
    #     print()

    # if haveMoveSlider:
    #     offset_moveY = offset_moveY + move_slider_bar_distance

    moveCoords_key = [offset_moveX,offset_moveY,-30]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    print("The Second The Key is {}, Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX,offset_moveY,down_green_moveZ]
    print('Click Key location is'.format((press_moveCoords_key)))
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key, 40)

    # #step 3
    # offset_x = (key_x+key_w/2- center_Key_x) / ratio
    # offset_y = (key_y-key_h/2 - center_Key_y) / ratio
    # offset_moveX = green_moveX - offset_y
    # offset_moveY = green_moveY + offset_x

    # moveCoords_key = [offset_moveX,offset_moveY,-35]
    # settings.SmartArm.set_coords(moveCoords_key, 85)
    # print("The Third The Key is {}, Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
    # time.sleep(2)
    # press_moveCoords_key = [offset_moveX,offset_moveY,down_green_moveZ]
    # settings.SmartArm.set_coords(press_moveCoords_key, 40)
    # time.sleep(0.1)
    # settings.SmartArm.set_coords(moveCoords_key, 40)

def move_to_key(key_name,setOffset):
    result = TestPictureFile.GetKeyLocation(key_name,machine_id)
    global green_moveX
    global green_moveY
    global haveMoveSlider

    if result != None:
        key_x,key_y,key_w,key_h = result
        print("The Key is {}, Location is {}".format(key_name,result))
    else:
        return
    if setOffset :
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
    moveCoords_key = [offset_moveX,offset_moveY,-30]
    settings.SmartArm.set_coords(moveCoords_key, 85)
    print("The Second The Key is {}, Target Move offset: {} ".format(key_name,(offset_moveX,offset_moveY)))
    time.sleep(2)
    press_moveCoords_key = [offset_moveX,offset_moveY,down_green_moveZ]
    print('Click Key location is'.format((press_moveCoords_key)))
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    settings.SmartArm.set_coords(moveCoords_key, 40)

def MoveRobotByCode():
    move_zero.GoToZero()
    if settings.SmartArm == None:
        settings.SmartArm = ultraArm(move_zero.getDeviceName(), 115200)
        ZERO = [235.55, 14, 130.0, 0.0]
        settings.SmartArm.set_coords(ZERO, 60)
        time.sleep(1.5)
    allAprilTag = GetAllAprilTag()
    left_tag = GetAprilTag(allAprilTag,586)
    right_tag = GetAprilTag(allAprilTag,90)
    ratio = abs((left_tag.center[0]-right_tag.center[0])/170)
    coords = settings.SmartArm.get_coords_info()
    posx = (right_tag.center[0] - c_x) / ratio
    posy = (right_tag.center[1] - c_y) / ratio
 
    if coords:
        green_moveX = coords[0] - posy
        green_moveY = coords[1] + posx
    befor_distance = get_distance_byport.GetCurrentDistance()
    print('Before move distance {}'.format(befor_distance))
    settings.SmartArm.set_coords([green_moveX,green_moveY,-35], 60)
    time.sleep(1)
    coords = settings.SmartArm.get_coords_info()
    settings.SmartArm.set_coords([green_moveX,green_moveY-30,-35], 60)
    time.sleep(1)

    allAprilTag = GetAllAprilTag()
    left_tag = GetAprilTag(allAprilTag,586)
    right_tag = GetAprilTag(allAprilTag,90)

machine_id = "90"
if __name__=="__main__":
    #MoveRobotByCode()
    #move_sliderbar.ScanAllMachines()
    move_zero.GoToZero() 
    if settings.SmartArm == None:
        settings.SmartArm = ultraArm(move_zero.getDeviceName(), 115200)
        ZERO = [235.55, 14, 130.0, 0.0]
        settings.SmartArm.set_coords(ZERO, 60)
        time.sleep(1.5)
    coords = settings.SmartArm.get_coords_info()
    print(coords)
    target_path = 'Temp_{}.jpg'.format(str(machine_id))
    # step 1, get april tag
    allAprilTag = GetAllAprilTag()
    left_tag = GetAprilTag(allAprilTag,586)
    right_tag = GetAprilTag(allAprilTag,90)
    keyId = 0
    # step 2, calculate the ratio
    machine_id = "90"
    GetMachineIndex(90,"90")

    ratio = abs((left_tag.center[0]-right_tag.center[0])/170)

    (MaxX,MaxY,MaxW,MaxH,piex_distance) = get_color_location.getColor()
    green_key_cx = MaxX + MaxW/2 
    green_key_cy = MaxY - MaxH/2
    posx = (green_key_cx - c_x) / ratio
    posy = (green_key_cy - c_y) / ratio
    print("key_cx = {}, key_cy = {}".format(green_key_cx,green_key_cy))

    if coords:
        green_moveX = coords[0] - posy
        green_moveY = coords[1] + posx
    befor_distance = get_distance_byport.GetCurrentDistance()
    print('Before move distance {}'.format(befor_distance))
    settings.SmartArm.set_coords([green_moveX,green_moveY,-35], 60)
    time.sleep(1)
    coords = settings.SmartArm.get_coords_info()
    settings.SmartArm.set_coords([green_moveX,green_moveY-30,-35], 60)
    time.sleep(1)
    #settings.SmartArm.set_coords([coords[0],green_moveY,-70], 80)
    #time.sleep(1)
    move_down_distance = get_distance_byport.GetCurrentDistance()
    print('Move down distance {}'.format(move_down_distance))
    have_move = (befor_distance) - (move_down_distance)
    print('have Move distance {}'.format(have_move))

    move_zero.SetRobotForLongKey()

    time.sleep(2)
    current_distance = get_distance_byport.GetCurrentDistance()
    coords = settings.SmartArm.get_coords_info()
    green_moveX = coords[0]
    green_moveY = coords[1]

    press_key_distance = get_distance_byport.GetCurrentDistance()
    #move_down_distance = move_zero.move_down_distance #移动过程中查找最短距离 即为sensor到键盘的高度

    print('Press key distance {}'.format(press_key_distance))
    green_moveZ = coords[2]
    down_green_moveZ = green_moveZ - (press_key_distance - settings.Offset_Z)
    # 用弹簧
    press_moveCoords_key = [green_moveX,green_moveY,down_green_moveZ]
    print('Press key: {}'.format(press_moveCoords_key))
    settings.SmartArm.set_coords(press_moveCoords_key, 40)
    time.sleep(0.1)
    moveCoords_key = [green_moveX,green_moveY,-35]
    settings.SmartArm.set_coords(moveCoords_key, 40)
    
    center_Key = settings.Machines_center.get(machine_id)
    center_Key_x,center_Key_y,center_Key_w,center_Key_h = MaxX,MaxY,MaxW,MaxH 
    #center_Key_x,center_Key_y,center_Key_w,center_Key_h = TestPictureFile.GetKeyLocation(center_Key, machine_id)
    
    yellow_key_location = get_color_location.get_yellow_Color()
    
    
    TestPictureFile.machineIndex = machine_id
    allKeys = TestPictureFile.GetAllKeysLocation()
    for key in allKeys:
        move_to_key_for_long_keyboard(key,True)
    
    if haveMoveSlider:
        move_sliderbar.MoveSlideByCode(-20)
    # typeStr = TestRandom.GetRandomWorld().lower()
    # print(typeStr)
    # for key in typeStr:
    #     if " " == key:
    #         key = "[SPACE]"
    #     move_to_key(key,True)

    # ClickTagKey(q_tag,moveX,moveY,1)
    # time.sleep(2)
    # ClickTagKey(fn_tag,moveX,moveY,0)
    # time.sleep(2)
    # ClickTagKey(space_tag,moveX,moveY,4)
    # time.sleep(2)
    # ClickTagKey(left_tag,moveX,moveY,586)
    # time.sleep(2)
    # ClickTagKey(right_tag,moveX,moveY,90)
    # time.sleep(2)
    # ClickTagKey(n_tag,moveX,moveY,7)
    # time.sleep(2)
    # ClickTagKey(up_tag,moveX,moveY,5)
    # time.sleep(2)
    # ClickTagKey(down_tag,moveX,moveY,6)
    ZERO = [235.55, 14, 130.0, 0.0]
    settings.SmartArm.set_coords(ZERO, 40)
    print("CSW QA Smart Arm Automation Test!")


    # q_tag = GetAprilTag(allAprilTag,1)
    # print('q_tag center {}'.format(q_tag.center))
    # fn_tag = GetAprilTag(allAprilTag,0)
    # print('fn_tag center {}'.format(fn_tag.center))
    # space_tag = GetAprilTag(allAprilTag,4)
    # print('space_tag center {}'.format(space_tag.center))
    # esc_tag = GetAprilTag(allAprilTag,2)
    # print('esc_tag center {}'.format(esc_tag.center))
    # n_tag = GetAprilTag(allAprilTag,7)
    # print('n_tag center {}'.format(n_tag.center))
    # up_tag = GetAprilTag(allAprilTag,5)
    # print('up_tag center {}'.format(up_tag.center))
    # down_tag = GetAprilTag(allAprilTag,6)
    # print('down_tag center {}'.format(down_tag.center))
