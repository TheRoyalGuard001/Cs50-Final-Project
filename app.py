from simulationHelpers import runRule, createGroup, resetGroup
from sharedVars import allGroups, setReflection, getReflection
# Frame rate here for easy acsess
FRAME_RATE = 60
#set up the groups before anything else
yellow = []
red = []
green = []
# consolodate groups for later
allGroups.append(yellow)
allGroups.append(red)
allGroups.append(green)

from flask import Flask, render_template # basic flask
from flask_socketio import SocketIO, emit # socketIO for seamless communication
import time, json # time for threads and json to send data
from threading import Thread, Event # threads to have the simulation go no matter what

app = Flask(__name__) # flask/socketIO setup
socketio = SocketIO(app)

# Old runFrame function. Had to set all rules manually. Used to test before finishing the UI.
# def runFrame():
#     while True:
#         data = []
#         runRule(red, red, -.3)
#         runRule(red,green,-.2)
#         runRule(green, green, -.1)
#         runRule(green,red, .5)
#         data.append(red)
#         data.append(green)
#         jsonified_data = json.dumps([data])  # Wrap the data in a list
#         socketio.emit('message', jsonified_data)
#         time.sleep(1/FRAME_RATE)  # Adjust the sleep time for your desired frame rate
# frameThread = Thread(target=runFrame)
# frameThread.start()


@app.route("/") # Basic display
def index():
    return render_template("index.html")

@socketio.on('reset-page') # Reset when recive reset message from client
def handle_event():
    for group in allGroups:
        group = resetGroup(group)

# OVERVEIW:
# This function takes the data from the 2nd form and updates the groups accordingly
@socketio.on('atom-changes')
def handle_changing_atoms(data):
    global red, green, yellow # Use global vars so other funcs have acsess to the info we change here
    redFlag = True if data['red-activate-form'] == 'on' else False # Check if the checkboxes are checked (say that 5 times fast)
    greenFlag = True if data['green-activate-form'] == 'on' else False
    yellowFlag = True if data['yellow-activate-form'] == 'on' else False

    if redFlag == True: # If red is activated, create a new group with all the values sent from the client (same for green/yellow)
        try:
            red = createGroup(int(data['red-number-form']), 'red', int(data['red-size-form']), int(data['red-range-form']))
            allGroups.append(red)
            print('red group changed')
        except:
            print('trouble creating red group')
    else: # If the user did not check the box, disable the group
        red = []
    if greenFlag == True:
        try:
            green = createGroup(int(data['green-number-form']), 'green', int(data['green-size-form']), int(data['green-range-form']))
            allGroups.append(green)
            print('green group changed')
        except:
            print('trouble creating green group')
    else:
        green = []
    if yellowFlag == True:
        try:
            yellow = createGroup(int(data['yellow-number-form']), 'yellow', int(data['yellow-size-form']), int(data['yellow-range-form']))
            allGroups.append(yellow)
            print('yellow group changed')
        except:
            print('trouble creating yellow group')
    else:
        yellow = []

    # Since REFLECTION_BOUNCE is used here and in simulationHelpers.py, to avoid any
    # import loops we connect the two through sharedVars.py and only
    # can acsess/change the var through get/setReflection().
    if data['reflection-strength'] != "":
        setReflection(data['reflection-strength'])
        print('reflection now =', getReflection())

    if data['frame-rate-change'] != "":
        global FRAME_RATE
        FRAME_RATE = int(data['frame-rate-change'])
        print('FRAME_RATE now =', FRAME_RATE)

    # SLOW var discontinued since it made simulation less fun
    # if data['slow-form'] != "":
    #     setSlow(float(data['slow-form']))
    #     print('SLOW NOW =', getSlow())
    # Same reasononing is applied for relfection off walls

# Setup for the threading we are about to do
stop_event = Event()
frameThread = None

# OVERVEIW:
# This func will take any attraction inputted through
# the sliders and 'run the rule' (aka apply that attraction).
# since we dont know if the user wants any attraction between
# any 2 groups, we have 9 one line if-else statements because if the attraction is 0,
# there is no point in spending time to calculate the attraction.
# Finally, it will package it all up in a json file and send it over clientside.
def runFrame(passedData):
    while not stop_event.is_set(): # this is here so we can later manually stop it and change the attractions
        global red, green, yellow
        sendingData = []
        runRule(red,red,passedData['red-red-attraction']) if passedData['red-red-attraction'] != 0 else None
        runRule(red,green,passedData['red-green-attraction']) if passedData['red-green-attraction'] != 0 else None
        runRule(red,yellow,passedData['red-yellow-attraction']) if passedData['red-yellow-attraction'] != 0 else None
        runRule(green,red,passedData['green-red-attraction']) if passedData['green-red-attraction'] != 0 else None
        runRule(green,green,passedData['green-green-attraction']) if passedData['green-green-attraction'] !=0 else None
        runRule(green,yellow,passedData['green-yellow-attraction']) if passedData['green-yellow-attraction'] !=0 else None
        runRule(yellow,red,passedData['yellow-red-attraction']) if passedData['yellow-red-attraction'] != 0 else None
        runRule(yellow,green,passedData['yellow-green-attraction']) if passedData['yellow-green-attraction'] != 0 else None
        runRule(yellow,yellow,passedData['yellow-yellow-attraction']) if passedData['yellow-yellow-attraction'] != 0 else None
        sendingData.append(red)
        sendingData.append(green)
        sendingData.append(yellow)
        jsonified_data = json.dumps([sendingData])  # Wrap the data in a list
        socketio.emit('message', jsonified_data)
        global FRAME_RATE
        time.sleep(1/FRAME_RATE)  # Adjust the sleep time

@socketio.on('attraction-changes')
def handle_changing_attractions(collectedData):
    global stop_event # These are coming back from before
    global frameThread

    if frameThread is not None:
        stop_event.set()  # Signal the thread to stop
        frameThread.join()  # Wait for the thread to finish

    stop_event.clear()  # Reset the stop event
    frameThread = Thread(target=runFrame, args=(collectedData,)) # setup the thread w/ the new info
    frameThread.start()

# Rest of these are basic Flask/socketIO tools
@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
