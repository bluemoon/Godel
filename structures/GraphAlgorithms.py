# -*- coding: utf-8 -*-
from structures.graph_algorithms.clustering import Clustering
from structures.graph_algorithms.page_rank  import PageRank
from structures.graph_algorithms.SVD        import SVD

class GraphAlgorithms:
    def __init__(self):
        self.clustering = Clustering()
        
    def cluster(self, G, cType=None, k=3):
        if cType == 'kmeans':
            return self.clustering.kMeans(G, k)
    
    def pageRank(self, G, **kwargs):
        pr = PageRank()
        pr.pageRank(G, **kwargs)
        
    def SVD(self, G, Node=None):
        svd = SVD()

        if not Node:
            return svd.SVD_each(G)
        else:
            return svd.SVD(G)

