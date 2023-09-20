import cv2,sys,os
import numpy as np
cap = cv2.VideoCapture(1, cv2.CAP_V4L)
if not cap.isOpened():
    cap.open(1)
# y增大,向左移动;y减小,向右移动;
# x增大,前方移动;x减小,向后方移动
parameters = cv2.aruco.DetectorParameters_create()
# 获取Aruco图案参数
params = cv2.aruco.DetectorParameters_create()
aruco = cv2.aruco
idList = {}
###------------------ ARUCO TRACKER ---------------------------
while (True):
    ret, frame = cap.read()
    #if ret returns false, there is likely a problem with the webcam/camera.
    #In that case uncomment the below line, which will replace the empty frame 
    #with a test image used in the opencv docs for aruco at https://www.docs.opencv.org/4.5.3/singlemarkersoriginal.jpg
    # frame = cv2.imread('./images/test image.jpg') 
    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # set dictionary size depending on the aruco marker selected
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
    # detector parameters can be set here (List of detection parameters[3])
    parameters = aruco.DetectorParameters_create()
    parameters.adaptiveThreshConstant = 10
    # lists of ids and the corners belonging to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    # font for displaying text (below)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # check if the ids list is not empty
    # if no check is added the code will crash
    for image in rejectedImgPoints:
        print(image)
    if np.all(ids != None):
        # estimate pose of each marker and return the values
        # rvet and tvec-different from camera coefficients
        # rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
        # #(rvec-tvec).any() # get rid of that nasty numpy value array error
        # for i in range(0, ids.size):
        #     # draw axis for the aruco markers
        #     cv2.drawFrameAxes(frame, mtx, dist, rvec[i], tvec[i], 0.1)

        # draw a square around the markers
        aruco.drawDetectedMarkers(frame, corners)
        # code to show ids of the marker found
        strg = ''
        for i in range(0, ids.size):
            strg += str(ids[i][0])+', '
        cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)


    else:
        # code to show 'No Ids' when no markers are found
        cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)

    # display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

# while True:
#     # 读入每一帧
#     ret, frame = cap.read()
#     cv2.imshow("capture", frame)
#     try:
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         codebook = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_1000)
#         corners, ids, rejectedImgs = cv2.aruco.detectMarkers(gray, codebook)
#         print("##########################")
#         for corner in corners:
#             print(corner)
#         for id in ids:
#             print(id)
#         for img in rejectedImgs:
#             print(img)
#         print("##########################")
#     except Exception as e:
#         print("Error:", e)
#     # 在这里执行其他操作，例如绘制矩形框、计算距离等
#     # close the window
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cap.release()
#         cv2.destroyAllWindows()
#         sys.exit()