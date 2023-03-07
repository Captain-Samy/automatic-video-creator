from flask import Flask, Response, render_template, request, stream_with_context
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("/index.html")


@app.route('/run_videoCreator')
def run_script():
    arg1 = request.args.get("arg1")
    arg2 = request.args.get("arg2")
    arg3 = request.args.get("arg3")

    command = ['python', 'scripts/videoCreator/videoCreator.py', arg1, arg2, arg3]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_lines = []

    def stream():
        for line in iter(process.stdout.readline, b''):
            output_lines.append(line.decode())
            yield line

    return Response(stream_with_context(stream()), mimetype='text/plain')