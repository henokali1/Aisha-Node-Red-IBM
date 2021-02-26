from pynput import keyboard
from time import sleep
from djitellopy import tello
import threading
import cv2
import face_recognition
import numpy as np
from os import listdir
from os.path import isfile, join


lr, fb, ud, yv = 0, 0, 0, 0
me = tello.Tello()

me.connect()
me.streamoff()
sleep(2)
me.streamon()

speed = 50


preSetFacePath = 'imgs/'
onlyfiles = [f for f in listdir(preSetFacePath) if isfile(join(preSetFacePath, f))]

known_face_encodings = []
known_face_names = []

for i in onlyfiles:
    lable = i.split('.')[0]
    fn = preSetFacePath + i
    known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(fn))[0])
    known_face_names.append(lable)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True




def on_press(key):
    global lr
    global fb
    global ud
    global yv
    try:
        if(key.char == 'a') or (key.char == 'A'):
            yv = speed
        if(key.char == 's') or (key.char == 'S'):
            ud = -speed
        if(key.char == 'w') or (key.char == 'W'):
            ud = speed
        if(key.char == 'd') or (key.char == 'D'):
            yv = -speed
        if(key.char == 'l') or (key.char == 'L'):
            me.land()
            me.streamoff()
            pass
        if(key.char == 't') or (key.char == 'T'):
            me.takeoff()
            pass
    except AttributeError:
        if(key == key.left):
            lr = speed
        if(key == key.right):
            lr = -speed
        if(key == key.up):
            fb = -speed
        if(key == key.down):
            fb = speed

def on_release(key):
    global lr
    global fb
    global ud
    global yv
    lr = 0
    fb = 0
    ud = 0
    yv = 0
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def frame_stream_thread(name):
    global process_this_frame
    while True:
        frame = me.get_frame_read().frame
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    # video_capture.release()
    cv2.destroyAllWindows()

frame_thread = threading.Thread(target=frame_stream_thread, args=(1,))
frame_thread.start()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

while 1:
    pass
    vals = [lr, fb, ud, yv]
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
