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

if __name__ == "__main__":
    print("Test")
