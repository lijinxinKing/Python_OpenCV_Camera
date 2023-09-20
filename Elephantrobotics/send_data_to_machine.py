import socket
# 创建一个TCP套接字
def SendDataToMachine(clientIp,data):
    try:
        server_address = (clientIp, 16666)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接到服务器
        client_socket.connect(server_address)
        # 发送数据到服务器
        data = data + '\n'
        client_socket.sendall(data.encode('utf-8'))
        # 接收从服务器发送的数据
        result = b''
        receive_size = 2048
        chunk = client_socket.recv(receive_size)
        final_string = chunk.decode('utf-8')
        print(f"收到服务器的回复：{final_string}")
    # 关闭套接字
    except:
        print('')
    client_socket.close()

if __name__=='__main__':
    #,'5':'10.119.96.60','7':'10.119.96.224'
    machine_ips={'6':'10.119.96.12'}
    for ip in machine_ips:
        value = machine_ips.get(ip)
        print(value)
        SendDataToMachine(value,"FindMachine:-158")