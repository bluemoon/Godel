# -*- coding: utf-8 -*-
import numpy
from scipy import linalg
from scipy import dot
import scipy
import pylab

from scipy.cluster.vq import *
import sys, math, random

class PageRank:
    def _gMatrix(self, G,  alpha=0.85, nodelist=None):
        M = self.adjacencyMatrix()
        (n,m) = M.shape
        
        Danglers = numpy.where(M.sum(axis=1)==0)
        
        for d in Danglers[0]:
            M[d]=1.0/n
        
        M = M / M.sum(axis=1)
        
        P = alpha * M + (1 - alpha) * numpy.ones((n,n)) / n
        return P
    
    def pageRank(self, G,  alpha=0.85, max_iter=100, Tolerance=1.0e-6, nodelist=None):
        M = self._gMatrix(alpha, nodelist)   
        (n,m) = M.shape
        ## should be square
        x = numpy.ones((n))/n
        for i in range(max_iter):
            xlast = x
            x = numpy.dot(x,M) 
            ## check convergence, L1 norm            
            err=numpy.abs(x-xlast).sum()
            if err < n*Tolerance:
                return numpy.asarray(x).flatten()
