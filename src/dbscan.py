
'''
% -------------------------------------------------------------------------
% Function: [class,type, Eps]=dbscan(x,k,Eps)
% -------------------------------------------------------------------------
% Aim:
% Clustering the data with Density-Based Scan Algorithm with Noise (DBSCAN)
% -------------------------------------------------------------------------
% Input:
% x - data set (m,n); m-objects, n-variables
% k - number of objects in a neighborhood of an object
% (minimal number of objects considered as a cluster)
% Eps - neighborhood radius, if not known avoid this parameter or put []
% -------------------------------------------------------------------------
% Output:
% class - vector specifying assignment of the i-th object to certain
% cluster (m,1)
% type - vector specifying type of the i-th object
% (core: 1, border: 0, outlier: -1)
% -------------------------------------------------------------------------
% Example of use:
% x=[randn(30,2)*.4;randn(40,2)*.5+ones(40,1)*[4 4]];
% [class,type, Eps]=dbscan(x,5,[]);
% -------------------------------------------------------------------------
% References:
% [1] M. Ester, H. Kriegel, J. Sander, X. Xu, A density-based algorithm for
% discovering clusters in large spatial databases with noise, proc.
% 2nd Int. Conf. on Knowledge Discovery and Data Mining, Portland, OR, 1996,
% p. 226, available from:
% www.dbs.informatik.uni-muenchen.de/cgi-bin/papers?query=--CO
% [2] M. Daszykowski, B. Walczak, D. L. Massart, Looking for
% Natural Patterns in Data. Part 1: Density Based Approach,
% Chemom. Intell. Lab. Syst. 56 (2001) 83-92
% -------------------------------------------------------------------------
% Written by Michal Daszykowski
% Department of Chemometrics, Institute of Chemistry,
% The University of Silesia
% December 2004
% http://www.chemometria.us.edu.pl

ported to python Dec, 2008 by Brian H. Clowers, Pacific Northwest National Laboratory.
Dependencies include scipy, numpy, and hcluster. Note the function now returns a boolean
stating whether the process was a successfully completed.

'''
import sys

import numpy as N
import hcluster as H
import scipy.special as special


def set2List(indArray):
    ind = []
    for item in indArray:
        ind.append(item.tolist())

    return ind

def dbscan(x,k,Eps = None, distMethod = 'euclidean'):
    try:
        m = x.shape[0]
        if Eps == None:
            Eps = epsilon(x,k)
        dist = H.squareform(H.pdist(x, distMethod))

        x = N.column_stack((N.arange(0,m),x))
        if len(x.shape)>1:
            m,n = x.shape
        else:
            m = x.shape[0]
            n == 1
        type = N.zeros(m)
        touched = N.zeros(m)
        no = 1

        tType = N.zeros(m)
        cClass = N.zeros(m)

        for i in xrange(m):
            if touched[i] == 0:
                ob = x[i]
                D = dist[ob[0]]
                ind = N.where(D<=Eps)
                ind = set2List(ind)[0]

                if len(ind)>1 and len(ind)<(k+1):
                    tType[i] = 0
                    cClass[i] = 0

                if len(ind) == 1:
                    tType[i] = -1
                    cClass[i] = -1
                    touched[i] = 1

                if len(ind) >= k+1:
                    tType[i] = 1
                    cClass[ind] = N.ones(len(ind))*no

                    for l in ind:
                        ob2 = x[l]
                        touched[l]=1
                        D2 = dist[ob2[0]]
                        i1 = N.where(D2<=Eps)
                        i1 = set2List(i1)[0]
                        if len(i1) > 1:
                            cClass[i1] = no
                            if len(i1)>=k+1:
                                tType[ob2[0]] = 1
                            else:
                                tType[ob2[0]] = 0

                            for j in xrange(len(i1)):
                                if touched[i1[j]] == 0:
                                    touched[i1[j]]=1
                                    ind.append(i1[j])
                                    cClass[i1[j]] = no

                    no+=1
        i1 = N.where(cClass == 0)
        i1 = set2List(i1)[0]
        cClass[i1] = -1
        tType[i1] = -1
        return cClass, tType, Eps, True
    except:
        errorMsg ="An error occured with the DBSCAN Algorithm"
        errorMsg += "Sorry: %s\n\n%s\n"%(sys.exc_type, sys.exc_value)
        print errorMsg

        return None,None,None,False

'''
%...........................................
function [Eps]=epsilon(x,k)

% Function: [Eps]=epsilon(x,k)
%
% Aim:
% Analytical way of estimating neighborhood radius for DBSCAN
%
% Input:
% x - data matrix (m,n); m-objects, n-variables
% k - number of objects in a neighborhood of an object
% (minimal number of objects considered as a cluster)
'''
def epsilon(x,k):
    if len(x.shape)>1:
        m,n = x.shape
    else:
        m = x.shape[0]
        n == 1
    prod = N.prod(x.max(axis = 0)-x.min(axis = 0))
    gamma = special.gamma(0.5*n+1)
    denom = (m*N.sqrt(N.pi**n))
    modifier = 1/n
    Eps = ((prod*k*gamma)/denom)**(1.0/n)

    return Eps

'''
NOTE: In python this function is replaced with the hcluster module
which adds more flexibility in the distance calculation method.
%............................................
function [D]=dist(i,x)

% function: [D]=dist(i,x)
%
% Aim:
% Calculates the Euclidean distances between the i-th object and all objects in x
%
% Input:
% i - an object (1,n)
% x - data matrix (m,n); m-objects, n-variables
%
% Output:
% D - Euclidean distance (m,1)


'''




if __name__ == "__main__":
    import pylab as P
    import scipy as S
    x1 = S.rand(30,2)*2
    x2 = (S.rand(40,2)*0.5+1)*4
    xy= N.concatenate((x1,x2))
    P.scatter(xy[:,0],xy[:,1], alpha =  0.5)
#    [class,type, Eps]=dbscan(x,5,[]);

#    % x=[randn(30,2)*.4;randn(40,2)*.5+ones(40,1)*[4 4]];
#% [class,type, Eps]=dbscan(x,5,[]);

#    xy = P.load('RawPeaks.csv', delimiter = ',')

#    distThresh = N.arange(1,20)
#    cMax = []
#    EpsArray = []
#    for i in distThresh:
#        cClass, tType, Eps, boolAns = dbscan(xy[:,0:2], i)
#        cMax.append(cClass.max())
#        EpsArray.append(Eps)
#
#    P.plot(distThresh,cMax)
#    P.figure()
#    P.plot(distThresh,EpsArray)
#    P.plot(cMax,EpsArray)

#    P.plot(xy[:,0],xy[:,1],'ro', alpha = 0.6)
#    cClass, tType, Eps, boolAns = dbscan(xy[:,0:2], 1)
    xy = N.column_stack((xy[:,0],xy[:,1]))
    cClass, tType, Eps, boolAns = dbscan(xy, 5)
    print cClass.max(), len(tType)
    i = cClass.max()
    for m in xrange(int(i)+1):
        ind = N.where(m == cClass)
        temp = xy[ind]
        P.plot(temp[:,0],temp[:,1],'s', alpha = 0.7, ms = 3)


    P.show()
