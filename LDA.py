# -*- coding: utf-8 -*-
#
# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Load the SVD representation of documents done for the whole corpus of ISTEX and UCBL.
# Classify the documents by clusters using the LatentDirichletAllocation method. Try with different number of clusters.
# Extract the key words representing each cluster.

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2

# Thanks to ISTEX project for the foundings

import os, argparse, pickle, json
from sklearn.feature_extraction.text import CountVectorizer,  TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

import IPython
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def print_top_words(model, feature_names, n_top_words):
	for topic_idx, topic in enumerate(model.components_):
		print("Topic #%d:" % topic_idx)
		print(" | ".join([feature_names[i]
		for i in topic.argsort()[:-n_top_words - 1:-1]]))
	print()

def write_top_words(model, feature_names, n_top_words, outfile):
	for topic_idx, topic in enumerate(model.components_):
		outfile.write("Topic #%d:" % topic_idx)
		outfile.write("\n")
		outfile.write(" | ".join([feature_names[i]
		for i in topic.argsort()[:-n_top_words - 1:-1]]))
		outfile.write("\n")
	outfile.write("\n")

def KeysValuesInit(nb_articles) : 
	keys = np.array(range(nb_articles),dtype=np.object)
	values = np.array(range(nb_articles),dtype=np.object)
	for i, (key,value) in enumerate(input_dict.items()) :
		keys[i] = key
		values[i] = value

	return keys, values

def statisticsClusterSelection(cluster, document_id, docs_topic, selection, stat_selection, outfile_pointer):
	if selection in document_id and outfile_pointer != None : # keys[t] is a string, the name of the document
		max_index = np.argmax(docs_topic[cluster], axis=0) #docs_topic[t]: dictionary of the clusters with the likelihood to belong to this cluster
		outfile_pointer.write(str(document_id) + " best cluster : " + str(max_index) + " likelihood: " + str(docs_topic[cluster][max_index])) # find the index of one list, with a numpy array format
		if max_index not in stat_selection :
			stat_selection[max_index] = 0
		stat_selection[max_index] += 1
		outfile_pointer.write("\n")
	return stat_selection

# Compute the clusters of document and write the results in output files.
# Need the
def statiticsClusters(nb_cluster, tf_idf_bow, tf_feature_names, ucbl_output=None, istex_output = None ,max_iter=5, learning_method='online', learning_offset=50., random_state=0):
	lda = LatentDirichletAllocation(n_topics=nb_cluster, max_iter=max_iter, learning_method=learning_method, learning_offset=learning_offset, random_state=random_state)
	lda.fit(tf_idf_bow)
	docs_topic = lda.transform(tf_idf_bow)
	list_ucbl = dict()
	list_mristex = dict()
	for t in range(len(docs_topic)) :
		list_ucbl = statisticsClusterSelection(t, keys[t], docs_topic, "UCBL", list_ucbl, ucbl_output)
		list_mristex = statisticsClusterSelection(t, keys[t], docs_topic, "MRISTEX", list_mristex, istex_output)
	generic.write("Total number of topics: "+str(nb_cluster))
	generic.write("\nNumber of topics for ucbl: "+str(len(list_ucbl)))
	generic.write("\nNumber of topics for istex: "+str(len(list_mristex)))
	ucbl_out.write("\nNumber of topics: "+str(len(list_ucbl))+"\n")
	ucbl_out.write("Total number of topics: "+str(i)+"\n\n")
	istex_out.write("Number of topics: "+str(len(list_mristex))+"\n\n")
	generic.write("\nTop words\n")
	write_top_words(lda, tf_feature_names, 15, generic)
	generic.write("End top words")
	vocab = tf_idf_vectorizer.get_feature_names()
	generic.write('size of the vocabulary:'+str(len(vocab)))
	generic.write("\nUCBL in topics :\n")
	for t in list_ucbl :
		generic.write("Cluster " + str(t) + " UCBL Nb : " + str(list_ucbl[t]) + "\n")
	generic.write("\nMR ISTEX in topics :\n")
	for t in list_mristex :
		generic.write("Cluster " + str(t) + " MR ISTEX Nb : " + str(list_mristex[t]) + "\n")
	generic.write("\n\n")
	print "Nb clusters ", i, " Nb ucbl clusters " , len(list_ucbl.values()) , min(list_ucbl.values()), " Nb istex cluster ",len(list_mristex), min(list_mristex.values()) # how many documents in the cluster containing less ucbl documents


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_file", default='results.pickle', type=str) # is a .json file
	parser.add_argument("--output_file", default='results/results_lda.txt', type=str) # is a .json file
	parser.add_argument("--lemmatizer", default=0, type=int) # for using lemmatization_tokenizer
	parser.add_argument("--mx_ngram", default=2, type=int) # the upper bound of the ngram range
	parser.add_argument("--mn_ngram", default=1, type=int) # the lower bound of the ngram range
	parser.add_argument("--stop_words", default=1, type=int) # filtering out English stop-words
	parser.add_argument("--vec_size", default=100, type=int) # the size of the vector in the semantics space
	parser.add_argument("--min_count", default=1, type=int) # minimum frequency of the token to be included in the vocabulary
	parser.add_argument("--max_df", default=0.95, type=float) # how much vocabulary percent to keep at max based on frequency
	parser.add_argument("--debug", default=0, type=int) # embed IPython to use the decomposed matrix while running
	parser.add_argument("--compress", default="json", type=str) # for dumping resulted files
	parser.add_argument("--out_dir", default="results", type=str) # name of the output directory
	parser.add_argument("--min_nb_clusters", default=2, type=int) # minimum number of cluster we try
	parser.add_argument("--max_nb_clusters", default=10, type=int) #  maximum number of cluster we try

	args = parser.parse_args()
	input_file = args.input_file
	output_file = args.output_file
	out_dir = args.out_dir
	lemmatizer = args.lemmatizer
	min_nb_clusters = args.min_nb_clusters
	max_nb_clusters = args.max_nb_clusters

	if lemmatizer:
		lemmatizer = Lemmatizer()
	else:
		lemmatizer = None
	mx_ngram = args.mx_ngram
	mn_ngram =  args.mn_ngram
	stop_words = args.stop_words
	if stop_words:
		stop_words = 'english'
	else:
		stop_words = None
	n_components = args.vec_size
	min_count = args.min_count
	max_df = args.max_df
	debug = args.debug
	compress = args.compress
	out_dir = args.out_dir

	# instead of recomputing the vectors, we should use the one of the complete experiment, so use  pickle load
	f = open(input_file, "r")
	input_dict = pickle.load(f)
	nb_articles = len(input_dict)
	f.close()

	keys, values = KeysValuesInit(nb_articles)
	tf_idf_vectorizer = TfidfVectorizer(input='content', analyzer='word', stop_words=stop_words, tokenizer=lemmatizer,
			min_df=min_count,  ngram_range=(mn_ngram, mx_ngram), max_df=max_df)

	tf_idf_bow = tf_idf_vectorizer.fit_transform(values)
	tf_feature_names = tf_idf_vectorizer.get_feature_names()

	generic = open(output_file, "w")
	ucbl_out = open(os.path.join(out_dir, "lda_ucbl_cluster.txt"), "w")
	istex_out = open(os.path.join(out_dir, "lda_mristex_cluster.txt"), "w") 

	for i in range(min_nb_clusters, max_nb_clusters) :
		statiticsClusters(i, tf_idf_bow, tf_feature_names, ucbl_out, istex_out ,max_iter=5, learning_method='online', learning_offset=50., random_state=0)

	generic.close()
	ucbl_out.close()
	istex_out.close()

