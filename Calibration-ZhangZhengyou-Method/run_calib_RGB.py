# -*- coding: utf-8 -*-
"""
Calibrate the Camera with Zhang Zhengyou Method.
Picture File Folder: "./pic/RGB_camera_calib_img/", Without Distortion. 

By You Zhiyuan, 2022.07.04, zhiyuanyou@foxmail.com
"""

import os

from calibrate_helper import Calibrator

import numpy as np
def main():
    #img_dir = "./pic/CameraCalibration_VGA"
    img_dir = "D:\imgs"
    shape_inner_corner = (9, 6)
    size_grid = 0.026 #棋盘格子大小 26mm
    # create calibrator
    calibrator = Calibrator(img_dir, shape_inner_corner, size_grid)
    # calibrate the camera
    mat_intri, coff_dis = calibrator.calibrate_camera()


if __name__ == '__main__':
    matrixHand2Camera = np.array([[ 0.56186877, -0.82718502, -0.00827197, 0.00665606],
                            [ 0.82722097,0.56180082, 0.00923615, -0.0420225],
                            [-0.00299281 , -0.01203225, 0.99992313, 0.02549419],
                            [ 0,          0,          0,          1         ]]) # 手眼矩阵THC

    matrixBase2Hand = np.array([[0.26195007,	-0.14356031, 0.95434407, 0.319418241631],
                            [-0.67221037, -0.73668364, 0.07369148,	-0.010993728332],
                            [0.69247049, -0.66082346, -0.28947706, 0.689715275419],
                            [0,           0,          0,          1         ]]) # 末端姿态TBH

    matrixCamera2Pixel = np.array([ [893.1528305,    0,         230.94830809],
                                    [  0,         880.48101697, 262.30719081],
                                    [  0,           0,           1        ]]) # 内参

    matrixBase2Camera = np.dot(matrixBase2Hand,matrixHand2Camera)
    matrixCamera2Base = np.linalg.inv(matrixBase2Camera)

    zc = 0.490
    u = 118
    v = 222

# 直接变换
    outputBase2 = np.dot(np.linalg.inv(matrixCamera2Base[0:3,0:3]),zc*np.dot(np.linalg.inv(matrixCamera2Pixel),np.array([u,v,1]).reshape(3,1))-matrixCamera2Base[:3,3].reshape(3,1))
    print("直接变换",outputBase2)

