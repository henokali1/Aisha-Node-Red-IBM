#
# --- (c) 01/2020 f41ardu
#
# Tello cam using opencv proof of concept
# issue: huge delay -> Tipp scale down video size for improved performance on Raspberry PI 3+ 
# May also work with older versions of opencv supporting incomming udp streams. 
#
 
#import numpy as np
# import opencv 4.2.0 
import cv2
import time
from djitellopy import tello



me = tello.Tello()

me.connect()


me.streamon()

telloVideo = cv2.VideoCapture("udp://@0.0.0.0:11111")
#telloVideo.set(cv2.CAP_PROP_FPS, 3)

# wait for frame
ret = False
# scale down 
scale = 3

while(True):
    # Capture frame-by-framestreamon
    ret, frame = telloVideo.read()
    
    if(ret): 
    # Our operations on the frame come here
        height , width , layers =  frame.shape
        new_h=int(height/scale)
        new_w=int(width/scale)
        resize = cv2.resize(frame, (new_w, new_h)) # <- resize for improved performance 
        # Display the resulting frame
        cv2.imshow('Tello',resize)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
telloVideo.release()
cv2.destroyAllWindows()
