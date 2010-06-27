# -*- coding: utf-8 -*-
import numpy
from scipy import linalg
from scipy import dot

import scipy
import pylab

from scipy.cluster.vq import *
import sys, math, random

class SVD:
    def SVD(self, G,  Node, dropAlpha=0.90):
        """\
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
            
    def SVD_each(self, G):
        """ run SVD on every item in the graph return
        a list which corresponds to a dict of each SVD """
        nodeList = G.nodes.items()
        each = []
        
        while nodeList:
            curNode = nodeList.pop(0)[0]
            currentSVD = self.SVD(Node=curNode)
            each.append({curNode:currentSVD})

        return each
