from airtest.core.api import *
import time,socket,sys
import subprocess
import platform
#subprocess.check_call(['adb', 'start-server'], cwd=r"C:\\Users\\lijinxin\AppData\\Local\\Android\\SDK\\platform-tools")
                      
DEFAULT_ADB_PATH={}
global localIp
def _set_adb_path():
    system = platform.system()
    machine = platform.machine()
    adb_index = '{}-{}'.format(system, machine)
    if adb_index not in DEFAULT_ADB_PATH:
        adb_index = system
    
    # overwrite uiautomator adb
    if "ANDROID_HOME" in os.environ:
        sdk_path = os.environ["ANDROID_HOME"]
        if "Windows" == adb_index:
            adb_path = os.path.join(sdk_path, 'platform-tools', 'adb.exe')
        else:
            adb_path = os.path.join(sdk_path, 'platform-tools', 'adb')
        if os.path.exists(adb_path):
            DEFAULT_ADB_PATH[adb_index] = adb_path
            print('set adb path to {0}'.format(DEFAULT_ADB_PATH[adb_index]))

_set_adb_path()

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
                print(localIp)
def ClickBegin():
    try:
        init_device("Android")
        keyevent("BACK")
        start_app("com.tuya.smartlifeiot")
        wait(Template("smart fingure 2.png"),5, touch(Template("smart fingure 2.png")))    
        wait(Template("clickBeginBtn.png"),5, touch(Template("clickBeginBtn.png")))      
    except BaseException as e:
        print(e)

def ClickReturn():
    init_device("Android")
    wait(Template(
        "clickBackBtn.png"),5,touch(Template("clickBackBtn.png")))  
    keyevent("BACK")
    keyevent("BACK")

def main(args):
    # 获取除了脚本名以外的命令行参数
    arg1 = args[1]
    #arg2 = args[2]
    print(arg1)
    print(args)
    if "b" in arg1:
        ClickBegin()
    elif "r" in arg1:
        ClickReturn()

if __name__ == '__main__':
    main(sys.argv)