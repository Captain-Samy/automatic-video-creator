import subprocess
import sys
import threading

from flask import Flask, Response, request, render_template


app = Flask(__name__)


def run_script(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        yield line.strip() + '<br>\n'
        sys.stdout.write(line)
        sys.stdout.flush()
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_script')
def run_script_route():
    arg1 = request.args.get('arg1')
    arg2 = request.args.get('arg2')
    arg3 = request.args.get('arg3')
    command = ['python', 'scripts/videoCreator/videoCreator.py', arg1, arg2, arg3]
    return Response(run_script(command), mimetype='text/html')


if __name__ == '__main__':
    # start a separate thread to run the Flask app
    app_thread = threading.Thread(target=app.run, kwargs={'debug': False})
    app_thread.daemon = True
    app_thread.start()

    # run the command in the main thread
    command = ['echo', 'hello', 'world']
    subprocess.run(command, check=True)

    # wait for the app thread to finish
    app_thread.join()
