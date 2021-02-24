from djitellopy import tello

import cv2
from time import sleep

me = tello.Tello()

me.connect()


me.streamon()

while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow('Live', img)
    cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.streamoff()
        cv2.destroyAllWindows()
        break
