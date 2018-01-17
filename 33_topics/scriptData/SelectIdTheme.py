# -*- coding: utf-8 -*-

# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.
# co-author : Lucie Martinet <lucie.martinet@eric.univ-lyon2.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2, CESI EXIA/LINEACT

# Thanks to ISTEX project for the funding

import numpy as np
#import pandas as pd
import random, pickle, argparse, json, os, urllib2, subprocess
from collections import OrderedDict
from operator import itemgetter
from sklearn.ensemble import RandomForestClassifier


# functions
########################################################################################
def query_from(q, f):
	q = q+'&from='+str(f)
	response = urllib2.urlopen(q)
	data = json.load(response)
	subject_ids = np.array(range(len(data['hits'])), dtype=np.object)
	for (i, hit) in enumerate(data['hits']):
		subject_ids[i] = hit['id']
	return subject_ids

def query(q):
	response = urllib2.urlopen(q)
	data = json.load(response)
	nb_requests = 1 + data['total'] / 1000
	if nb_requests > 10: # maximum number of pages due to API pagination restrection
		nb_requests = 10
	subject_ids = query_from(q, 0)
	for i in range(nb_requests)[1:]:
		f = i * 1000
		next_request = query_from(q, f)
		subject_ids = np.hstack((subject_ids, next_request))
	return subject_ids.tolist()

def find_intersection(list_a, list_b):
	return list(set(list_a) & set(list_b))

def find_B_less_AOne(list_a, list_b):
	return list(set(list_b)-set(list_a))

def find_B_less_A(list_a, list_b):
	l = []
	for i in list_b :
		if i not in list_a :
			l.append(i)
	return l

def assure_path_exists(path):
	if not os.path.exists(path):
			os.makedirs(path)


def term2url(string):
	string = string.split(' ')
	res = '%22'
	for s in string:
		res = res + s + '%20'
	res = res[:-3]
	res = res + '%22'
	return res

def babel_synset(synset):
	q = 'https://api.istex.fr/document/?q=(('
	for syn in synset:
		syn = term2url(syn)
		q = q + 'title:' + syn + '%20OR%20abstract:' + syn + '%20OR%20'
	q = q[:-8]
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_synset(synset):
	q = 'https://api.istex.fr/document/?q=(('
	for syn in synset:
		syn = term2url(syn)
		q = q + 'title:' + syn + '%20OR%20abstract:' + syn + '%20OR%20'
	q = q[:-8]
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_subj_keyword(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'subject.value:' + topic + '%20OR%20keywords:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_subj(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'subject.value:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_keyword(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'keywords:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20AND%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q
 
def babel_title_abst(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'title:' + topic + '%20OR%20abstract:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20ANvdD%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_title(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'title:' + topic 
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20ANvdD%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q

def babel_abst(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'abstract:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20ANvdD%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q


def babel_title_abst_subject_keywords(topic):
	q = 'https://api.istex.fr/document/?q=(('
	topic = term2url(topic)
	q = q+ 'title:' + topic + '%20OR%20abstract:' + topic + 'subject.value:' + topic + '%20OR%20keywords:' + topic
	q = q + ')%20AND%20(qualityIndicators.abstractWordCount:[35%20500]%20AND%20qualityIndicators.pdfPageCount:[3%2060]%20AND%20publicationDate:[1990%202016]%20ANvdD%20language:(%22eng%22%20OR%20%22unknown%22)%20AND%20genre:(%22research_article%22%20OR%20%22conference[eBooks]%22%20OR%20%22article%22%20)%20))&size=1000&output=id'
	return q


def print_list_in_file (l,file_name): # l is a list of documents
	f=open(file_name, "w")
	for d in l :
		f.write(d)
	f.close()

def query_json(DirName, list_files):
	assure_path_exists(DirName)
	for f in list_files :
		os.system('wget https://api.istex.fr/document/%s -O %s'%(f,os.path.join(DirName,f+".json")) )



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--output_dir", default='ThemesIstexIdList', type=str)
	args = parser.parse_args()
	output = args.output_dir

	list_themes = ["Artificial Intelligence","Information Systems", "Rehabilitation", "Philosophy","Microscopy","Infectious Diseases","Respiratory System", \
"Literature","Robotics", "Pediatrics", "Mechanics", "Condensed Matter", "Transplantation", "Religion", "Pathology", "Immunology", "Nursing", "Substance Abuse", "Thermodynamics", "Psychology", 
"Ophthalmology", "Ceramics", "Toxicology", "Neuroimaging", "Sociology", "Psychiatry", "Oncology", "biophysics", "Emergency Medicine", "Surgery", "Physiology", "Mycology", "Biomaterials"]

	assure_path_exists(output)
	print "Themes;Titles;Abstracts;Subjects;Keywords;All 4"
	for topics in list_themes :
		file_name_base = topics.replace(" ", "_")
		directoryT = file_name_base+"/"
		out_dir=os.path.join(output, directoryT)
		assure_path_exists(out_dir)
		abstract=babel_abst(topics)
		title=babel_title(topics)
		subj=babel_subj(topics)
		keywords=babel_keyword(topics)
		title_abs_subj_keywords=babel_title_abst_subject_keywords(topics)
		t = query(title)
		a = query(abstract)
		#inutile#########################
		#print_list_in_file (tb,os.path.join(output,file_name_base+"TitleAbs.txt"))
		#print t+"Title Abs :",len(tb)
		s = query(subj)
		k = query(keywords)
		#print_list_in_file (sk,os.path.join(output,file_name_base+"SubjectKeywords.txt"))
		#print t+"Subject Keywords :",len(sk)
		all_4 = query(title_abs_subj_keywords)
		#print_list_in_file (all_4,os.path.join(output,file_name_base+"All4.txt"))
		#print t+"All 4 :",len(all_4)
		#set_uncommon = find_B_less_A(tb, sk)
		#################################################
		print topics+";",len(t),";", len(a),";",len(s),";", len(k),";",len(all_4)
		out_t = os.path.join(out_dir, "Title")
		out_s = os.path.join(out_dir, "Subject")
		out_k = os.path.join(out_dir, "Keywords")
		out_a = os.path.join(out_dir, "Abstract")
		query_json(out_t, t)
		print_list_in_file (t,os.path.join(out_dir, "Title.csv"))
		query_json(out_a, a)
		print_list_in_file (a,os.path.join(out_dir, "Abstracts.csv"))
		query_json(out_s, s)
		print_list_in_file (s,os.path.join(out_dir, "Subjects.csv"))
		query_json(out_k, k)
		print_list_in_file (k,os.path.join(out_dir, "Keywords.csv"))

