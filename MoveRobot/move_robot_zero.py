import socket,time,os,sys,re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from GetDistance import get_distance_byport

target_z = 400
client = None

def GetCurrentRobotXYZR():
    global client
    enableRobot = "EnableRobot()"
    if client == None:
        client = socket.socket() # 生成socket，连接server
        ip_port =("192.168.1.6",30003) # server地址和端口号（最好是10000以后）
        client.connect(ip_port) # 连接 
        client.send(enableRobot.encode("utf-8")) # 传送和接收都是bytes类型
        content = str("ClearError()")   
        client.send(content.encode("utf-8")) # 传送和接收都是bytes类型
        
    getPose = "GetPose(2,0)"
    content = str(getPose)   
    client.send(content.encode("utf-8")) # 传送和接收都是bytes类型   
    time.sleep(2)
    message = client.recv(1024)
    print(message)
    if message != None:
        msg = str(message)
        msg = msg.replace('b\'0,{','')
        count = re.findall('-?\d+.?\d+', msg)
        print(count)
        return count[0:4]
     
def ClearError(): 
    content = str("ClearError()")   
    client.send(content.encode("utf-8")) # 传送和接收都是bytes类型 

def MoveTargetHigh():
    xyzr = GetCurrentRobotXYZR()
    if len(xyzr) < 2:
        return
    current_distance = get_distance_byport.GetCurrentDistance()
    print("current_distance: " + current_distance)
    movez = target_z - float(current_distance)
    print(movez)
    current_z = float(xyzr[2]) + movez
    moveHigh = "MovL({0},{1},{2},{3},User=2)".format(0, 0, current_z, 0)
    print(moveHigh)
    client.send(moveHigh.encode("utf-8")) # 传送和接收都是bytes类型
    time.sleep(1.5)
 
def main():
    MoveTargetHigh()

if __name__ == '__main__':
    main()
    client.close()