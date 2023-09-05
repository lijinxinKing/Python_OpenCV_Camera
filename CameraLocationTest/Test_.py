import numpy as np
image_point = np.array([265, 210])
depth = 390
center_point = np.array([320, 240])
focal_length = 3.24
intrinsic_matrix = np.array([[1.48033813e+03, 0.00000000e+00, 3.11530886e+02],
                            [0.00000000e+00, 1.49998779e+03, 2.16501076e+02],
                            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

#计算2D点相对于中心点的偏移量
center_offset = image_point - center_point
#根据相机模型计算3D点的空间坐标
print(center_offset)
print(intrinsic_matrix[0, 0])
world_point = (center_offset * depth) / (focal_length * intrinsic_matrix[0, 0])
print(world_point)