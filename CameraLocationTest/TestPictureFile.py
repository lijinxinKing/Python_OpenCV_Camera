import json
PictureData = []
index_key_Data = []
def GetKeyboardXXY(fileIndex):
    global PictureData
    fileName = "data_{}_temp.json".format(fileIndex)
    with open(fileName,"r") as f:
        data = json.load(f)
    PictureData = data

def GetKeyboardIndex(key_name):
    global index_key_Data
    with open(r'D:\Picture\Index_0.json') as f:
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

    return key_location

def GetAllKeysLocation():
    GetKeyboardXXY("5")
    layout_data = PictureData["data"]
    return layout_data

# def GetRealXY(key_name):
#     GetKeyboardXXY()
#     layout_data = PictureData["data"]
#     global index_key_Data
#     key_row,key_col = GetKeyboardIndex(key_name)
#     key_fist_row = index_key_Data[key_row][0]
#     key_x_row,key_y_row,key_w_row,key_h_row = layout_data[key_fist_row]
#     print((key_x_row,key_y_row,key_w_row,key_h_row))

#     h_key_row,h_key_col = GetKeyboardIndex("H")
#     based_fist_row = index_key_Data[h_key_row][0]
#     based_x_row,based_y_row,based_w_row,based_h_row = layout_data[based_fist_row]
#     print((based_x_row,based_y_row,based_w_row,based_h_row))
#     row_offset = key_row - h_key_row
#     col_offset = key_col - h_key_col
#     w_offset = key_w_row - based_w_row
#     return (row_offset,col_offset,w_offset)
