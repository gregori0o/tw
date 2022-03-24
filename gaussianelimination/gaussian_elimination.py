#!/usr/bin/python

from concurrent.futures import ThreadPoolExecutor
from random import shuffle
import numpy as np


class Scheduler:
    def __init__ (self, m = 8):
        self.tasks = []
        self.max = m
        
    def add_task (self, task, *args):
        self.tasks.append((task, *args))
        
    def run (self):
        #shuffle(self.tasks)
        with ThreadPoolExecutor (max_workers=self.max) as executor:
            for task in self.tasks:
                executor.submit(*task)
        self.clear()
        
    def clear (self):
        self.tasks = []


class GaussianElimination:
    def __init__ (self, M, N):
        self.M = M
        self.N = N
        self.m = np.zeros ((N,N))
        self.d = np.zeros ((N,N+1,N))

    def taskA (self, i, k):
        self.m[i,k] = self.M[k,i] / self.M[i,i]
    
    def taskB (self, i, j, k):
        self.d[i,j,k] = self.M[i,j] * self.m[i,k]
    
    def taskC (self, i, j, k):
        self.M[k,j] -= self.d[i,j,k]
    
    def normalise_matrix (self):
        for i in range (self.N):
            self.M[i, i:] /= self.M[i,i]
        return self.M
    
    def backward_sub (self):
        for k in range (self.N-1,-1,-1):
            for i in range (k):
                m = self.M[i,k] / self.M[k,k]
                self.M[i,k:] -= self.M[k,k:] * m
        return self.M

    def run (self):
        scheduler = Scheduler (self.N)
        for i in range (self.N):
            for k in range (i+1, self.N):
                scheduler.add_task(self.taskA, i, k)
            scheduler.run()
            for k in range (i+1, self.N):
                for j in range (i, self.N+1):
                    scheduler.add_task(self.taskB, i, j, k)
            scheduler.run()
            for k in range (i+1, self.N):
                for j in range (i, self.N+1):
                    scheduler.add_task(self.taskC, i, j, k)
            scheduler.run()
        self.M = self.normalise_matrix()
        self.M = self.backward_sub()
        return self.M


def parse_matrix (filepath = "in.txt"):
    with open (filepath) as f:
        f = list(f)
        N = int(f[0])
        M = []
        for line in f[1:N+1]:
            arr = []
            for el in line.split():
                arr.append(float(el))
            M.append(arr)
        for i, el in enumerate (f[N+1].split()):
            M[i].append(float(el))
    return np.array(M), N

def save_matrix (M, N, filepath="solved.txt"):
    f = open (filepath, 'w')
    f.write(str(N) + '\n')
    for line in M:
        for el in line[:-1]:
            f.write(str(el) + ' ')
        f.write('\n')
    for el in M[:,-1]:
        f.write(str(el) + ' ')
    f.write('\n')
    f.close()


def make_test (filepath_source = "in.txt", filepath_result = "solved.txt", filepath_check = "out.txt"):
    M, N = parse_matrix(filepath_source)
    TASK = GaussianElimination (M, N)
    M = TASK.run()
    save_matrix(M, N, filepath_result)
    K, _ = parse_matrix(filepath_check)
    return np.allclose(M, K)


if __name__ == '__main__':
	b = make_test ()
	if b:
		print ("Elimnacja Gaussa przebiegła prawidłowo")
	else:
		print ("Otrzymano błędny wynik")