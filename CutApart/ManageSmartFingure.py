import sys
import time
import cv2
import numpy as np
import sys,os,cv2,math
import redis,uuid,base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Elephantrobotics import settings
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from appium.options.common import AppiumOptions

option = AppiumOptions()

desired_caps = {
    'platformName': 'Android',
    'platformVersion': '8.1.0',
    'deviceName': 'HLTE700T',
    'appPackage': 'com.tuya.smartiot',
    'appActivity': 'com.smart.ThingSplashActivity',
    'skipServerInstallation': False,
    'skipDeviceInitialization': True,
    'dontStopAppOnReset': True,
    'noReset': True
}
option.set_capability('platformName','android')
option.set_capability('platformVersion','8.1.0')
option.set_capability('deviceName','HLTE700T')
option.set_capability('appPackage','com.tuya.smartiot')
option.set_capability('appActivity','com.smart.ThingSplashActivity')
option.set_capability('skipServerInstallation',False)
option.set_capability('skipDeviceInitialization',True)
option.set_capability('dontStopAppOnReset',True)
option.set_capability('noReset',True)
option.set_capability('newCommandTimeout',100)

app_started = False
color_threshold = 500

def startApp():
    try:
        if settings.AndroidDriver == None:
            settings.AndroidDriver = webdriver.Remote('http://127.0.0.1:4724/wd/hub',desired_capabilities=desired_caps)
            settings.AndroidDriver.implicitly_wait(5)

        if 'appContext' in settings.AndroidDriver.session:
            settings.AndroidDriver.execute_script('mobile: activateApp', {'bundleId': settings.AndroidDriver.session['appContext']})
        else:
            settings.AndroidDriver.session['appContext'] = settings.AndroidDriver.current_package
    except Exception as e:
        print('Start Android App Failed')
        time.sleep(1)
    
def closeAPP():
    try:
        f = os.popen(r"adb shell dumpsys activity top | findstr ACTIVITY", "r")  # 获取当前界面的Activity
        current_activity = f.read()
        f.close()
        print(current_activity)  # cmd输出结果
        
        # 用in方法 判断一个字符串是否包含某字符
        apppackage_name = 'com.tuya.smartiot'
        if apppackage_name in current_activity:
            settings.AndroidDriver.quit()
            settings.AndroidDriver = None
        else:
            pass
    except:
        print('Start Android App Failed')

def ClickBegin(arg):
    global color_threshold
    if "And" in arg:
        arg_parts = arg.split("And")
        arg1 = arg_parts[0].strip()
        arg2 = arg_parts[1].strip()
        text_element1 = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg1}']/..")
        target_button1 = text_element1.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        text_element2 = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg2}']/..")
        target_button2 = text_element2.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        TouchAction(settings.AndroidDriver).tap(target_button1).perform()
        time.sleep(1)
        TouchAction(settings.AndroidDriver).tap(target_button2).perform()
    elif "Long" in arg:
        arg_parts = arg.split("Long")
        arg1 = arg_parts[0].strip()
        text_element1 = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg1}']/..")
        target_button1 = text_element1.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        TouchAction(settings.AndroidDriver).tap(target_button1).perform()
        time.sleep(3)
        TouchAction(settings.AndroidDriver).tap(target_button1).perform()
    elif "Press" in arg:
        arg_parts = arg.split(" ")
        arg1 = arg_parts[1].strip()
        text_element = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg1}']/..")
        target_button = text_element.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        button_location = target_button.location
        button_size = target_button.size
        screenshot_path = r"smartFingure_screenshot.png"
        settings.AndroidDriver.get_screenshot_as_file(screenshot_path)
        screenshot = cv2.imread(screenshot_path)
        button_x, button_y = button_location['x'], button_location['y']
        button_width, button_height = button_size['width'], button_size['height']
        button_area = screenshot[button_y:button_y + button_height, button_x:button_x + button_width]
        average_color_per_row = np.average(button_area, axis=0)
        average_color = np.average(average_color_per_row, axis=0)
        print("Average color for the button:", average_color)
        #sum(average_color)
        print("Sum color for the button:", sum(average_color))
         
        if(sum(average_color) > color_threshold): #已经按下
            TouchAction(settings.AndroidDriver).tap(target_button).perform()
            time.sleep(1)
    else:
        arg_parts = arg.split(" ")
        arg1 = arg_parts[1].strip()
        text_element = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg1}']/..")
        target_button = text_element.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        #这个按钮的状态一直是false,颜色也get不到  没有办法对按钮的状态进行判断了
        #print("target_button state IS ", target_button.get_attribute("checked"))
        TouchAction(settings.AndroidDriver).tap(target_button).perform()
        time.sleep(1)
        TouchAction(settings.AndroidDriver).tap(target_button).perform()

def ClickFRelease(arg):
    if "And" in arg:
        arg_parts = arg.split("And")
        arg1 = arg_parts[0].strip()
        arg2 = arg_parts[1].strip()
        text_element1 = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg1}']/..")
        target_button1 = text_element1.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        text_element2 = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg2}']/..")
        target_button2 = text_element2.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        TouchAction(settings.AndroidDriver).tap(target_button1).perform()
        time.sleep(1)
        TouchAction(settings.AndroidDriver).tap(target_button2).perform()
    else:
        text_element = settings.AndroidDriver.find_element(By.XPATH, f"//*[@text='{arg}']/..")
        target_button = text_element.find_element(By.ID, 'com.tuya.smartiot:id/switchButton')
        #这个按钮的状态一直是false,颜色也get不到  没有办法对按钮的状态进行判断了
        #print("target_button state IS ", target_button.get_attribute("checked"))
        TouchAction(settings.AndroidDriver).tap(target_button).perform()
        time.sleep(1)
        TouchAction(settings.AndroidDriver).tap(target_button).perform()

def PressSmartFingure(fingureName):
    startApp()
    global color_threshold
    color_threshold = 600
    ClickBegin("Press "+fingureName)
    

def ReleaseSmartFingure(fingureName):
    startApp()
    global color_threshold
    color_threshold = 500
    ClickBegin("Press "+fingureName)
    closeAPP()

def main(args):
    if len(args) > 1:
        arg1 = args[1]
        print("arg1 IS ", arg1)
        if arg1 == "b":
            if not app_started:
                startApp()
                app_started = True
            if len(args) > 2:
                arg2 = args[2]
                ClickBegin(arg2)
                print("arg2 IS ", arg2)
            else:
                print("缺少第二个命令行参数")
            #settings.AndroidDriver.quit()
        else:
            print("不匹配的命令行参数")
    else:
        print("缺少命令行参数")


if __name__ == '__main__':
    PressSmartFingure("gaming-Y770SIN")#区分大小写
    ReleaseSmartFingure("gaming-Y770SIN")#区分大小写     