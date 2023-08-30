import socket,time
def GetCurrentPos():
    enableRobot = "EnableRobot()"
    client = socket.socket() # 生成socket，连接server
    ip_port =("192.168.1.6",30003) # server地址和端口号（最好是10000以后）
    client.connect(ip_port) # 连接
    content = str(enableRobot)   
    res = client.send(content.encode("utf-8")) # 传送和接收都是bytes类型   
    time.sleep(1)
    getPos = "GetPose(2,0)"
    content = str(getPos)   
    client.send(content.encode("utf-8")) # 传送和接收都是bytes类型
    data = client.recv(1024)
    print(data)
    data = client.recv(1024)
    print(data)
    moveHigh = "MovL({0},{1},{2},{3},User=2)".format(34, -132, -200, 0)
    client.send(moveHigh.encode("utf-8")) # 传送和接收都是bytes类型
    data = client.recv(1024)
    data = client.recv(1024)
    print(data)   
ratioCalculator = 1.5
c_x = 320
c_y = 240
key_cx = 123
key_cy = 290
posx = (key_cx - c_x) / ratioCalculator
posy = (key_cy - c_y) / ratioCalculator
print(GetCurrentPos())