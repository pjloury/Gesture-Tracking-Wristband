#Written by Yanming Chen and Jiarong Fu
#Berkeley EECS 249, Fall 2013

import sys
import serial
import array
import time
import math
import numpy as np

# enum states
class states:
    initial,ready,steady,go,finish = range(5)

class gestures:
    none,up,down,right,left,front,back = range(7)

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
sleep = False
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
    nlabels = 7
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

######################################################
# start processing
######################################################
theta = read_params('thetaExperiment.txt')
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
            gesture = 'up'
        elif p == gestures.down:
            gesture = 'down'
        elif p == gestures.right:
            gesture = 'right'
        elif p == gestures.left:
            gesture = 'left'
        elif p == gestures.front:
            gesture = 'front'
        elif p == gestures.back:
            gesture = 'back'
        else:
            gesture = 'none'
        
        if sleep:
            gesture = 'Tap to Activate'
        print(gesture)
        
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

