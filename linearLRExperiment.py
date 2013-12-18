import sys
import numpy as np
from scipy import optimize as op


# global variables
UP = 1
DOWN = 2
RIGHT = 3
LEFT = 4
FRONT = 5
BACK = 6
NONE = 0

G = 50

class fstruct:
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []

def parse_line(line):    # parse a line in text into a integer list
    line = line.strip("xyz: []\n")
    line = line.replace(",","")
    retList = [float(i) for i in line.split()]
    #print(retList)    
    return retList

def read_data(filename):
#     filename = 'data_set_1.txt'
    print('reading from file: '+filename)
    try:
        infile = open(filename,'r')
    except:
        sys.exit(filename+' can\'t be opened')
    
    data = []
    label = []
    count = 0
    while True:
        # read label
        line = infile.readline()
        if line == 'up\n':
            label.append(UP)
        elif line == 'down\n':
            label.append(DOWN)
        elif line == 'right\n':
            label.append(RIGHT)
        elif line == 'left\n':
            label.append(LEFT)
        elif line == 'front\n':
            label.append(FRONT)
        elif line == 'back\n':
            label.append(BACK)
        elif line == 'none\n':
            label.append(NONE)
        elif line == '':
            break
        else:
            print(line)
            sys.exit('file format doesn\'t match')
        
        # form feature vector
        fv = []
        for i in range(3):
            line = parse_line(infile.readline())
            fv = fv+line
        data.append(fv)
        count += 1
        print(count)
    
    # conform data into matrices    
    data = np.matrix(data)/G
    label = np.matrix(label)
    label = label.transpose()
#     data = data.T
       
    return (data,label)

def write_data(theta):
    filename = 'thetaExperiment.txt'
    try:
        outfile = open(filename,'w')
    except:
        sys.exit('can\'t creat output file')
    
    nlabels = 7
    for i in range(7):
        if i == 0:
            outfile.write('none: \n')
        elif i == 1:
            outfile.write('up: \n')
        elif i == 2:
            outfile.write('down: \n')
        elif i == 3:
            outfile.write('right: \n')
        elif i == 4:
            outfile.write('left: \n')
        elif i == 5:
            outfile.write('front: \n')
        else:
            outfile.write('back: \n')
#         outfile.write(str(list(theta[i]))+'\n')
        outfile.write(str(theta[i])+'\n')
    
    return


def sigmoid(z):
    s = 1./(1+np.exp(-z))
    return s

def cost_function(theta,x,y,l):
    (m,n) = x.shape
    theta = (np.matrix(theta)).T
    g = x*theta
    h = sigmoid(g)
#     j = -(1/m)*((np.log(h).T)*y+(np.log(1-h).T)*(1-y))+0.5*l*(theta.T*theta)/m
#     j1 = (np.log(h).T)*y
#     j2 = (np.log(1-h).T)*(1-y)
#     j3 = j1+j2
#     j4 = -(1/m)*j3
#     j5 = 0.5*l*(theta.T*theta)/m
#     j6 = j4+j5
    j = -((np.log(h).T)*y+(np.log(1-h).T)*(1-y))/m+0.5*l*(theta.T*theta)/m
        
    return j

def d_cost_function(theta,x,y,l):
    (m,n) = x.shape     
    theta = (np.matrix(theta)).T
#     print(x.shape)
#     print(theta.shape)
    g = x*theta
    h = sigmoid(g)
    dj = (x.T*(h-y)+l*theta)/m
    dj = np.asarray(dj).flatten()  
    return dj

def predict_single(theta,x):
    theta = (np.matrix(theta)).T
    g = x*theta
    h = sigmoid(g)
    p = h > 0.5
    return p

def predict_all(theta,x):
    theta = (np.matrix(theta)).T
    g = x*theta
    h = sigmoid(g)    
    h = np.asarray(h)
    p = h.argmax(1)    
    return p

def train(initial_theta,x,y,l):
    nlabels = 7
    n = len(initial_theta)
    theta = []
    for i in range(nlabels):
        y_l = y==i
        theta.append(op.fmin_cg(f=cost_function,x0=initial_theta,args=(x,y_l,l),fprime=d_cost_function))
    theta = np.asarray(theta)
    return theta

##################################################################
print('starting...')
train_file = 'data/experiment_data.txt'
test_file = 'data/experiment_data.txt'

(x,y) = read_data(train_file)

(x0,y0) = read_data(test_file)

# prepare train set
l = 0.1     # regularization parameter
(m,n) = x.shape
col = np.matrix(np.ones((m,1),dtype=np.float))  # add bias
x = np.append(x,col,1)

# prepare test set
(m0,n0) = x0.shape
col0 = np.matrix(np.ones((m0,1),dtype=np.float))
x0 = np.append(x0,col0,1)

# initial_theta = np.asarray(np.matrix(np.zeros((n+1,1),dtype=np.float)))
initial_theta = np.zeros((1,n+1),dtype=np.float)

theta_all = train(initial_theta,x,y,l)
# print(theta_all)
p_all = predict_all(theta_all,x0)
p_all = (np.matrix(p_all)).T
print(p_all.shape)
result = np.append(p_all,y0,1)
print(result)

write_data(theta_all)


# # single label prediction
# y = y==UP       # pick label
# # print(y)
# theta = op.fmin_cg(f=cost_function,x0=initial_theta,args=(x,y,l),fprime=d_cost_function)
# # theta = op.fmin_cg(f=cost_function,x0=initial_theta,args=(x,y,l))
# j = cost_function(theta,x,y,l)
# dj = d_cost_function(theta,x,y,l)

#print(theta)

# # check single prediction
# p = predict_single(theta,x)
# result = np.append(p,y,1)
# result = np.asarray(result)
# print(result)