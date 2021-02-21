from flask import Flask
from os import system
from flask import jsonify,render_template
from time import time

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
    data = {'battery': 97, 'height': 33, 'time': str(time())}
    json_data = jsonify(data)
    return json_data

if __name__ == "__main__":
    app.run(debug=True)
