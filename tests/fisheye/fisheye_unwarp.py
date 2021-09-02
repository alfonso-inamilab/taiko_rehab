import math
import numpy as np 
import cv2 


#K=np.array([[781.3524863867165, 0.0, 794.7118000552183], [0.0, 779.5071163774452, 561.3314451453386], [0.0, 0.0, 1.0]])
#D=np.array([[-0.042595202508066574], [0.031307765215775184], [-0.04104704724832258], [0.015343014605793324]])
K = np.array([[228.27974798,   0.0,         365.63436654],
 [  0.0,         228.71761585, 365.48321445],
 [  0.0,           0.0,           1.0        ]])

D = np.array([[-2.92138132e-01],  [8.01465122e-02], [-9.01684318e-05],  [2.16792447e-05] ])

print (D.shape)
print (K.shape)

def main():
    # Open image
    img = cv2.imread("fisheye_sample.jpeg",-1)

    # Divide the image in two
    h = img.shape[0]
    w = img.shape[1]
    ww = w // 2
    hh = h // 2
    DIM=(h, ww)
    left = img[:, :ww]
    right = img[:, ww:]

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(left, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    cv2.imshow('result', undistorted_img)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()