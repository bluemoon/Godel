# -*- coding: utf-8 -*-
import numpy

from scipy import linalg
from scipy import dot
from scipy.cluster.vq import vq, kmeans, whiten, kmeans2

class Clustering:
    def _kInit(self, kFeatures, k):
        '''
        init k seeds according to kmeans++
        from: http://blogs.sun.com/yongsun/entry/k_means_and_k_means    
        '''
            
        n = kFeatures.shape[0]
            
        'choose the 1st seed randomly, and store D(x)^2 in D[]'
        centers = [kFeatures[numpy.random.randint(n)]]
        D = [numpy.linalg.norm(x-centers[0])**2 for x in kFeatures]
        
        for _ in range(k-1):
            bestDsum = bestIdx = -1
            
            for i in range(n):
                ''' Dsum = sum_{x in X} min(D(x)^2,||x-xi||^2) '''
                Dsum = reduce(lambda x,y:x + y,
                              (min(D[j], numpy.linalg.norm(kFeatures[j]-kFeatures[i])**2) for j in xrange(n)))

                if bestDsum < 0 or Dsum < bestDsum:
                    bestDsum, bestIdx  = Dsum, i

            centers.append(kFeatures[bestIdx])
            D = [min(D[i], numpy.linalg.norm(kFeatures[i]-kFeatures[bestIdx])**2) for i in xrange(n)]
            
        return numpy.array(centers)

    def kMeans(self, G, k=3, threshold=1.0e-05):
        incidence = G.incidenceList()
        
        incidence = numpy.array(incidence)
        white = whiten(incidence)

        initialCentroids = self._kInit(white, k)
        centroids, idx = kmeans2(initialCentroids, k,
                                 thresh=threshold,
                                 minit='points')
        
        """
        kmeans2 output:
          centroid : ndarray
            A k by N array of centroids found at the last iteration of k-means.
          label : ndarray
            label[i] is the code or index of the centroid the i’th observation is closest to.
        """
        
        print centroids, idx

