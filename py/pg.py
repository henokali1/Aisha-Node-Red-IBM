from flask import Flask
from os import system
from flask import Flask,jsonify,render_template, send_from_directory,Response
from random import randint

from numpy import imag

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
        if(key.char == 'q') or (key.char == 'Q'):
            me.land()
            me.streamoff()
            pass
        if(key.char == 'e') or (key.char == 'E'):
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

# Download face data from IBM database
download_faces()


def gen_frames():  # generate frame by frame from camera
    global process_this_frame
    while True:
        # Capture frame-by-frame
        success, frame = video_capture.read()  # read the camera frame
        if not success:
            break
        else:
            ret, frame = video_capture.read()
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
                        
                        generate_report(name, fn)


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/telemetry")
def telemetry():
    return render_template('telemetry.html')

@app.route("/start_script")
def start_script():
    print('Starting Script...')
    system('py -3 v1.py')
    return "Start Script"

@app.route("/telemetry_update")
def telemetry_update():
    print('updating telemetry info')
    battery = randint(10,100)
    speed = randint(0,10)
    flight_time = randint(0,20)
    height = randint(0,400)
    attitude = randint(0,1000)

    data = {
        'battery': battery,
        'speed': speed,
        'flight_time': flight_time,
        'height': height,
        'attitude': attitude,
    }

    json_data = jsonify(data)

    return json_data

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    
    lr, fb, ud, yv = 0, 0, 0, 0
    # me = tello.Tello()
    # video_capture = cv2.VideoCapture('tv2.mp4')
    video_capture = cv2.VideoCapture("udp://@0.0.0.0:11111")

    # me.connect()
    # me.streamoff()
    # sleep(2)
    # me.streamon()

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
    
    me = tello.Tello()
    me.connect()
    print('Tello stream on.....')
    me.streamon()



    app.run(debug=True)
