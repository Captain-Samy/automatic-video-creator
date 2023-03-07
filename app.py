from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("/index.html")


@app.route('/run_videoCreator')
def run_script():
    query_string = request.query_string.decode()
    print(query_string)
    arg1 = request.args.get("arg1")
    print("arg1: " + arg1)
    arg2 = request.args.get("arg2")
    print("arg2:  " + arg2)
    arg3 = request.args.get("arg3")
    print("arg3: " + arg3)
    subprocess.run(['python', 'scripts/videoCreator/videoCreator.py', arg1, arg2, arg3])
    return 'Script executed successfully!'