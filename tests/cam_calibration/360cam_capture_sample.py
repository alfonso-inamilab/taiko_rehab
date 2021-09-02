import cv2

# index = 0
# arr = []
# while True:
#     cap = cv2.VideoCapture(index)
#     if not cap.read()[0]:
#         break
#     else:
#         arr.append(index)
#     cap.release()
#     index += 1

# print (arr)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

print("Press 'c' to capture, or 'q' to quit.")
count = 0
while True:
    ret, frame = cap.read()
    if frame is not None:

        ret, img = cap.read()  #cam with leds
        if ret == False:
            continue

        cv2.imshow('CAM', img)

        #save the images 
        key = cv2.waitKey(23)
        if key & 0xFF == ord(' '):
            cv2.imwrite("captures/cam_%02d.png" % count, img)
            
            print ("Capture no. " + str(count))
            count = count + 1
            print("Press 'SPACE' to capture, or 'q' to quit.")
        elif key & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()