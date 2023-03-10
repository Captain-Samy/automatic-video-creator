import os
import subprocess
import sys
import threading

from flask import Flask, Response, request, render_template, send_file


app = Flask(__name__)

#First Page to start at / = nothing. It renders the index.html file.
@app.route('/')
def index():
    return render_template('index.html', openAiApiKey = loadOpenAiApiKey())

# Complicated shit which does the backend for the terminal 
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


# This leds us run the script and push the arguments to it 
@app.route('/run_script')
def run_script_route():
    arg1 = request.args.get('arg1') # textprompt
    arg2 = request.args.get('arg2') # videoLink
    arg3 = request.args.get('arg3') # themelink 
    arg4 = request.args.get('arg4') # possibleNewApiKey
    keyComparer(arg4)
    arg4 = loadOpenAiApiKey()

    command = ['python', 'scripts/videoCreator/videoCreator.py', arg1, arg2, arg3, arg4] # create the command for the popen subprocess which also pushs the argument 
    return Response(run_script(command), mimetype='text/html') # does the response to the frontend/client-side and also starts the script

#Download function whichs sends the mp4 file to the client 
@app.route('/download_file')
def download_file():
    return send_file('output.mp4', as_attachment=True)

#loads Api Key from txt file
def loadOpenAiApiKey ():
        with open('openAiKey.txt', 'r') as file:
             key = file.read()
        return key

def keyComparer (possibleNewKey): 
    if loadOpenAiApiKey() != possibleNewKey:
        data = open('openAiKey.txt', 'w') 
        data.truncate(0)
        data.write(possibleNewKey)
        print("API KEY changed")
               



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
