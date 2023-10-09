# -*- coding: utf-8 -*-
import base64
import os.path
import json,time,cv2
import requests,redis,uuid
taskUUID = None
from Elephantrobotics import settings
from PIL import Image

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
    print("Test")
