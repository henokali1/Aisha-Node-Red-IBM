import base64
import requests
from datetime import datetime

def upload_rec_face():
    with open("imgs/test.jpg", "rb") as file:
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

def generate_report(convict_name):
    cdt = get_current_date_time()
    lm = get_last_mission()
    convict_info = get_convict_info(convict_name)
    officer_name = get_last_login()
    detected_face_img = upload_rec_face()
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

# print(generate_report('Obama'))
