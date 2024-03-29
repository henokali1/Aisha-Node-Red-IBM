from pynput import keyboard
from time import sleep
from djitellopy import tello
import threading
import cv2
import face_recognition
import requests
import numpy as np
from os import listdir, remove
from os.path import isfile, join
import base64
from datetime import datetime
import pickle


def get_face_db(img_name, img_url):
    img_data = requests.get(img_url).content
    with open(img_name, 'wb') as handler:
        handler.write(img_data)

def download_faces():
    url = 'https://node-red-arzjk-2021-01-25.eu-gb.mybluemix.net/all-registered-faces-db'
    resp = requests.get(url=url)
    data = resp.json()

    # Remove old face images
    print('Removing old face data')
    preSetFacePath = 'imgs/'
    filenames = [f for f in listdir(preSetFacePath) if isfile(join(preSetFacePath, f))]
    for fn in filenames:
        remove(preSetFacePath+fn)
    print('Old face data removed')
    print('Downloading new face data.....')
    for i in data:
        img_url = i['img_url']
        img_extension = img_url.split('.')[-1]
        img_name = f"imgs/{i['name']}.{img_extension}"
        get_face_db(img_name, img_url)
    print('New face data download completed')

# Download face data from IBM database
download_faces()


lr, fb, ud, yv = 0, 0, 0, 0
me = tello.Tello()
# video_capture = cv2.VideoCapture('tv2.mp4')

me.connect()
me.streamoff()
sleep(2)
me.streamon()

speed = 50
rec_names = {}

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


def upload_rec_face(attachment_img):
    with open(attachment_img, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": 'b1089233e4d54c193d35a18dfdb37ed0',
            "image": base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)
        data = res.json()['data']
        img_url = data['display_url']
    return img_url

def get_last_login():
    url = 'https://node-red-arzjk-2021-01-25.eu-gb.mybluemix.net/get-last-login-db'
    res = requests.get(url).json()
    ts = []
    for i in res:
        ts.append(int(i['timestamp']))
    last_login_ts = max(ts)
    last_login_full_name = ''
    for i in res:
        if int(i['timestamp']) == last_login_ts:
            return i['fullname']

def get_last_mission():
    url = 'https://node-red-arzjk-2021-01-25.eu-gb.mybluemix.net/get-all-missions-db'
    res = requests.get(url).json()
    ts = []
    for i in res:
        ts.append(int(i['timestamp']))
    last_mission_ts = max(ts)
    for i in res:
        if int(i['timestamp']) == last_mission_ts:
            return {'mission_name':i['mission_name'], 'mission_location':i['mission_location']}

def get_current_date_time():
    # datetime object containing current date and time
    now = datetime.now()
    
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    c_date = dt_string.split(' ')[0]
    c_time = dt_string.split(' ')[1]
    return {'date':c_date, 'time':c_time}

def get_convict_info(convict_name):
    url = 'https://node-red-arzjk-2021-01-25.eu-gb.mybluemix.net/all-registered-faces-db'
    res = requests.get(url).json()
    for i in res:
        if(i['name'] == convict_name):
            return i

def generate_report(convict_name, attachment_img):
    print(f'Generating report for {convict_name}')
    cdt = get_current_date_time()
    lm = get_last_mission()
    convict_info = get_convict_info(convict_name)
    officer_name = get_last_login()
    detected_face_img = upload_rec_face(attachment_img)
    date = cdt['date']
    time = cdt['time']
    mission_name = lm['mission_name']
    mission_location = lm['mission_location']
    convict_name = convict_info['name']
    convict_age = convict_info['age']
    prev_case = convict_info['prev_case']
    registered_face = convict_info['img_url']

    params = f'?date={date}&time={time}&mission_name={mission_name}&mission_location={mission_location}&officer_name={officer_name}&'
    params += f'convict_name={convict_name}&convict_age={convict_age}&prev_case={prev_case}&detected_face_img={detected_face_img}&'
    params += f'registered_face={registered_face}'
    url = 'https://node-red-arzjk-2021-01-25.eu-gb.mybluemix.net/add-reports-db'+params
    res = requests.get(url).json()
    for i in res:
        print(i, res[i])


def on_press(key):
    global lr
    global fb
    global ud
    global yv
    try:
        if(key.char == 'a') or (key.char == 'A'):
            yv = -speed
        if(key.char == 's') or (key.char == 'S'):
            ud = -speed
        if(key.char == 'w') or (key.char == 'W'):
            ud = speed
        if(key.char == 'd') or (key.char == 'D'):
            yv = speed
        if(key.char == 'l') or (key.char == 'L'):
            me.land()
            me.streamoff()
            pass
        if(key.char == 't') or (key.char == 'T'):
            me.takeoff()
            pass
    except AttributeError:
        if(key == key.left):
            lr = -speed
        if(key == key.right):
            lr = speed
        if(key == key.up):
            fb = speed
        if(key == key.down):
            fb = -speed

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
    print('Connecting to drone...')
    telemetry_data = {}
    while True:
        telemetry_data['speed'] = me.get_speed()
        telemetry_data['battery'] = me.get_battery()
        telemetry_data['flight_time'] = me.get_flight_time()
        telemetry_data['height'] = me.get_height()
        telemetry_data['attitude'] = me.get_attitude()
        telemetry_data['barometer'] = me.get_barometer()
        telemetry_data['distance_tof'] = me.get_distance_tof()
        print(telemetry_data)
        # Save telemetry data
        with open('telemetry.pickle', 'wb') as handle:
            pickle.dump(telemetry_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        frame = me.get_frame_read().frame
        # ret, frame = video_capture.read()
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
            if name != 'Unknown':
                print(f'Face detected:\t{name}')
                if not(name in rec_names):
                    rec_names[name]=name
                    print(f'Generating Report for {name}')
                    fn = f'imgs/report-imgs/{name}-report.jpg'
                    print(fn)
                    cv2.imwrite(fn, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                    generate_report(name, fn)

                

        # Display the resulting image
        cv2.imshow('Video', frame)
        fifn = 'static/imgs/cfi.jpg'
        cv2.imwrite(fifn, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        
        # cv2.imwrite(fifn, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    # video_capture.release()
    # cv2.destroyAllWindows()

frame_thread = threading.Thread(target=frame_stream_thread, args=(1,))
frame_thread.start()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

while 1:
    # pass
    vals = [lr, fb, ud, yv]
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
