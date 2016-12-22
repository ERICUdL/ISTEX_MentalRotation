# -*- coding: utf-8 -*-
#
# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Script that produces statitics about the use of vocabulary through time.

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2, University of Lorraine

# Thanks to ISTEX project for the funding


import string 
import nltk
import json
from nltk.stem.porter import PorterStemmer
import numpy as np
import sys, argparse
reload(sys)
sys.setdefaultencoding('utf8')


#######
# based on http://www.cs.duke.edu/courses/spring14/compsci290/assignments/lab02.html
stemmer = PorterStemmer()
def stem_tokens(tokens, stemmer):
	stemmed = []
	for item in tokens:
		stemmed.append(stemmer.stem(item))
	return stemmed


def tokenize(text):
	tokens = nltk.word_tokenize(text.lower())
	tokens = [i for i in tokens if i not in string.punctuation]
	stems = stem_tokens(tokens, stemmer)
	str_lem = ""
	for i in stems :
		str_lem += i + " "
	return str_lem

def tokenizeList(list_text) :
	token_list = []
	for i in list_text :
		token_tmp = tokenize(i)
		token_list.append(token_tmp)
	return token_list

# stemmer list of key words : rebuild the bigram at the end to be sure.
def createVocabularyDictTokenized(cluster = 0, mr_tools=[], mr_demographic=[] ) : # 0 if all, 1 if cluster tools, 2 if cluster demographic
	dico = dict()
	if cluster == 0 or cluster == 1 :
		for m in mr_tools :
			dico[tokenize(m)] = 0
	if cluster == 0 or cluster == 2 :
		for m in mr_demographic :
			dico[tokenize(m)] = 0
	return dico

def createVocabularyDict(cluster = 0, mr_tools=[], mr_demographic=[]) : # 0 if all, 1 if cluster tools, 2 if cluster demographic
	# list of key word for the 2 clusters
	dico = dict()
	if cluster == 0 or cluster == 1 :
		for m in mr_tools :
			dico[m] = 0
	if cluster == 0 or cluster == 2 :
		for m in mr_demographic :
			dico[m] = 0
	return dico


def computeTiming(file_name, cluster = 0) :
	time = dict()
	# for each time, we have a dict() with: we need to create the json file containing the information
	# we only have the ids in the resulting picklefile
	for doc in json :
		year = doc["year"]
		text = doc["title"]+" " + doc["abstract"]
	if year not in time :
		time[year] = createVocabularyDict(cluster)

	tmp = createVocabularyDict(cluster)
	for m in tmp :
		l_text = tokenize(text)
		if m in l_text :
			time[year][m] += 1
	return time

class Document(object) :
	def __init__(self, istex_id, text, publicationDate, source):
		self.istex_id = istex_id
		self.text = text
		self.publicationDate = publicationDate
		self.source = source

# read the raw data files (mainly ucbl and mental rotation istex documents)
def read_json_inputs(path, source):
	f_input = open(path, "rb")
	json_docs = json.load(f_input)
	f_input.close()
	doc_list = []
	for doc in json_docs :
		doc_list.append(Document(doc["istex_id"], doc["title"]+" __ "+doc["abstract"], doc["publicationDate"], source))
	return doc_list

# read the resulting file out of istex database, supposely containing documents related to mental rotation
def read_json_results(path) :
	f_input = open(path, "rb")
	json_docs = json.load(f_input)
	f_input.close()
	doc_list = []
	for doc in json_docs :
		doc_list.append(Document(doc["istex_id"], doc["text"], doc["publicationDate"], "ISTEX"))
	return doc_list

def create_phrases_dict(nb_phrases) :
	dico = dict()
	for p in range(nb_phrases) :
		dico[p] = 0
	return dico

# nb_years : lines, len_voc: columns
def createNumpyArray(nb_years, len_voc) :
	return np.zeros((nb_years, len_voc))

#list_voc contains the key phrases on which we do the statistics, the labels of the columns
def save_csv(max_year, min_year, count_years, all_voc, cluster_one, cluster_two, list_voc, output_file) :
	f_out = open(output_file, "w")
	str_first_line = "year\tnb_documents\tnb_doc_selected_domain\tcluster selected domain methods\tcluster demograhic"
	
	for v in list_voc :
		str_first_line += "\t"+v
	f_out.write(str_first_line)
	
	for year in range(min_year,max_year) :
		str_line = str(year)+"\t"+str(count_years[year-min_year])+"\t"+str(all_voc[year-min_year][0])+"\t"+str(cluster_one[year-min_year][0])+"\t"+str(cluster_two[year-min_year][0])
		for w in range(len(list_voc)) :
			str_line += "\t"+str(numpy_array[year-min_year][w])
		f_out.write("\n"+str_line)
	f_out.close()

def document_in_cluster(list_voc, text) :
	for v in list_voc :
		if v in text :
			return True
	return False

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_file", default='results/chart_input_complete.json', type=str)
	parser.add_argument("--key_words_cluster1", default=["mental rotation", "motor" , "task" , "stimuli" , "orientation", "event related potentials", "mismatch negativity", "attention deficit hyperactivity disorder", "lingual gyrus", "perirhinal cortex", "transcranial magnetic stimulation"], type=str, nargs='+')
	parser.add_argument("--key_words_cluster2", default = ["mental rotation", "sex differences", "spatial ability", "visual", "age", "perform"], type=str, nargs='+')
	#parser.add_argument("--output_csv", default='results/chart_csv_ucbl_clusters.csv', type=str) # is a .json file
	parser.add_argument("--output_csv", default='results/chart_csv_istex_clusters.csv', type=str) # is a .json file
	parser.add_argument("--min_year", default=1944, type=str) # is a .json file
	parser.add_argument("--max_year", default=2017, type=str) # is a .json file
	parser.add_argument("--voc", default=0, type=str) # all the selected voc= 0, only cluster 1 (tools) voc=1, cluster 2 : demographics voc=2

	args = parser.parse_args()

	input_file = args.input_file
	output_file = args.output_csv
	max_year = args.max_year
	min_year = args.min_year
	voc_selection = args.voc
	cluster1= args.key_words_cluster1
	cluster2= args.key_words_cluster2
	docs = read_json_results(input_file)
	#docs = read_json_inputs(input_file, "UCBL")
	voc = createVocabularyDict(voc_selection, mr_tools=cluster1, mr_demographic=cluster2) # without tokenization
	list_voc = voc.keys()
	tokenstrings = tokenizeList(list_voc) # can give an integer to specify a selection of vocabulary
	nb_phrases = len(tokenstrings)

	voc_clusterone = tokenizeList(createVocabularyDict(1, mr_tools=cluster1, mr_demographic=cluster2).keys()) 
	voc_clustertwo = tokenizeList(createVocabularyDict(2, mr_tools=cluster1, mr_demographic=cluster2).keys()) 

	nb_years = max_year-min_year # from 1944 to 2016
	numpy_array = createNumpyArray(nb_years, nb_phrases)
	cluster_one = createNumpyArray(nb_years, 1)
	cluster_two = createNumpyArray(nb_years, 1)
	all_voc = createNumpyArray(nb_years, 1)
	# need to retrieve the documents with an object: list of documents, each doc is an object with : time, paragraph, istex_id
	count_years = np.zeros(nb_years)
	for doc in docs :
		token_text = tokenize(doc.text)
		index_year = int(doc.publicationDate)-min_year
		for p in range(nb_phrases) :
			if tokenstrings[p] in token_text:
				numpy_array[index_year][p] += 1
		if document_in_cluster(voc_clusterone, token_text): # any text containing one of the key_phrase of the cluster is considered to belong to this cluster
			cluster_one[index_year] += 1
		if document_in_cluster(voc_clustertwo, token_text):
			cluster_two[index_year] += 1
		if document_in_cluster(tokenstrings, token_text):
			all_voc[index_year] += 1
		count_years[int(doc.publicationDate)-min_year] += 1

	save_csv(max_year, min_year, count_years, all_voc, cluster_one, cluster_two, list_voc, output_file)

