#Written by Yanming Chen and Jiarong Fu
#Berkeley EECS 249, Fall 2013

import sys
import serial
import array
import time
import math
import numpy as np
from subprocess import Popen, PIPE

# enum states
class states:
    initial,ready,steady,go,finish = range(5)

class gestures:
    none,up,down,right,left,front,back,tap = range(8)

# struct used for feature and window
class fstruct:
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []


def startAccessPoint():
    return array.array('B', [0xFF, 0x07, 0x03]).tostring()
 
def accDataRequest():
    return array.array('B', [0xFF, 0x08, 0x07, 0x00, 0x00, 0x00, 0x00]).tostring()

# global variables
# sleep = False
#Open port
ser = serial.Serial('/dev/tty.BTUART-DevB',9600,timeout=1)
 
#Start access point
# ser.write(startAccessPoint())


# Read accelerometer data
def readAcc(ser):
    raw = ser.readline().strip().split(",")
    # print raw
    try:
        # b = 1 # doing nothing
        if raw is not None:
            signal = [int(raw[i]) for i in range(3)]
            # print signal
    except:
        signal = None
        

    ser.flushInput()

    if not signal:
        return signal
    return (signal[0], signal[1], signal[2])

def parse_line(line):    # parse a line in text into a integer list
    line = line.strip("[]\n")
    #     line = line.replace(",","")
    retList = [float(i) for i in line.split()]
    #print(retList)    
    return retList

def read_params(filename):  # hacky
    try:
        infile = open(filename,'r')
    except:
        sys.exit('can\'t open parameter file')
    
    theta = []
    nlabels = 8
    for i in range(nlabels):
        line = infile.readline()
        
        row = np.array([])
        while True:
            line = infile.readline()
            flag = 0
            if line.endswith(']\n'):
                flag = 1
            new = np.array(parse_line(line))
            row = np.append(row,new,1)
            if flag == 1:
                break
        theta.append(row)
    
    theta = np.asarray(theta)
    return theta

# predict functions
def sigmoid(z):
    s = 1./(1+np.exp(-z))
    return s

def predict(theta,window):
    f = [float(i) for i in window.x]+[float(i) for i in window.y]+[float(i) for i in window.z]
    f = f + [1.0]     # add bias term
    f = np.matrix(f)
    
    theta = (np.matrix(theta)).T
    g = f*theta
    h = sigmoid(g)    
    h = np.asarray(h)
    p = h.argmax(1)  
    return p

def Safari_application(gesture):
    spt = ""
    if gesture == "Left":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke "[" using command down
                end tell
                '''
    elif gesture == "Right":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke "]" using command down
                end tell
                '''
    elif gesture == "Up":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke (key code 126) 
                end tell
                '''
    elif gesture == "Down":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke (key code 125) 
                end tell
                '''
    elif gesture == "Back":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke (key code 53)
                end tell
                '''
    elif gesture == "Front":
        spt += '''
                tell application "Safari"
                activate
                    tell application "System Events" to keystroke (key code 36)
                end tell
                '''
    return spt
    # implemented

def iTunes_application(gesture):
    spt = ""
    if gesture == "Left":
        spt += '''
                tell application "System Events"
                    keystroke (key code 123 using command down)
                end tell
                '''
    elif gesture == "Right":
        spt += '''
                tell application "System Events"
                    keystroke (key code 124 using command down)
                end tell
                '''
    elif gesture == "Up":
        spt += '''
                set volume output volume ((output volume of (get volume settings)) + 10)
                '''
    elif gesture == "Down":
        spt += '''
                set volume output volume ((output volume of (get volume settings)) - 10)
                '''
    elif gesture == "Back":
        spt += '''
                tell application "iTunes" to stop
                '''
    elif gesture == "Front":
        spt += '''
                tell application "iTunes" to playpause
                '''
    return spt
    # implemented

def QuickTimes_application(gesture):
    spt = ""
    if gesture == "Left":
        spt += '''
                tell application "System Events"
                    keystroke (key code 123 using command down)
                end tell
                '''
    elif gesture == "Right":
        spt += '''
                tell application "System Events"
                    keystroke (key code 124 using command down)
                end tell
                '''
    elif gesture == "Up":
        spt += '''
                set volume output volume ((output volume of (get volume settings)) + 10)
                '''
    elif gesture == "Down":
        spt += '''
                set volume output volume ((output volume of (get volume settings)) - 10)
                '''
    elif gesture == "Back":
        spt += '''
                tell application "QuickTime" to stop
                '''
    elif gesture == "Front":
        spt += '''
                tell application "QuickTime" to playpause
                '''
    return spt

def Slides_application(gesture):
    spt = ""
    spt += '''
            tell application "System Events" to keystroke (key code 124)
            '''
    return spt

def Preview_application(gesture):
    spt = ""
    if gesture == "Left":
        spt += '''
                tell application "Preview"
                activate
                    tell application "System Events" to keystroke (key code 123)
                end tell
                '''
    elif gesture == "Right":
        spt += '''
                tell application "Preview"
                activate
                    tell application "System Events" to keystroke (key code 124)
                end tell
                '''
    elif gesture == "Up":
        spt += '''
                tell application "Preview"
                activate
                    tell application "System Events" to keystroke (key code 126) 
                end tell
                '''
    elif gesture == "Down":
        spt += '''
                tell application "Preview"
                activate
                    tell application "System Events" to keystroke (key code 125) 
                end tell
                '''
    elif gesture == "Back":
        spt += '''
                tell application "Preview"
                activate
                    tell application "System Events" to keystroke "-" using command down
                end tell
                '''
    elif gesture == "Front":
        spt += '''
                tell application "Preview"
                activate 
                    tell application "System Events" to keystroke "+" using command down
                end tell
                '''
    return spt

def Finder_application(gesture):
    spt = ""
    if gesture == "Left":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke (key code 123)
                end tell
                '''
    elif gesture == "Right":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke (key code 124)
                end tell
                '''
    elif gesture == "Up":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke (key code 126) 
                end tell
                '''
    elif gesture == "Down":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke (key code 125) 
                end tell
                '''
    elif gesture == "Back":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke "w" using command down
                end tell
                '''
    elif gesture == "Front":
        spt += '''
                tell application "Finder"
                activate
                    tell application "System Events" to keystroke "o" using command down
                end tell
                '''
    return spt
    # implemented

def oascript_function_init():
    functions = '''
        to getCurrentApp()
            set front_app to (path to frontmost application as Unicode text)
            set AppleScript's text item delimiters to ":"
            set front_app to front_app's text items
            set AppleScript's text item delimiters to {""} --> restore delimiters to default value
            set item_num to (count of front_app) - 1
            set app_name to item item_num of front_app
            set AppleScript's text item delimiters to "."
            set app_name to app_name's text items
            set AppleScript's text item delimiters to {""} --> restore delimiters to default value
            set MyApp to item 1 of app_name
            return MyApp
        end getCurrentApp

        set output to (getCurrentApp())
        '''
    return functions

def read_application_name(script):
    p = Popen(['osascript'], stdin = PIPE, stdout = PIPE, stderr = PIPE)
    stdout, stderr = p.communicate(script)
    return stdout

def gesture_assigner(gesture, script):
    currentApp = (read_application_name(script)).strip()
    print "currently at: " + currentApp
    if currentApp == "Safari":
        command = Safari_application(gesture)
    elif currentApp == "iTunes":
        command = iTunes_application(gesture)
    elif currentApp == "Finder":
        print "get inside finder"
        command = Finder_application(gesture)
    elif currentApp == "Keynote":
        print "get inside Keynote"
        command = Slides_application(gesture)
    else:
        return None

    p2 = Popen(['osascript'], stdin = PIPE, stdout = PIPE, stderr = PIPE)
    stdout, stderr = p2.communicate(command)
    print gesture

######################################################
# start processing
######################################################
def start_control_session(script):
    theta = read_params('udlr_theta.txt')
    g = 64
    wlen = 25
    x = 0
    y = 0
    z = 0
    state = states.initial
    tstart = time.time()
    timer = time.time()
    window = fstruct()
    print("start")
    while (time.time()-tstart)<600:
        # state operations
        # print('state is '+str(state))
        if state == states.ready:
            ser.flushInput()
            while True:
                print '.'
                signal = readAcc(ser)
                if signal == None:
                    continue
                else:
                    x, y, z = signal
                    # print 'read successful'
                    break          
                    
        elif state == states.steady:
            # ser.flushInput()
            while True:
                signal = readAcc(ser)
                if signal == None:
                    continue
                else:
                    (x,y,z) = signal
                    break

        elif state == states.go:
            # ser.flushInput()
            while True:
                # print '.'
                signal = readAcc(ser)
                if signal:
                    # print signal
                    (x,y,z) = signal
                    # print 'read successful'
                    break
                else:
                    continue        
            window.x.append(x)
            window.y.append(y)
            window.z.append(z)
        elif state == states.finish:
            pass
        else:
            pass
                
        # state transitions
        if state == states.initial:
            next_state = states.ready
            timer = time.time()
        elif state == states.ready:
    #         print(str(x)+' '+str(y)+' '+str(z))
    #         print(math.sqrt(x**2+y**2+z**2))
            if abs(math.sqrt(x**2+y**2+z**2)-g) > 0.1*g:
                next_state = states.ready
                timer = time.time()
            else:
                if time.time()-timer > 0.5:
                    next_state = states.steady
                    timer = time.time()
                    print('ready')
                else:
                    next_state = states.ready
        elif state == states.steady:
            #print(math.sqrt(x**2+y**2+z**2))
            if abs(math.sqrt(x**2+y**2+z**2)-g) > 0.1*g:
                next_state = states.go
                timer = time.time()
            else:
                next_state = states.steady
                timer = time.time()
        elif state == states.go:
            if len(window.x) >= wlen:
                next_state = states.finish
                timer = time.time()
            else:
                next_state = states.go
        elif state == states.finish:
            # gesture recognition and actions
            p = predict(theta,window)
            
            if p == gestures.up:
                gesture = 'Up'
            elif p == gestures.down:
                gesture = 'Down'
            elif p == gestures.right:
                gesture = 'Right'
            elif p == gestures.left:
                gesture = 'Left'
            elif p == gestures.front:
                gesture = 'Front'
            elif p == gestures.back:
                gesture = 'Back'
            elif p == gestures.tap:
                gesture = 'Tap'
                # sleep = not(sleep)
            else:
                gesture = 'none'
            
            # if sleep:
                # gesture = 'Tap to Activate'
            print(gesture)
            gesture_assigner(gesture, script)
            print(window.x)
            print(window.y)
            print(window.z)
            # clear window and transit
            window.x = []
            window.y = []
            window.z = []
            next_state = states.ready
            timer = time.time()
                        
        state = next_state

    print('finish') 

functions = oascript_function_init()
start_control_session(functions)

