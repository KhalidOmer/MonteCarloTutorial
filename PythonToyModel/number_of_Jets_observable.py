import heapq
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from numpy.linalg import norm
from Distributions import*
from pseudo_jets_generator import*
from partonshower3d import*
#######

def dij(Ji,Jj,p, R):
    Pi = Ji.momentum
    Pj = Jj.momentum
    pTi = np.sqrt(Pi[1]**2 + Pi[2]**2)
    #yi = 1/2 * np.log((Pi[0] + Pi[3])/(Pi[0]-Pi[3]))
    yi = 1/2 * np.log((norm(Pi[1:])+Pi[3])/(norm(Pi[1:])-Pi[3]))
    phii = np.arctan(Pi[2]/Pi[1])
    pTj = np.sqrt(Pj[1]**2 + Pj[2]**2)
    yj = (1/2) * np.log((norm(Pj[1:]) + Pj[3])/(norm(Pj[1:])-Pj[3]))
    phij = np.arctan(Pj[2]/Pj[1])
    Delij = np.sqrt((yi - yj)**2 + (phii - phij)**2)
    mini = min(pTi**(2*p), pTj**(2*p))
    di_j = mini * Delij/R
    if debug:
        if di_j != di_j:
            print("nan", Pi, Pj)
    return di_j 


#####

def Delta(x,y):
    phii = np.arctan(x[2]/x[1])
    phij = np.arctan(y[2]/y[1])
    yi = 1/2 * np.log((norm(x[1:])+x[3])/(norm(x[1:])-x[3]))
    yj = (1/2) * np.log((norm(y[1:]) + y[3])/(norm(y[1:])-y[3]))
    Delij = np.sqrt((yi - yj)**2 + (phii - phij)**2) 
    return Delij


#####

def diB(Ji, p):
    Pi = Ji.momentum
    pTi = np.sqrt(Pi[1]**2 + Pi[2]**2)
    di_B = pTi**(2*p)
    return di_B


#####

class Pseudojet:
    instances  = []
    def __init__(self, v_momentum,lista):
        self.momentum = v_momentum
        self.index = len(Pseudojet.instances)
        self.is_jet = False
        self.exists = True 
        self.list = lista
        Pseudojet.instances.append(self)

######

def combine(J1, J2,p,R,H,lis):
    J = J1.momentum + J2.momentum
    J1.exists = False
    J2.exists = False
    J  = Pseudojet(J,J1.list + J2.list)
    di_B = diB(J,p)
    heapq.heappush(H,(di_B,J.index,-1))
    for i in range(len(lis)-1):
        if lis[i].exists:
            di_j = dij(J,lis[i],p,R)
            heapq.heappush(H,(di_j,J.index,i))


######

def jetcluster(p,R,J):
    Pseudojet.instances = []
    for j in J:
        Pseudojet(j,[j])
    lis = Pseudojet.instances
    H =[]
    for i in range(len(lis)):
        di_B = diB(lis[i],p)
        heapq.heappush(H,(di_B,i,-1))
        for j in range(i+1, len(lis)):
            di_j = dij(lis[i],lis[j],p,R)
            heapq.heappush(H,(di_j,i,j))
    d, i, j = heapq.heappop(H)
    if j != -1:
        if lis[i].exists and lis[j].exists:
            combine(lis[i],lis[j],p,R,H,lis)
    else:
        if lis[i].exists:
            lis[i].exists = False
            lis[i].is_jet = True 
    while len(H) !=0:
        d, i, j = heapq.heappop(H)
        if j != -1:
            if lis[i].exists and lis[j].exists:
                combine(lis[i],lis[j],p,R,H,lis)
        else:
            if lis[i].exists:
                lis[i].exists = False
                lis[i].is_jet = True
    return [j for j in Pseudojet.instances if j.is_jet]


#######
# creating a jetty event of two partons (J) opposite to each other, a parton is rotated with (thet) and (ph) angles  
l =[]
for i in range(1000):
    thet = np.random.uniform(0,np.pi)
    ph   = np.random.uniform (0,np.pi*2)
    En   = E()
    P    = np.array([En,0,0,En])
    n    = normv(P[1:])
    rot1 = rotation(n,thet)
    rot2 = rotation(P[1:]/norm(P[1:]),ph)
    tmp  = np.dot(rot2,np.dot(rot1,P[1:]))
    tmp  = P[0]*tmp/norm(tmp)
    a    = np.array([P[0]])
    P_i  = np.concatenate((a,tmp))
    J    = partons(P_i)
    l.append(J)
	
#here clustering with different values of R. 
n =[]
#en = []	
for num, i in enumerate(l):	
	Jets = jetcluster(-1,1,i)
	#n.append(len(Jets))
	print(num, 'loop 1')
	#for i in Jets:
	#	en.append(i[0])

#en1 = []
k=[]
for num, i in enumerate(l):
	Jets = jetcluster(-1,.1,i)
	k.append(len(Jets))
	print(num, 'loop 2')
	#for i in Jets:
	#	en1.append(i[0])

en2 = []	
m = []
for num, i in enumerate(l):
	Jets = jetcluster(-1,.05,i)
	m.append(len(Jets))
	print(num, 'loop 3')
	#for i in Jets:
	#	en2.append(i[0])
with open('data3.pickle', 'wb') as f:
	pickle.dump(en, f)
	pickle.dump(en1, f)
	pickle.dump(en2, f)




#plt.hist([n, k, m], bins=30, histtype='barstacked', edgecolor=['blue', 'yellow', 'red'], label=['R=1', 'R=.1', 'R=.05'], fill = False)
#plt.xlabel('Number of Jets')
#plt.ylabel('Frequency')
#plt.legend(loc='upper right')
#plt.show()
#######
