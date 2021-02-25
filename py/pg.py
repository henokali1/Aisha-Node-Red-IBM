from flask_opencv_streamer.streamer import Streamer
import cv2

import time
from djitellopy import tello



me = tello.Tello()

me.connect()


me.streamoff()
time.sleep(2)
me.streamon()
time.sleep(2)

port = 3030
require_login = False
streamer = Streamer(port, require_login)

scale = 9
# Open video device 0
# video_capture = cv2.VideoCapture('tv2.mp4')
video_capture = cv2.VideoCapture("udp://@0.0.0.0:11111")

while True:
    _, frame = video_capture.read()
    
    height , width , layers =  frame.shape
    new_h=int(height/scale)
    new_w=int(width/scale)
    resize = cv2.resize(frame, (new_w, new_h)) # <- resize for improved performance 

    streamer.update_frame(frame)

    if not streamer.is_streaming:
        streamer.start_streaming()

    cv2.waitKey(30)
