from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("/index.html")


@app.route('/run_videoCreator')
def run_script():
  subprocess.run(['python', 'scripts/videoCreator.py'])
  return 'Script executed successfully!'