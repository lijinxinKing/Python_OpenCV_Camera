import cv2
import numpy as np
import glob
 
# 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差阈值0.001
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 35, 0.001)
 
# 获取标定板4*4角点的位置
objp = np.zeros((4*4,3), np.float32)
objp[:,:2] = np.mgrid[0:4,0:4].T.reshape(-1,2) # 将世界坐标系建在标定板上，所有点的Z坐标全部为0，所以只需要赋值x和y
 
obj_points = [] # 存储3D点
img_points = [] # 存储2D点
 
# 获取指定目录下.jpg图像的路径
images = glob.glob(r"D:/imgs/*.jpg")

i=0
for fname in images:
    # print(fname)
    img = cv2.imread(fname)
    # 图像灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size = gray.shape[::-1]
    # 获取图像角点
    ret, corners = cv2.findChessboardCorners(gray, (4, 4), None)
    # print(corners)
    if ret:
        # 存储三维角点坐标
        obj_points.append(objp)
        # 在原角点的基础上寻找亚像素角点，并存储二维角点坐标
        corners2 = cv2.cornerSubPix(gray, corners, (1, 1), (-1, -1), criteria)
        #print(corners2)
        if [corners2]:
            img_points.append(corners2)
        else:
            img_points.append(corners)
        # 在黑白棋盘格图像上绘制检测到的角点
        cv2.drawChessboardCorners(img, (4, 4),corners, ret)
        i+=1
        cv2.imwrite('conimg'+str(i)+'.jpg', img)
        cv2.waitKey(10)
print(len(obj_points))
cv2.destroyAllWindows()
# 标定
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)
print('------照相机内参与外参------')
print("ret:", ret) # 标定误差
print("mtx:\n", mtx) # 内参矩阵
print("dist:\n", dist) # 畸变参数 distortion coefficients = (k_1,k_2,p_1,p_2,k_3)
print("rvecs:\n", rvecs) # 旋转向量 # 外参数
print("tvecs:\n", tvecs ) # 平移向量 # 外参数
 
 
img = cv2.imread(images[10])
print(images[10])
h, w = img.shape[:2]
# 计算一个新的相机内参矩阵和感兴趣区域（ROI）
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
print('------新内参------')
print (newcameramtx)
print('------畸变矫正后的图像newimg.jpg------')
newimg = cv2.undistort(img,mtx,dist,None,newcameramtx)
x,y,w,h = roi
newimg = newimg[y:y+h,x:x+w]
cv2.imwrite('newimg.jpg', newimg)
print ("newimg的大小为:", newimg.shape)


# # 此函数只是外部定义而已，大家可自行定义
# camera_matrix=mtx, rvec=rvecs, tvec =tvecs
# print("相机内参:", camera_matrix)
# print("平移向量:", tvec)
# print("旋转矩阵:", rvec)
# # (R T, 0 1)矩阵
# Trans = np.hstack((rvec, [[tvec[0]], [tvec[1]], [tvec[2]]]))
# # 相机内参和相机外参 矩阵相乘
# temp = np.dot(camera_matrix, Trans)
# Pp = np.linalg.pinv(temp)
# # 点（u, v, 1) 对应代码里的 [605,341,1]
# p1 = np.array([382, 210, 1], np.float)
# print("像素坐标系的点:", p1)
# X = np.dot(Pp, p1)
# print("X:", X)
# # 与Zc相除 得到世界坐标系的某一个点
# X1 = np.array(X[:3], np.float)/X[3]
# print("X1:", X1)

# ==================================================
#           将像素坐标转换为基平面世界坐标
#			import numpy as np
# ==================================================
def camera2CalibrationPlate(u: int, v: int) -> list:
    Zw = 0
    R = np.mat([[ 0.35066758],[-0.01744657],[-0.31043756]])
    T = np.mat([[-6.25989891],
       [ 3.4231296 ],
       [45.85018562]])
    I = np.mat(
        [[1.43928823e+03, 0.00000000e+00, 3.00724131e+02],
        [0.00000000e+00, 1.52014929e+03, 2.08443300e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]
        )
    imagePoint = np.mat([[u],
                         [v],
                         [1]])

    leftSideMat = R.I * I.I * imagePoint
    rightSideMat = R.I * T
    s = Zw + rightSideMat[2] / leftSideMat[2]
    s = float(s[0])
    wcPoint = R.I * (s * I.I * imagePoint - T)
    mappoint = [float(wcPoint[1]), float(wcPoint[0])]
    print(mappoint)
    return mappoint