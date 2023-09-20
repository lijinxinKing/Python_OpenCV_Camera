# -*- coding: utf-8 -*-
import base64
import os.path
import json,time,cv2
import requests,redis,uuid
taskUUID = None
from Elephantrobotics import settings
from PIL import Image

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
# 测试代码

def GetMachineIndex(machineIndex,keyboardCode):
    target_path = 'Temp_{}.jpg'.format(str(machineIndex))
    temp_path =  'Temp_{}_1.jpg'.format(str(machineIndex))
    if settings.Camera == None:
        settings.Camera = cv2.VideoCapture(1)  # 打开USB摄像头
        
    flag = settings.Camera.isOpened()
    if flag: # 笔记本内置摄像头被打开后
        ret, frame = settings.Camera.read() # 从摄像头中实时读取视频
        #settings.Camera.release() # 关闭笔记本内置摄像头
        if os.path.exists(target_path):
            cv2.imwrite(temp_path, frame) # 保存按下空格键时摄像头视频中的图像
        else:
             cv2.imwrite(target_path, frame) # 保存按下空格键时摄像头视频中的图像
        cv2.destroyAllWindows() # 销毁显示图像的窗口
    global taskUUID
    if os.path.exists(target_path) and os.path.exists(temp_path):
        result = compare_images(target_path, temp_path)
        if result:
            return
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

def main(**kargs):
    target_path = 'Temp_2.jpg'
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    flag = cap.isOpened()
    if flag: # 笔记本内置摄像头被打开后
        ret, frame = cap.read() # 从摄像头中实时读取视频
        cap.release() # 关闭笔记本内置摄像头
        cv2.imwrite(target_path, frame) # 保存按下空格键时摄像头视频中的图像
        cv2.destroyAllWindows() # 销毁显示图像的窗口
    global taskUUID
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
        data_2 = data.replace(data_1,"")
        taskUUID = uuid.uuid1()
        print("Set Get Location Task to redis: ")
        r.set(str(taskUUID)+"_1",str(data_1))
        r.set(str(taskUUID)+"_2",str(data_2))
    finished = []
    while True:
        finished = r.get(str(taskUUID)+":Finished")
        if finished != None:
            iamgeResult = finished.decode("utf-8")
            with open("data_5_temp.json","r") as file:
                file.write(iamgeResult)
            break
        else:
            time.sleep(30)

def GetLocationByServer():
    # http://10.37.171.126:58082/image/segment?code=US02&demo=1&keyboard=1&show=1&name=keyboard&key=G
    url = "http://10.37.171.126:58082/"
    pool = redis.ConnectionPool(host='10.119.96.35',port=6379,password='',db=1)   #实现一个连接池
    r = redis.Redis(connection_pool=pool)
    keys = r.keys()
    data_dic = {}

    image_key = ''
    code = 2
    for key in keys:
        key = key.decode('utf-8')
        data_index = key.split(':')[1]
        image_key = key.split(':')[0]
        result = r.get(image_key+":Finished")
        if result == None:
            image = r.get(key)
            if image != None:
                if data_index != None:
                    data_dic[data_index] = image
                    print(data_index)
            machine_code = r.get(image_key+":code")
            if machine_code != None:
                code =str(machine_code.decode("utf-8"))
    if len(data_dic) != 3:
        time.sleep(10)
        return
    data_image = data_dic["1"] + data_dic["2"]
    data = {"image": data_image.decode("utf-8")}
    print('Get Keyboard Location')
    # data = json.dumps(m, ensure_ascii=False)
    resp = requests.post(url+"image/segment?code={}&keyboard=1&show=1&name=keyboard&async=1".format(code), json=data)
    print("Request url is " + str(resp))
    json_data = json.loads(resp.text)
    print(json_data)
    getLocation = url+json_data['taskid']
    print(getLocation)
    while True:
        resp1 = requests.get(getLocation)
        print(resp1.status_code)
        if resp1.status_code != 404:
            print(resp1.text)
            with open('data_{}_temp.json'.format(code), 'w') as f:
                f.write(resp1.text)
            r.set(str(image_key)+":Finished",resp1.text)
            print("Finished")
            break
        time.sleep(30)

def main(**kargs):

    target_path = os.path.join("data", "qrcode", "keyboard.png")
    ko = os.path.join(os.path.split(os.path.realpath(__file__))[0], "..", "..", "..", "..", "output", "keyboard")
    target_path = 'Temp_2.jpg'
    url = "http://10.176.34.22:58083/"
    
    pool = redis.ConnectionPool(host='10.119.96.35',port=6379,password='',db=1)   #实现一个连接池
    r = redis.Redis(connection_pool=pool)
    keys = r.keys()
    data_dic = {}
    image_key = ''
    code = 2
    for key in keys:
        key = key.decode('utf-8')
        data_index = key.split(':')[1]
        image_key = key.split(':')[0]
        result = r.get(image_key+":Finished")
        if result == None:
            image = r.get(key)
            if image != None:
                if data_index != None:
                    data_dic[data_index] = image
                    print(data_index)
            machine_code = r.get(image_key+":code")
            if machine_code != None:
                code =str(machine_code.decode("utf-8"))

    data_image = data_dic["1"] + data_dic["2"]
    # with open(target_path, "rb") as f:
    #     tk = f.read()
    #     image = base64.b64encode(tk)
    data = {"image": data_image.decode("utf-8")}

    #print(data)
    print('Get Keyboard Location')
    # data = json.dumps(m, ensure_ascii=False)
    resp = requests.post(url+"image/segment?code={}&keyboard=1&show=1&name=keyboard&async=1".format(code), json=data)
    print("Request url is " + str(resp))
    json_data = json.loads(resp.text)
    print(json_data)
    getLocation = url+json_data['taskid']
    print(getLocation)
    while True:
        resp1 = requests.get(getLocation)
        print(resp1.status_code)
        if resp1.status_code != 404:
            print(resp1.text)
            # 保存数据到文件
            with open('data_3_temp.json', 'w') as f:
                f.write(resp1.text)
            r.set(str(image_key)+":Finished",resp1.text)
                # r.set(code,resp1.text)
                # print(r.get(code).decode('utf8'))
            break
        time.sleep(30)
        
if __name__ == "__main__":
    while True:
        GetLocationByServer()
        time.sleep(10)
