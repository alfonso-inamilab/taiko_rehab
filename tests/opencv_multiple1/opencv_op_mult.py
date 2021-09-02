# Ejemplo sacado de : https://gist.github.com/buff4life123/031bd2d32f758656b113d73900c474e4

import estimator
import cv2
import argparse
import time


parser = argparse.ArgumentParser(
        description='This script is used to demonstrate OpenPose human pose estimation network '
                    'from https://github.com/CMU-Perceptual-Computing-Lab/openpose project using OpenCV. '
                    'The sample and model are simplified and could be used for a single person on the frame.')
parser.add_argument('--input', default="Images/p2.jpg", help='Path to image or video. Skip to capture frames from camera')
parser.add_argument('--proto', help='Path to .prototxt')
parser.add_argument('--model', default="openpose/graph_opt.pb", help='Path to .caffemodel')
parser.add_argument('--dataset',default="COCO" , help='Specify what kind of model was trained. '
                                      'It could be (COCO, MPI) depends on dataset.')
parser.add_argument('--thr', default=0.1, type=float, help='Threshold value for pose parts heat map')
parser.add_argument('--width', default=386, type=int, help='Resize input to specific width.')
parser.add_argument('--height', default=386, type=int, help='Resize input to specific height.')
parser.add_argument('--inf_engine', action='store_true',
                    help='Enable Intel Inference Engine computational backend. '
                         'Check that plugins folder is in LD_LIBRARY_PATH environment variable')

args = parser.parse_args()

e = estimator.PoseEstimator()

cap = cv2.VideoCapture(args.input if args.input else 0)
# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
while cv2.waitKey(1) < 0:
    hasFrame, frame = cap.read()
    if not hasFrame:
        cv2.waitKey()
        print("No frame")
        break

    t = time.time()
    humans = e.inference(frame,args.model,args.width,args.height)

    elapsed = time.time() - t
    print('inference image: %s in %.4f seconds.' % (args.input, elapsed))

    image = e.draw_humans(frame, humans, imgcopy=False)
    cv2.imshow('tf-pose-estimation result', image)