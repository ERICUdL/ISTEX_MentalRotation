# -*- coding: utf-8 -*-
#
# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Load and transform ISTEX and wiki articles into bag_of_words decomposed by SVD.

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2

# Thanks to ISTEX project for the funding


import os, argparse, pickle, json
from sklearn.feature_extraction.text import CountVectorizer,  TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import numpy as np
import IPython
from sklearn.decomposition import LatentDirichletAllocation



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


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_file", default='results/LDA_res_input.pickle', type=str) # path to input file
	parser.add_argument("--out_file", default='results_lda.txt', type=str) # name of output file
	parser.add_argument("--lemmatizer", default=0, type=int) # for using lemmatization_tokenizer
	parser.add_argument("--mx_ngram", default=2, type=int) # the upper bound of the ngram range
	parser.add_argument("--mn_ngram", default=1, type=int) # the lower bound of the ngram range
	parser.add_argument("--stop_words", default=1, type=int) # filtering out English stop-words
	parser.add_argument("--vec_size", default=100, type=int) # the size of the vector in the semantics space
	parser.add_argument("--min_count", default=20, type=int) # minimum frequency of the token to be included in the vocabulary
	parser.add_argument("--max_df", default=0.95, type=float) # how much vocabulary percent to keep at max based on frequency
	parser.add_argument("--out_dir", default="results", type=str) # name of the output directory

	args = parser.parse_args()
	input_file = args.input_file
	out_file = args.out_file
	lemmatizer = args.lemmatizer
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
	out_dir = args.out_dir

	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	f = open(input_file, "r")
	input_dict = pickle.load(f)
	nb_articles = len(input_dict)
	f.close()
	keys = np.array(range(nb_articles),dtype=np.object)
	values = np.array(range(nb_articles),dtype=np.object)

	
	for i, (key,value) in enumerate(input_dict.items()) :
		keys[i] = key
		values[i] = value
	tf_idf_vectorizer = TfidfVectorizer(input='content',
			analyzer='word', stop_words=stop_words, tokenizer=lemmatizer,
			min_df=min_count,  ngram_range=(mn_ngram, mx_ngram), max_df=max_df)

	tf_idf_bow = tf_idf_vectorizer.fit_transform(values)
	tf_feature_names = tf_idf_vectorizer.get_feature_names()

	r = open(os.path.join(out_dir, out_file), "w")
	for i in range(2, 11) :
		lda = LatentDirichletAllocation(n_topics=i, max_iter=5, learning_method='online', learning_offset=50., random_state=0)
		lda.fit(tf_idf_bow)
		r.write('Number of topics: '+str(i))
		r.write('\nTop words\n')
		write_top_words(lda, tf_feature_names, 25, r)
		r.write('End top words\n')
		vocab = tf_idf_vectorizer.get_feature_names()
		r.write('size of the vocabulary: '+str(len(vocab))+'\n')
		r.write('______________________________\n')
	print 'results are written in file: ', os.path.join(out_dir, out_file)
