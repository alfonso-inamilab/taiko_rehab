import cv2
 
capture = cv2.VideoCapture(0)
 
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
videoWriter = cv2.VideoWriter('test-video.mp4', fourcc, 30.0, (640,480))
 
while (True):
 
    ret, frame = capture.read()
     
    if ret:
        cv2.imshow('video', frame)
        videoWriter.write(frame)
 
    if cv2.waitKey(1) == 27:
        break
 
capture.release()
videoWriter.release()
 
cv2.destroyAllWindows()