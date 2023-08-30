import socket,time
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location

y_offset = 55
z_offset = 90
c_x = 320
c_y = 240
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
posx1 = (key_cx1 - c_x) / ratioCalculator1
posy1 = (key_cy1 - c_y) / ratioCalculator1
#244, 281, 19, 19, 1.2666666666666666
ratioCalculator = 1.4333333333333333
#120, 225, 22, 21, 1.4333333333333333
(key_x,key_y,w,h,radio)= get_color_location.getColor()
print((key_x,key_y,w,h,radio))
key_cx = key_x + w/2 
key_cy = key_y + h/2
posx = (key_cx - c_x) / radio
posy = (key_cy - c_y) / radio
#MovL(34.772727272727266,-132.27272727272725,-200,100,User=2)
MoveRobot(posy - y_offset,posx)
#time.sleep(10)
#MoveRobot(posy + posy1,posx + posx1)