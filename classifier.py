# -*- coding: utf-8 -*-
#
# This file is part of ISTEX_MentalRotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see License file for
# more details.

# Binary classifier for Mental_Rotation articles

# co-author: Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr>
# Affiliation:{University of Lyon, ERIC Laboratory, CNRS, ISH-Lyon}, France

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# Affiliation: ERIC Laboratory, France
# Thanks to ISTEX project for the funding

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import OrderedDict
import numpy as np
import random, pickle, argparse, json, os


def sampling(lst, class_type, sample_size=200):
	# given a list, return a sample list of a given size with a class label for
	# each sample
	lst_size = len(lst)
	if sample_size > lst_size:
		indecies = np.random.choice(range(lst_size),size=sample_size - lst_size)
		sample_lst = np.vstack((lst,lst[indecies]))
	else:
		indecies = random.sample(range(lst_size), sample_size)
		sample_lst = lst[indecies]

	if class_type == 'positive':
		labels = np.ones(sample_size, dtype=np.int)
	elif class_type == 'negative':
		labels = np.zeros(sample_size, dtype=np.int)
	else:
		raise NameError('Unrecognized class type. \
		       Must be either "positive" or "negative"')
	labels = labels.reshape(-1, 1)
	sample = np.hstack((sample_lst, labels))
	return sample

def balanced_dataset(pos_lst, neg_lst, size):
	pos_size = size/2
	neg_size = size - pos_size # in case of odd int value of size
	positives = sampling(pos_lst, 'positive', pos_size)
	negatives = sampling(neg_lst, 'negative', neg_size)
	return np.vstack((positives,negatives))


def search_top_relevant(sim_results, doc_id_dict, sim_th, count_positive):
	related = sim_results[:,1] > sim_th
	related_indecies = []
	for i, r in enumerate(related):
		if r:
			related_indecies.append((i, sim_results[i,1]))
	results = dict()
	for i, score in related_indecies:
		doc_id = doc_id_dict[str(count_positive + i)]
		results[doc_id[5:]] = score
	sorted_results = OrderedDict(sorted(results.items(), key=lambda k: k[1], reverse=True))
	return sorted_results

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--vectors", default="results/output_svd.pickle", type=str,
	                     help='location of the decomposed document vectors (pickle file)')
	parser.add_argument("--doc_dict", default="results/output_paragraph_inverse_index.json", type=str,
	                     help='location of index-to-doc_id dictionary (json file)')
	parser.add_argument("--count_positive", default=183, type=int,
	                     help='the count of positive examples, i.e. mental-\
	                     rotation articles. It also corresponds to the max\
	                     index where all indices below are for positive\
	                     examples in the passed decomposed vectors')
	parser.add_argument("--test_split", default=0.25, type=float,
	                     help='float number to indicate the percentage of the test split')
	parser.add_argument("--min_relevant", default=10, type=int,
	                     help='minimum number ot relevant document to return')
	parser.add_argument("--training_size", default=300, type=int,
	                     help='the size of training dataset for the classifier')
	parser.add_argument("--testing_size", default=100, type=int,
	                     help='the size of testing dataset for the classifier')
	parser.add_argument("--n_iterations", default=10, type=int,
	                     help='number of iterations to be averaged for \
	                     estimating the classifier accuracy')
	parser.add_argument("--n_estimators", default=500, type=int,
	                     help='number of estimators as a parameter for \
	                     Random-Forest-Classifier')
	parser.add_argument("--verbose", default=1, type=int,
	                     help='if 0, it will not print iterations')
	parser.add_argument("--out_dir", default="results", type=str,
	                     help='name of the output directory')

	args = parser.parse_args()
	vectors = args.vectors
	doc_dict = args.doc_dict
	count_positive = args.count_positive
	test_split =  args.test_split
	min_relevant = args.min_relevant
	training_size = args.training_size
	testing_size = args.testing_size
	n_iterations = args.n_iterations
	n_estimators = args.n_estimators
	verbose = args.verbose
	out_dir = args.out_dir

	svd_vectors = pickle.load(open(vectors,'rb'))
	print 'The model (document decomposed vectors) was loaded successfully'
	vec_size = svd_vectors.shape[1]
	pos_lst = svd_vectors[:count_positive]
	neg_lst = svd_vectors[count_positive:]

	scores = np.zeros(n_iterations)
	for i in range(n_iterations):
		if verbose > 0:
			print 'iteration', i + 1 , 'out of ', n_iterations
		train, test = train_test_split(pos_lst, test_size=test_split)
		train_data = balanced_dataset(train, neg_lst, training_size)
		test_data = balanced_dataset(test, neg_lst, testing_size)

		X_train = train_data[:,:vec_size]
		y_train = train_data[:,vec_size:].ravel() # better shape for the classifier
		X_test = test_data[:,:vec_size]
		y_test = test_data[:,vec_size:]

		rfc = RandomForestClassifier(n_estimators=n_estimators)
		rfc.fit(X_train, y_train)
		y_predict = rfc.predict(X_test)
		scores[i] = accuracy_score(y_test, y_predict)
	print 'classifier estimated accuracy (average over n_iterations):'
	print np.average(scores)

	# Now try to retreive high relevant articles
	classifier = RandomForestClassifier(n_estimators=n_estimators)
	dataset = balanced_dataset(pos_lst, neg_lst, training_size + testing_size)
	X = dataset[:,:vec_size]
	y = dataset[:,vec_size:].ravel()
	classifier.fit(X, y)
	sim_results = classifier.predict_proba(neg_lst)
	doc_id_dict = json.load(open(doc_dict,'rb'))
	for sim_th in np.arange(1.0,0.25,-0.001):
		results = search_top_relevant(sim_results, doc_id_dict, sim_th,
		                              count_positive)
		if len(results) > min_relevant:
			print 'doi of articles that are classified as mental-retotation'
			print 'with a probability value of at least ', sim_th
			print results
			break
	
	# dumping results
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	json.dump(results, open(out_dir+'/results.json','wb'))
	pickle.dump(classifier,open(out_dir+'/model.pickle','wb'))
