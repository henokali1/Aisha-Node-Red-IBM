from flask import Flask,jsonify,render_template
from random import randint
from os import system
import pickle



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
    system('py -3 v3.py')
    return "Start Script"

@app.route("/telemetry_update")
def telemetry_update():
    print('updating telemetry info')
    battery = randint(10,100)
    speed = randint(0,10)
    flight_time = randint(0,20)
    height = randint(0,400)
    attitude = randint(0,1000)

    with open('telemetry.pickle', 'rb') as handle:
        data = pickle.load(handle)
    json_data = jsonify(data)
    return json_data


if __name__ == "__main__":
    app.run(debug=True)
