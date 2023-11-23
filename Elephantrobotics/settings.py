Camera = None
SmartArm = None
AndroidDriver = None
TestMachine_ips={'6':'10.119.96.64','5':'10.119.96.62','7':'10.119.96.224'}

#Return Message
SliderNotLaunch = "The Slider Not Launch,Failed"
ScanMachineFinished = "Scan Machines Finished,Successful"

# Key:机器AprilTag ID，Value: layoutId，考虑到，不同的机器 可能存在一样的layout，
# 不添加key 和value 的对应关系 则 代表 key 和value 为一个值
Machine_Code_Dic={'6':2,'5':3}
# 摄像头的宽和高的值
resolutionRatio_Width = 1280
resolutionRatio_Height = 720
#机器AprilTag ID 和 键盘中心点色块所在的按键位置
Machines_center={'90':'L','91':'L','5':'h','7':'j'}
#机器上粘贴二维码的距离，可以为机器AprilTag ID,Value 为 距离
machine_len = {'90':170,'91':172,'5':178,'7':201}
#
Offset_Z = 98
end_left_distance = 50
end_up_distance = 30
end_high_distance = 118

min_keyboard = [['Num Lock','/','*','-'],
                ['7','8','9','+'],
                ['4','5','6',''],
                ['1','2','3','Enter'],
                ['0','','.','']]


#智能手指Name和测试机DeviceName 的对应关系 注：区分大小写
SmartFingureMachine = {'LAPTOP-T7SDIEJE':'gaming-Y770SIN'}
#机械臂识别的ID和测试机DeviceName 的对应关系 注：区分大小写
SmartArmMachine = {'LAPTOP-T7SDIEJE':'7'}