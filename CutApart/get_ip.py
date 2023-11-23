# -*- coding: utf-8 -*-
import socket
import requests
import re
from netifaces import interfaces, ifaddresses, AF_INET
import socket

class IP:
    @staticmethod
    def get_ip_public():
        """
        获取本机公网IP
        :return:
        """
        try:
            text = requests.get("http://txt.go.sohu.com/ip/soip").text
            ip_public = re.findall(r'\d+.\d+.\d+.\d+', text)[0]
            return ip_public
        except:
            return '0.0.0.0'

    @staticmethod
    def get_ip_local():
        """
        查询本机内网IP
        :return:
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

def GetLocalIPByPrefix(prefix):
    r""" 多网卡情况下，根据前缀获取IP（Windows 下适用） """
    localIP = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        print(ip)
        if ip.startswith(prefix) == None:
            localIP = ip
        
    return localIP
    

if __name__ == '__main__':
    print(GetLocalIPByPrefix('192.168'))
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        print(' '.join(addresses))

    print("内网IP：{}".format(IP.get_ip_local()))
    print("外网IP：{}".format(IP.get_ip_public()))

