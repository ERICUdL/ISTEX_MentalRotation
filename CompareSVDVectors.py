# -*- coding: utf-8 -*-
#
# This file is part of ISTEX_MentalRotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for
# more details.

#Load and transform Istex abstracts into doc2vec representation.


# Author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author: Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2

# Thanks to ISTEX project for the fundings

import os, argparse
import json
import pickle
import numpy
import sklearn.cluster as cl
from nltk import cluster # for the distances
from scipy.stats import itemfreq

# load the keys that are the SOURCE+DOI of the documents
# source can be UCBL or Istex, UCBL can also contain documents that are in istex but none of the istex documents are in the UCBL corpus 
def keysloadKeys(keysFile) :
	f=open(keysFile)
	dictkeys = json.load(f)
	f.close()
	return dictkeys

#
def SmallBallEnvelop(vectors) :# vectors suppose to be numpy array, list of vectors
	return (vectors.min(axis=0)+vectors.max(axis=0))/2.

def Barycenter(vectors) : # vectors suppose to be numpy array, list of vectors
	return vectors.sum(axis=0)/float(len(vectors)) 

def VectorsCosinusDistances(center, vectors) : # vectors is supposed to be a simple vector
	distances = dict()
	for i in range(len(vectors)) :
		distances[i]=(cluster.util.cosine_distance(center,vectors[i])) # cosine_distance return the similarity, so 1- u.v/|u||v|
	return distances

def VectorsEuclideanDistances(center, vectors) : # vectors is supposed to be a simple vector
	distances = dict()
	for i in range(len(vectors)) :
		distances[i]=(cluster.util.euclidean_distance(center,vectors[i])) # cosine_distance return the simimlarity, so 1- u.v/|u||v|
	return distances

# gives the standard deviation of dictances
def StandardDeviation (distances):
	return numpy.std(distances)

def DistancesFrequencies (distances) :
	return itemfreq(distances.values()) # return [[val,freq],[val2,freq2]] in sorted order from the smallest value


def splitKeysCorpus(dictKeys) :
	ucblkeys = dict()
	istexkeys = dict()
	countUcbl = 0
	countIstex = 0 
	for k in dictKeys :
		if k.find("UCBL") == 0 : # found UCBL at 0 position
			ucblkeys[k] = (dictKeys[k], countUcbl )
			countUcbl += 1
		else : 
			istexkeys[k] = (dictKeys[k], countIstex) # (doc2vec id, id for the splitted corpus)
			countIstex += 1
	return (ucblkeys, istexkeys)

def loadModel(ModelFile) :
	return Doc2Vec.load(ModelFile)

def extractMatrix(model, list_keys, which_index=1) : # be carreful to extract the matrix in the index order (0 for doc2vec, complete model, 1 for the selected one (ucbl or istex))
	matrix = []
	for i in sorted([ x[which_index] for x in list_keys.values() ]) :
		matrix.append(model.docvecs["DOC_%s"%i])
	return numpy.array(matrix)

def saveDistances(distances, fileName, keys, cluster = "0") : # distances is a dictionnary with documents keys (SourceDOI) and distance to the barycenter of UCBL douments (or any other distance we chosed)
	f=open(fileName, "w")
	for k in sorted(distances, key=distances.get) : # sort keys according to values	
		if str(k) in keys :
			f.write(str(k) + ", " + str(distances[k]) + " : " + keys[str(k)] + " : " + "Cluster" + str(cluster) + "\n")
		else :
			f.write(str(k) + ", " + str(distances[k]) + "\n")

	f.close()

def computeKmeans(matrix, nb_clusters = 4) :
	k_means = cl.KMeans(n_clusters=nb_clusters)
	k_means.fit(ucbl_mat)
	
	return k_means

#make the list of the index of documents of cluster number cluster_index, given by the user
def ListSameCluster(cl_labels, cluster_index = 0) :
	l = []
	for i in range(len(cl_labels)) :
		if cl_labels[i] == cluster_index :
			l.append(i)
	return l

if __name__  == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--model", default='output_svd.pickle', type=str) # contains .json files
	parser.add_argument("--model_keys", default='output_paragraph_inverse_index.pickle', type=str) # is a .json file
	parser.add_argument("--output_dir", default="UCBLIstexResults/", type=str) # contains wikipedia text files

	args = parser.parse_args()
	model = args.model
	model_keys = args.model_keys
	outputdir = args.output_dir


	f = open(model, 'r')
	svdMatrix = pickle.load(f)
	f.close()

	keys = open(model_keys, 'r')
	index_keys = pickle.load(keys)
	keys.close()

	if not os.path.exists(outputdir):
		os.makedirs(outputdir)

	output = outputdir+"testSvdUcblIstexDistancesCluster"
	f = open(outputdir+"StandardDeviation.txt", "w")

	os.mknod(outputdir+"StandardDeviation.txt")
	os.mknod(outputdir+"Clusters4MentalRotation.txt")

	ucbl_mat = svdMatrix[0:184]
	
	clusters = computeKmeans(ucbl_mat, nb_clusters=4)
	for i in range(4): 
		l_good_indices = ListSameCluster(clusters.labels_,  cluster_index = i)
		ucblbary = Barycenter(svdMatrix[l_good_indices]) # take the 184 first vectors corresponding to UCBL
		f = open(outputdir+"Clusters4MentalRotation.txt", "a")
		f.write(outputdir+"Cluster "+str(i)+"\n")
		for doc in l_good_indices :
			f.write(str(doc) + " " + index_keys[str(doc)]+"\n")
		f.close()
		distances = VectorsCosinusDistances(ucblbary, svdMatrix )
		saveDistances(distances, output+ str(i)+".txt", keys = index_keys, cluster=i  )
		

