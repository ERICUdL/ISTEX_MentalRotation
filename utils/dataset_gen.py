# -*- coding: utf-8 -*-

# Helper functions for generating dataset for diferent use-cases
# These set of functions are designed for using the output of bow_svd.py
# Use example could be found in '../use_cases/istex_topic_tagging_use_case.py'

import numpy as np
import pandas as pd
import random, json, urllib2
from collections import OrderedDict

def istex_query_from(q, f):
	q = q+'&from='+str(f)
	response = urllib2.urlopen(q)
	data = json.load(response)
	subject_ids = np.array(range(len(data['hits'])), dtype=np.object)
	for (i, hit) in enumerate(data['hits']):
		subject_ids[i] = hit['id']
	return subject_ids

def istex_query(q):
	response = urllib2.urlopen(q)
	data = json.load(response)
	nb_requests = 1 + data['total'] / 1000
	if nb_requests > 10: # maximum number of pages due to API pagination restrection
		nb_requests = 10
	subject_ids = istex_query_from(q, 0)
	for i in range(nb_requests)[1:]:
		f = i * 1000
		next_request = istex_query_from(q, f)
		subject_ids = np.hstack((subject_ids, next_request))
	return subject_ids.tolist()

def find_intersection(list_a, list_b):
	return list(set(list_a) & set(list_b))

def get_svd_from_doc_id(ids_lst, svd_inversed_index, svd):
	res = np.arange(len(ids_lst), dtype=np.object)
	i = 0
	for (i, idd) in enumerate(ids_lst):
		res[i] = svd[int(svd_inversed_index[idd])]
	return res

def istex_positives_input(topic_query, topic_test, corpus_ids, categories=0):
	# topic is a string of words seperated by the ASCII code space '%20'
	# corpus_ids are from svd_inversed_index.keys()
	# categories is a flag for using the categories field in generating the positive examples and test set

	if not categories:
		initial_corpus = istex_query('https://api.istex.fr/document/?q=((title:%22'+topic_query+'%22%20OR%20abstract:%22'+topic_query+'%22)%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id')
		_gs = istex_query('https://api.istex.fr/document/?q=((subject.value:%22'+topic_test+'%22%20OR%20keywords:%22'+topic_test+'%22%20)%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id')
	else:
		initial_corpus = istex_query('https://api.istex.fr/document/?q=((title:%22'+topic_query+'%22%20OR%20subject.value:%22'+topic_query+'%22%20OR%20keywords:%22'+topic_query+'%22%20OR%20abstract:%22'+topic_query+'%22)%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id')
		_gs = istex_query('https://api.istex.fr/document/?q=((categories.wos:%22'+topic_test+'%22%20AND%20corpusName:%22elsevier%22)%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id')
	initial_corpus = find_intersection(initial_corpus, corpus_ids)
	test_set = {x for x in _gs if x not in initial_corpus}
	test_set = find_intersection(test_set, corpus_ids)
	initial_corpus = list(initial_corpus)
	test = list(test_set)
	return initial_corpus, test

def istex_negatives_input(q, initial_corpus, corpus_ids, neg_random_size, all_rand=1):
	# q is the topic key-pharse
	# corpus_ids are from svd_inversed_index.keys()
	# initial_corpus is an output of istex_positives_input() fuction

	other_ids = other_ids = [x for x in corpus_ids if x not in initial_corpus]
	if not all_rand: 
		keywords = q.split('%20')
		nb_negative_types = len(keywords) + 1
		negatives = {}
		for k in keywords:
			q_k = 'https://api.istex.fr/document/?q=((title:%22'+k+'%22%20OR%20abstract:%22'+k+'%22)%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
			results_of_k = istex_query(q_k)
			negatives[k] = np.array([x for x in results_of_k if x not in initial_corpus])
		#random indecies to select from each type
		for k in keywords:
			indicies = random.sample(range(len(negatives[k])), neg_random_size/nb_negative_types)
			negatives[k] = negatives[k][indicies]
		indicies = random.sample(range(len(corpus_ids)), neg_random_size/nb_negative_types)
		unique_negatives = np.unique(negatives.values())
		unique_negatives = find_intersection(unique_negatives, other_ids)
	else:
		unique_negatives = []
	print 'length of unique negatives of keywords:', len(unique_negatives)
	other_ids = [x for x in other_ids if x not in unique_negatives]
	indicies = random.sample(range(len(other_ids)), neg_random_size - len(unique_negatives))
	other_ids = np.array(other_ids)
	random_negatives = other_ids[indicies]
	negative_examples = np.hstack((unique_negatives,random_negatives))
	print 'size of negative examples:', len(negative_examples)
	return negative_examples.tolist()

def generate_dataset(positive_docs_svd, negative_rand_docs_svd):
	# Takes 2 numpy arrays which are the SVD representation of the documents, output of get_svd_from_doc_id()
	# First array represents the positive examples while the other represents the negative examples
	# Returns a dataset (X,y) where X is a combination of the 2 arrays and y is the lables

	vector_size = len(positive_docs_svd[0])
	ones_lables = np.ones(len(positive_docs_svd), dtype=np.int)
	size_negative = len(negative_rand_docs_svd)
	negative_examples = negative_rand_docs_svd
	zeros_lables = np.zeros(len(negative_examples), dtype=np.int)
	y = np.hstack((ones_lables, zeros_lables))
	X_in = np.hstack((positive_docs_svd, negative_examples))
	X = np.zeros((len(X_in),vector_size))
	for (i, x) in enumerate(X_in):
		for (j, f) in enumerate(x):
			X[i,j] = f
	return X, y

def sorted_results(sim_results, doc_id_dict):
	results = dict()
	for i, score in enumerate(sim_results[:,1]):
		doc_id = doc_id_dict[str(i)]
		results[doc_id] = score
	sorted_results = OrderedDict(sorted(results.items(), key=lambda k: k[1], reverse=True))
	return sorted_results

def eval_use_case(sorted_results, top_n, test):
	top = pd.DataFrame(sorted_results.items()[:top_n])
	print 'matched rate at '+str(top_n)+':' , len(find_intersection(test,top[0]))/float(len(test))
