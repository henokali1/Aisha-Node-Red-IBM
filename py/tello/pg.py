from flask import Flask
from os import system
app = Flask(__name__)

@app.route("/")
def hello():
    system('py -3 pg2.py')
    return "Hello!"

if __name__ == "__main__":
    app.run()
