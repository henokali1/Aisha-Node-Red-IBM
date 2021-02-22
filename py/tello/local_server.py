from flask import Flask
from os import system
from flask import jsonify,render_template
from time import time
from random import randint


app = Flask(__name__)

@app.route("/")
def hello():
    return 'hello'

@app.route("/telemetry")
def telemetry():
    return render_template('telemetry.html')

@app.route("/start_script")
def start_script():
    print('Starting Script...')
    system('py -3 pg2.py')
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

if __name__ == "__main__":
    app.run(debug=True)
