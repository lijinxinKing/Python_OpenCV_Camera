import json
import os
#from Elephantrobotics import settings
PictureData = []
index_key_Data = []
machineIndex = ""
def GetKeyboardXXY(fileIndex):
    global PictureData
    fileName = "KeyboardLayout\\data_{}_temp.json".format(fileIndex)
    with open(fileName,"r") as f:
        data = json.load(f)
    PictureData = data

# def GetKeyboardIndex(key_name):
#     global index_key_Data
#     with open(r'D:\Picture\Index_0.json') as f:
#         data = json.load(f)
#     index_key_Data = data["keys"]
#     j = 0
#     i = 0
#     flag = False
#     for items in index_key_Data:
#         for item in items:
#             if len(key_name) == 1 and len(item) <= 2:
#                 if str(key_name).lower() in str(item).lower():
#                     flag = True
#                     break
#             elif len(key_name) > 1 and len(item) > 1:
#                 if str(key_name).lower() in str(item).lower():
#                     flag = True
#                     break
#             j = j + 1
#         if flag:
#             break
#         i = i + 1
#         j = 0
#         if i >=6 :
#             return None
#     return (i,j)

def GetKeyLocation(key_name,machineIndex):
    GetKeyboardXXY(machineIndex)
    layout_data = PictureData["data"]
    key_location = layout_data.get(key_name, None)
    if key_location == None:
        key_location = layout_data.get("["+key_name+"]", None)
        if key_location == None:
            key_location = layout_data.get(str(key_name).upper(), None)
            if key_location == None:
                key_location = layout_data.get(str(key_name).lower(), None)                      
                if key_location == None:
                    key_location = layout_data.get("["+str(key_name).upper()+"]", None)
                    if key_location == None:
                        key_location = layout_data.get("["+str(key_name).lower()+"]", None)
                        if key_location == None:
                           for key in list(key_name) :
                               key_location = layout_data.get(str(key).lower(), None)
                               if key_location != None:
                                   return key_location
    return key_location

def GetAllKeysLocation():
    GetKeyboardXXY(machineIndex)
    layout_data = PictureData["data"]
    return layout_data

# Get Index By MachineIndex
def GetKeyNameRowCol(i,j,machineIndex):
    fileName = "KeyboardLayout\\{}.json".format(machineIndex)
    if os.path.exists(fileName) == False:
        fileName = "KeyboardLayout\\US{}.json".format(machineIndex)
    with open(fileName,"r") as f:
        data = json.load(f)
    index_key_Data = data["keys"]
    col_count = len(index_key_Data[i])
    if j < col_count:
        if (index_key_Data[i][j]) == "" and index_key_Data[i][j-1] != "":
            return index_key_Data[i][j-1]
    else:
        return None
    return index_key_Data[i][j]

def GetRowColByKeyName(key_name,machineIndex): 
    fileName = "KeyboardLayout\\{}.json".format(machineIndex)
    if os.path.exists(fileName) == False:
        fileName = "KeyboardLayout\\US{}.json".format(machineIndex)
    with open(fileName,"r") as f:
        data = json.load(f)
    index_key_Data = data["keys"]
    j = 0
    i = 0
    flag = False
    for items in index_key_Data:
        for item in items:
            if len(key_name) == 1 and len(item) <= 2:
                if str(key_name).lower() in str(item).lower():
                    flag = True
                    break
            elif len(key_name) > 1 and len(item) > 1:
                if str(key_name).lower() in str(item).lower():
                    flag = True
                    break
            j = j + 1
        if flag:
            break
        i = i + 1
        j = 0
        if i >=6 :
            return None
    return (i,j)