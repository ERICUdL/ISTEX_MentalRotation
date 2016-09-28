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

# Thanks to ISTEX project for the foundings


import os, argparse, pickle, json
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from utils import Paragraphs
import IPython

def get_filenames(path_to_corpus):
	filenames = []
	for path, subdirs, files in os.walk(path_to_corpus):
	    for name in files:
	        filenames.append(os.path.join(path, name))
	        
	return filenames

def sense_tokenizer(line):
	try:
		return transform_doc(parser(line)).split()
	except:
		return line.split()

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--wiki_dir", default="sample_data/wiki", type=str) # contains wikipedia text files
	parser.add_argument("--istex_dir", default='sample_data/ISTEX/', type=str) # contains .json files
	parser.add_argument("--ucbl_file", default='sample_data/sportArticlesAsIstex.json', type=str) # is a .json file
	parser.add_argument("--max_nb_wiki", default=100000, type=int) # maximum number of Wikipedia paragraphs to use
	parser.add_argument("--paragraphs_per_article", default=2, type=int) # Maximum number of paragraphs to load per article
	parser.add_argument("--vectorizer_type", default="tfidf", type=str) # possible values: "tfidf" and "count", futurework: "doc2vec"
	parser.add_argument("--mx_ngram", default=2, type=int) # the upper bound of the ngram range
	parser.add_argument("--mn_ngram", default=1, type=int) # the lower bound of the ngram range
	parser.add_argument("--vec_size", default=100, type=int) # the size of the vector in the semantics space
	parser.add_argument("--min_count", default=20, type=int) # minimum frequency of the token to be included in the vocabulary
	parser.add_argument("--max_df", default=0.95, type=float) # how much vocabulary percent to keep at max based on frequency
	parser.add_argument("--debug", default=False, type=bool) # embed IPython to use the decomposed matrix while running
	parser.add_argument("--compress", default="json", type=str) # for dumping resulted files

	args = parser.parse_args()
	istex = args.istex_dir
	if istex == "None":
		istex = None
	ucbl = args.ucbl_file
	wiki_dir = args.wiki_dir
	if wiki_dir == "None":
		wiki_dir = None
	max_nb_wiki = args.max_nb_wiki
	paragraphs_per_article = args.paragraphs_per_article
	vectorizer_type = args.vectorizer_type
	mx_ngram = args.mx_ngram
	mn_ngram =  args.mn_ngram
	n_components = args.vec_size
	min_count = args.min_count
	max_df = args.max_df
	debug = args.debug
	compress = args.compress
	
	paragraphs = Paragraphs(istex=istex, ucbl=ucbl, wiki=wiki_dir, max_nb_wiki_paragraphs=max_nb_wiki, paragraphs_per_article=paragraphs_per_article)

	if vectorizer_type == "count":
		vectorizer = CountVectorizer(input='content',
			         analyzer='word', stop_words='english',
			         min_df=min_count,  ngram_range=(mn_ngram, mx_ngram), max_df=max_df)
	elif vectorizer_type == "tfidf":
		vectorizer = TfidfVectorizer(input='content',
			         analyzer='word', stop_words='english',
			         min_df=min_count,  ngram_range=(mn_ngram, mx_ngram), max_df=max_df)
	else:
		raise NameError('Please check your vectorizer option. It must be either "tfidf" or "count"')

	bow = vectorizer.fit_transform(paragraphs)

	vocab = vectorizer.get_feature_names()
	print 'size of the vocabulary:', len(vocab)

	svd = TruncatedSVD(n_components=n_components, n_iter=5, random_state=42)
	decomposed_bow = svd.fit_transform(bow)
	print 'shape of the SVD decomposed bag_of_words', decomposed_bow.shape
	print 'explained variance ratio sum', svd.explained_variance_ratio_.sum()

	#Dump and clean-up the vectorized bow to free some memory	
	try:
		pickle.dump(bow, open('vectorized_bow.pickle','wb'))
		bow = []
	except:
		bow = []

	#Compute the average cosine similarity withen ucbl vectors
	sum_sim = 0
	compare_count = 0
	ucbl_count = paragraphs.ucbl_count
	for i in range(0, ucbl_count):
	    for j in range(i+1, ucbl_count):
			sim = cosine_similarity(decomposed_bow[i], decomposed_bow[j])
			compare_count += 1
			sum_sim += sim
	print 'average cosine similarity within ucbl articles', sum_sim / compare_count

	if debug:
		IPython.embed()
	print "Now dumping results. This would take several minutes..."	
	if compress == "pickle":
		pickle.dump(decomposed_bow, open('output_svd.pickle','wb'))
		pickle.dump(paragraphs.index, open('output_paragraph_index.pickle','wb'))
		pickle.dump(paragraphs.inverse_index, open('output_paragraph_inverse_index.pickle','wb'))
	elif compress == "json":
		try:
			pickle.dump(decomposed_bow, open('output_svd.json','wb'))
			pickle.dump(paragraphs.index, open('output_paragraph_index.json','wb'))
			pickle.dump(paragraphs.inverse_index, open('output_paragraph_inverse_index.json','wb'))
		except:
			print "we could not dump the decomposed_bow in json. try pickle instead"
			IPython.embed()
	else:
		raise NameError('Unrecognized compress option. Must be either "pickle" or "json"')
	print "done successfully!"
