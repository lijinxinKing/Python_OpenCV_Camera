import socket,time
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from GetDistance import get_distance_byport
y_offset = 55
z_offset = 90
c_x = 320
c_y = 240
# 像素尺寸大小
f_x = 1.45
f_y = 1.45
#焦距
f = 3.24

current_distance = 230
moveZ = -200 - current_distance + z_offset
def MoveRobot(x,y):
    enableRobot = "EnableRobot()"
    client = socket.socket() # 生成socket，连接server
    ip_port =("192.168.1.6",30003) # server地址和端口号（最好是10000以后）
    client.connect(ip_port) # 连接
    content = str("ClearError()")   
    client.send(content.encode("utf-8")) # 传送和接收都是bytes类型 
    time.sleep(4)
    content = str(enableRobot)   
    client.send(content.encode("utf-8")) # 传送和接收都是bytes类型   
    time.sleep(1)
    moveHigh = "MovL({0},{1},{2},{3},User=2)".format(x, y, -300, 100)
    print(moveHigh)
    client.send(moveHigh.encode("utf-8"))
    time.sleep(1)
    client.recv(1024)
    data = client.recv(1024)
    print(data)
    return
#查看图片的属性，图片的像素大致是75X72，实际物体的大小是32X32毫米，75/32=2.3，
#比例大概是1: 2.3，这里的比例表示2.3个像素对应1毫米，后续用这个数据来进行坐
#标位置换算，因此摄像头安装高度对坐标位置换算是有影响的（分辨率也会影响）。       
ratioCalculator = 1.466666666666667
ratioCalculator1 = 2.866666666666667
key_cx1 = 293
key_cy1 = 197
#print(get_distance_byport.GetDistance())
MoveRobot(posy - y_offset,posx)
#time.sleep(10)
#MoveRobot(posy + posy1,posx + posx1)