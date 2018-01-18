from flask import Flask

app = Flask('uqcsbot')

@app.route('/')
def index():
    return "Hello World!"
