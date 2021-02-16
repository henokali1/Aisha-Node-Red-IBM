import requests
from os import listdir,remove
from os.path import isfile, join

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

download_faces()