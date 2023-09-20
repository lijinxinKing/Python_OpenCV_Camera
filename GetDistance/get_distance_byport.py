# 安装：pip3 install pyserial   //python3
import serial
import serial.tools.list_ports
import time
import re
com_rx_buf = ''				# 接收缓冲区
com_tx_buf = ''				# 发送缓冲区
COMM = serial.Serial()		# 定义串口对象
port_list: list				# 可用串口列表
port_select: list			# 选择好的串口
deviceName = ""
distanceDeviceName = "Silicon Labs CP210x USB to UART Bridge"
# 打开串口
def serial_open():
    global deviceName
    # 获取所有的串口名
    com_list = serial.tools.list_ports.comports()
    for com in com_list:
        if distanceDeviceName in str(com):
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

def com_receive():
        try:
            rx_buf = ''
            rx_buf = COMM.read()  # 转化为整型数字
            if rx_buf != b'':
                time.sleep(0.01)
                rx_buf = rx_buf + COMM.read_all()
                return rx_buf
            else:
                return None
        except:
            pass

def GetCurrentDistance():
    serial_open()
    recv = ""
    while recv == None or recv == "":
        recv = com_receive()
        if recv != None:
            lst = re.split(r"\s+", str(recv))
            for data in lst:
                if str(data).isdigit():
                    serial_close()
                    return data
        time.sleep(0.01)
    serial_close()
    return str(recv)

if __name__ == "__main__":
    print(GetCurrentDistance())