import cv2
import pupil_apriltags as apriltag     #  windows
import socket               # 导入 socket 模块

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
flag = cap.isOpened()
localIp = ""

#while flag:

def GetAprilTag():
    ret, image = cap.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 创建一个apriltag检测器，然后检测AprilTags
    options = apriltag.Detector(families='tag36h11 ')  # windows
    results = options.detect(gray)
    print(results)
    for r in results:
    # 获取4个角点的坐标
        b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
        c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
        d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
        a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])
    # 绘制检测到的AprilTag的框
        cv2.line(image, a, b, (255, 0, 255), 1, lineType=cv2.LINE_AA)
        cv2.line(image, b, c, (255, 0, 255), 1, lineType=cv2.LINE_AA)
        cv2.line(image, c, d, (255, 0, 255), 1, lineType=cv2.LINE_AA)
        cv2.line(image, d, a, (255, 0, 255), 1, lineType=cv2.LINE_AA)
    # 绘制 AprilTag 的中心坐标
        (cX, cY) = (int(r.center[0]), int(r.center[1]))
        cv2.circle(image, (cX, cY), 1, (0, 0, 255), -1)
    # 在图像上绘制标文本
        tagFamily = r.tag_family.decode("utf-8") +'_Id_'+ str(r.tag_id)
        cv2.putText(image, tagFamily, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        getTagPicName = 'image'+str(r.tag_id)+'.png'
        cv2.imwrite(getTagPicName, image)
    cv2.imshow("Image", image)
    # 按 Q 退出
    if cv2.waitKey(1000) & 0xFF == ord('q'): return

def get_local_ip():
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    return [addr[4][0] for addr in addrs]

def check_ipv4(str):
    ip = str.strip().split(".")
    return False \
        if len(ip) != 4 or False in map(lambda x: True if x.isdigit() and 0 <= int(x) <= 255 else False, ip) \
        else True

def getCurrentIP():
    ips = get_local_ip()
    for ip in ips:
        if check_ipv4(ip):
            if "192.168." not in ip :
                print(ip)
                localIp = ip

if __name__ == '__main__':
    print('Hello from main method of first_module.py')
    GetAprilTag()
    s = socket.socket()         # 创建 socket 对象
    host = socket.gethostbyname(socket.getfqdn(socket.gethostname())) # 获取本地主机名
    port = 17778                # 设置端口
    print(host)
    s.bind((localIp, port))        # 绑定端口
    s.listen(5)                 # 等待客户端连接
    while True:
        c,addr = s.accept()     # 建立客户端连接
        print (addr) #addr
        c.send('欢迎访问菜鸟教程！')
        GetAprilTag()
        c.close()                # 关闭连接