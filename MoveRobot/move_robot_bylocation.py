import time
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import get_color_location
from GetDistance import get_distance_byport
from MoveRobot import move_robot_zero
y_offset = 55
z_offset = 290
c_x = 320
c_y = 240
target_z = 115
current_distance = 0
moveZ = 0
client = None
def MoveRobot(x,y):   
    global client
    moveHigh = "MovL({0},{1},{2},{3},User=2)".format(x, y, moveZ, 100)
    print("Send: "+moveHigh)
    client.send(moveHigh.encode("utf-8"))
    time.sleep(1)

def main():
    move_robot_zero.MoveTargetHigh()
    time.sleep(10)
    (key_x,key_y,w,h,radio)= get_color_location.getColor()
    print((key_x,key_y,w,h,radio))
    key_cx = key_x + w/2 
    key_cy = key_y + h/2
    posx = (key_cx - c_x) / radio
    posy = (key_cy - c_y) / radio
    global current_distance
    current_distance = get_distance_byport.GetCurrentDistance()
    global moveZ
    current_xyz = move_robot_zero.GetCurrentRobotXYZR()
    global client
    client = move_robot_zero.client
    if len(current_xyz) > 0:
        current_z = current_xyz[2]
        print(current_z)
        need_move_z = target_z - float(current_distance)
        moveZ = float(current_z) + need_move_z
    MoveRobot(posy - y_offset, posx)
    time.sleep(8)

    (key_x,key_y,w,h,radio)= get_color_location.getColor()
    print((key_x,key_y,w,h,radio))
    robot_end_x = 310
    robot_end_y = 450
    key_cx = key_x + w/2
    key_cy = key_y + h/2
    posx = (key_cx - robot_end_x) / radio
    posy = (key_cy - robot_end_y) / radio
    current_xyz = move_robot_zero.GetCurrentRobotXYZR()
    move_x = float(current_xyz[0]) + posy #左右移动 机械臂的Y轴移动
    move_y = float(current_xyz[1]) + posx #上下移动 机械臂的X轴移动
    MoveRobot(move_x, move_y-10)
    #time.sleep(8)
    
    # (key_x,key_y,w,h,radio)= get_color_location.getColor()
    # print((key_x,key_y,w,h,radio))
    # need_move_x = robot_end_x - float(key_x)
    # need_move_y = robot_end_y - float(key_y)
    # key_cx = key_x + w/2 
    # key_cy = key_y + h/2
    # posx = (key_cx - robot_end_x) / radio
    # posy = (key_cy - robot_end_y) / radio
    # current_xyz = move_robot_zero.GetCurrentRobotXYZR()
    # if abs(need_move_x) < 10:
    #     current_x = float(current_xyz[0])
    # else:   
    #     current_x = float(current_xyz[0]) + posx
    # if abs(need_move_y) < 10:
    #     current_y = float(current_xyz[1])
    # else :
    #     current_y = float(current_xyz[1]) + posy
    # MoveRobot(current_x,current_y)

# x 上下移动
# y 左右移动
if __name__ == "__main__":
    main()
    #time.sleep(5)
    
#查看图片的属性，图片的像素大致是75X72，实际物体的大小是32X32毫米，75/32=2.3，
#比例大概是1: 2.3，这里的比例表示2.3个像素对应1毫米，后续用这个数据来进行坐
#标位置换算，因此摄像头安装高度对坐标位置换算是有影响的（分辨率也会影响）。  