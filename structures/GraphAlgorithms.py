# -*- coding: utf-8 -*-
import numpy
from scipy import linalg
from scipy import dot
import scipy
import pylab

from scipy.cluster.vq import *
import sys, math, random

## Original: http://www.ece.arizona.edu/~denny/python_nest/graph_lib_1.0.1.html
## Modifications: Alex Toney
#

class GraphAlgorithms:
    def clustering(self, G):
        pass
    
    def kInit (self, X, k):
        'init k seeds according to kmeans++'
        n = X.shape[0]
        
        'choose the 1st seed randomly, and store D(x)^2 in D[]'
        centers = [X[numpy.random.randint(n)]]
        D = [numpy.linalg.norm(x-centers[0])**2 for x in X]
        
        for _ in range(k-1):
            bestDsum = bestIdx = -1
            
            for i in range(n):
                ''' Dsum = sum_{x in X} min(D(x)^2,||x-xi||^2) '''
                Dsum = reduce(lambda x,y:x+y,
                              (min(D[j], numpy.linalg.norm(X[j]-X[i])**2) for j in xrange(n)))

                if bestDsum < 0 or Dsum < bestDsum:
                    bestDsum, bestIdx  = Dsum, i

            centers.append (X[bestIdx])
            D = [min(D[i], numpy.linalg.norm(X[i]-X[bestIdx])**2) for i in xrange(n)]

        return numpy.array(centers)

    def kMeans(self, G, k=3, threshold=0.5):
        incidence = G.incidenceList()
        
        incidence = numpy.array(incidence)
        white = whiten(incidence)
        book = array((white[0], white[2]))

        res,idx = kmeans(incidence, k)         
        print res, idx


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

    def SVD(self, Node, dropAlpha=0.90):
        """
        Singular value decomposition for *Node*
        :param Node: the node you want to run SVD on.
        :param dropAlpha: the cosine similiarity limit.

        As you know the SVD will give you a product :math:`A = U∑V*`,
        where the columns of U consists of left singular vectors
        for each respective singular value σ.
        """

        incidMatrix = self.incidenceMatrix()
        ## |V| = nodeCount
        nodeCount = self.number_of_nodes()
        ## |E| = edgeCount
        edgeCount = self.number_of_edges()+1
        
        ## dont run if it will just fail;
        if nodeCount < 3 and edgeCount < 3:
            return
        

        
        ## Create the edge incidence matrix
        U, S, Vh = linalg.svd(incidMatrix)
        Vt = Vh.T

        diagMatrix = linalg.diagsvd(S,len(incidMatrix),len(Vh))

        nSigma = diagMatrix
        U2   = numpy.mat(U)
        V2   = numpy.mat(Vh)
        Eig2 = numpy.mat(nSigma)

        if not Node:
            nodeList = self.nodes.items()
            curNode = nodeList.pop(0)[0]
        else:
            curNode = Node
            
        newNode = self.incidenceOfNode(curNode, edgeCount)
        if newNode == None:
            return
        
        if Eig2.shape[0] == Eig2.shape[1]:
            ## this shape is useless to us, singular matrix
            return
        
        U    = U2.T
        Eig  = Eig2.I.T
        node = newNode.T

        ## debug(U.shape, prefix="U")
        ## debug(Eig2.shape, prefix="Eig")
        ## debug(node.shape, prefix="node")
        ## debug(incidMatrix.shape, prefix="IncidenceMatrix")
        
        node = node * U * Eig2
        
        each = {}
        count = 0
        
        for x in V2:
            cosineSim = (node * x.T) / (linalg.norm(x) * linalg.norm(node))
            if cosineSim > dropAlpha:
                each[self.nodeByNodeNum(count)] = cosineSim.A.tolist()[0][0]

            count += 1
            
        return each
            
    def SVD_each(self):
        """ run SVD on every item in the graph return
        a list which corresponds to a dict of each SVD """
        nodeList = self.nodes.items()
        each = []
        
        while nodeList:
            curNode = nodeList.pop(0)[0]
            currentSVD = self.SVD(Node=curNode)
            each.append({curNode:currentSVD})

        return each
