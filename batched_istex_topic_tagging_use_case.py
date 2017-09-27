# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random, pickle, argparse, json, os, urllib2
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from utils import istex_positives_input, get_svd_from_doc_id, istex_negatives_input, generate_dataset, sorted_results, eval_use_case


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--svd_array", default='../RecSys_Exp_files/182_381_vec150_results/output_svd.pickle', type=str)
	parser.add_argument("--verbose", default= 1, type=int)
	parser.add_argument("--svd_index", default='../RecSys_Exp_files/182_381_vec150_results/output_paragraph_index.json', type=str)
	parser.add_argument("--svd_inv_index", default='../RecSys_Exp_files/182_381_vec150_results/output_paragraph_inversed_index.json', type=str)
	parser.add_argument("--topics", type=str) # list of topics as a comma seperated text
	parser.add_argument("--use_categories", default=1, type=int)
	parser.add_argument("--all_rand", default=1, type=int)
	parser.add_argument("--negative_ratio", default=1.0, type=float)
	parser.add_argument("--classifier", default='RFC', type=str) # possible values 'RFC' and 'GBC'
	parser.add_argument("--clf_out", default='results/clf_', type=str)
	parser.add_argument("--results_out", default='results/res_', type=str)
	parser.add_argument("--use_synset", default=0, type=str) # synset as a comma seperated text

	args = parser.parse_args()
	svd = pickle.load(open(args.svd_array,'rb'))
	verbose = args.verbose
	if verbose:
		print 'SVD array was successfully loaded'
	index = json.load(open(args.svd_index,'rb'))
	if verbose:
		print 'SVD index array was successfully loaded'
	inv_index = json.load(open(args.svd_inv_index,'rb'))
	if verbose:
		print 'SVD inversed index array was successfully loaded'
	topics = args.topics
	topics = topics.split(',')
	categories = args.use_categories
	all_rand = args.all_rand
	negative_ratio = args.negative_ratio
	classifier = args.classifier
	clf_out = args.clf_out
	results_out =  args.results_out
	use_synset = args.use_synset


	#Cleaning index
	inversed_index = dict()
	for (k, v) in inv_index.items():
		key = k.split('_')[1]
		inversed_index[key] = v

	for (k, v) in index.items():
		index[k] = v.split('_')[1]

	for topic in topics:
		topic = topic.replace(' ', '%20')
		#Get positive examples (initial_corpus) and test set
		corpus_ids = inversed_index.keys()
		initial_corpus, test = istex_positives_input(topic, topic, corpus_ids, categories=categories)
		if use_synset:
			synset_t = use_synset.split(', ')
			synset = []
			for syn in synset_t:
				x = syn.replace(' ','%20')
				synset.append(x)
			initial_corpus = np.array(initial_corpus, dtype=np.object)
			for syn in synset:
				syn_addition, _ = istex_positives_input(topic, syn, corpus_ids, categories=categories)
				syn_addition = np.array(syn_addition, dtype=np.object)
				initial_corpus = np.hstack((initial_corpus, syn_addition))
			initial_corpus = initial_corpus.tolist()

		if verbose:
			print 'initial corpus and test set was successfully extracted'
			print 'size of initial corpus:', len(initial_corpus)
			print 'size of test set:', len(test)
		positive_docs_svd = get_svd_from_doc_id(initial_corpus, inversed_index, svd)

		#Get negative examples
		neg_random_size = int(len(initial_corpus) * negative_ratio)
		try:
			negative_examples = istex_negatives_input(topic, initial_corpus, corpus_ids, neg_random_size, all_rand=0) #all_rand is false
		except:
			negative_examples = istex_negatives_input(topic, initial_corpus, corpus_ids, neg_random_size, all_rand=1) #all_rand is true
		if verbose:
			print 'the set of negative examples was successfully extracted'
		negative_docs_svd = get_svd_from_doc_id(negative_examples, inversed_index, svd)

		#Build the dataset and train a classifier
		X, y = generate_dataset(positive_docs_svd, negative_docs_svd)
		if classifier =='RFC':
			clf = RandomForestClassifier(n_estimators=500)
		elif classifier == 'GBC':
			clf = GradientBoostingClassifier(n_estimators=500)
		else:
			raise NameError('Please check your classsifier option. It must be either "RFC" or "GBC"')

		clf.fit(X, y)
		topic = topic.replace('%20','_')
		pickle.dump(clf, open(clf_out+topic, 'wb'))
		if verbose:
			print 'The classifier was successfully fitted with the dataset'
			print 'fitted classifier is dumped in:', clf_out+topic

		sim_results = clf.predict_proba(svd)
		results = sorted_results(sim_results, index)
		pickle.dump(results.items()[:100000], open(results_out+topic, 'wb'))
		if verbose:
			print 'The ranked list of result was successfully computed for the topic '+ topic
			print 'list of top 100K results are dumped in:', results_out+topic
