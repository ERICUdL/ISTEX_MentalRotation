#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.


"""This is a script to read different json files containing meta-data of documents. 
If nothing specified, the script generates a .json file containing specific keys for each document, not taking into account the documents that have missing requiered keys (that you can list yourself if wanted).
The script can also collect all the meaningful information and create new json files listing all the documents and their characteristics : the documents are split into 2 .json files, one for the complete documents, one for all the documents even those which have some keys missing. In addition, we list the documents ids in 2 files: the complete one, and the possibily incomplete ones."""

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2, University of Lorraine

# Thanks to ISTEX project for the funding

import os, argparse
import json
from nltk.corpus import stopwords
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def ListAuthors(jsonList) :
	l = []
	for i in jsonList["author"] :
		a=dict() ;
		a["name"]=i["name"]
		l.append(a)
	return l

# Read json file and extract some given keys to build another json file, with only selected information. 
'''fileName : input file,
   key_words_list : list of items that can have two possible formats : "key1" the keys to retrieve and keep for the new resulting json file, or "key1:keyBis1" "key1" is the key that was found in the data file, "keyBis1" is the key name to use in the resulting
   f_perfect : pointer to the open file containing the json information of the documents with all the required key words (present in key_word_list)
   prec = characters that have to precede the selected json information in the resulting files containing all the documents, even with some keys missing, mostly "[" or ","
   prec_perf = characters that have to precede the selected json information in the resulting files containing the documents with all keys present in the given data file, mostly "[" or ","
   perfectdoc_list: pointer on a file that will contain the list of documents path containing all the required keys (information file)
   f_all_docs : pointer to the open file containing all the json information of all the given  documents  (information file)
   f_errors : pointer on a file that will contain the list of path of all the documents wit missing keys and the name of the missing keys for each (information file)
   generate_key_words : do we generate key_words from the title
   stop : list of stop words if generate_key_words=True
   source : specify the source of the corpus
   verbose : do we generate the information files
 json_all: pointer on an open file, f_perfect: pointer on open file, stop: list of stop word to remove from key words, prec_perf: string to add before the json info, perfectdoc_list: string containing file name, excepterrors_list: string containing file name'''

def ReadJson (input_file_name, key_words_list, f_perfect, prec=",", prec_perf=",", perfectdoc_list=None, f_all_docs=None, f_errors = None, generate_key_words = False, stop_words=[], source="", verbose = False):
	nb_errors = 0
	list_errors = ""
	with open(input_file_name) as data_file:    
		data = json.load(data_file)
	data_file.close()
	data2 = {}
	for kw in key_word_list :
		l_key = kw.split(":")
		if l_key[0] ==  "host" :
			try : data2[l_key[-1]]={"corpusName":data["corpusName"],"title":data["host"]["title"], "volume":data["host"]["volume"]}
			except :
				nb_errors+=1
				list_errors += "host: corpusName, title, volume ; "

		elif l_key[0] == "doi" :
			try :
				data2[l_key[-1]]=data[l_key[0]][0]
			except : 
				nb_errors+=1
				list_errors += "doi ; " 
		elif l_key[0]=="authors":
			try :
				l=ListAuthors(data)
				data2["authors"]=l 
			except :	
				nb_errors+=1
				list_errors += "authors ; "
		else :
			try : 
				data2[l_key[-1]]=data[l_key[0]] # if a different key is specified for the new json file, use it: this key is the last element of the l_key list
			except : 
				nb_errors+=1
				list_errors += kw+"; "
				
	if generate_key_words :
		try :
			data2["KeyWords"]=[ i for i in data["title"].split() if i.lower() not in stop ]
		except:
			nb_errors+=1
			list_errors += "KeyWords ; "

	data2["source"]=["Istex"]
	if(nb_errors == 0) :
		if verbose :
			perfectdoc_list.write(input_file_name+"\n")
		f_perfect.write(prec_perf)
		json.dump(data2, f_perfect)
		if verbose :
			f_all_docs.write(prec)
			json.dump(data2, f_all_docs)

	elif verbose :
		f_all_docs.write(prec)
		json.dump(data2, f_all_docs)
		f_errors.write("Something missing with :" + input_file_name + "nb errors = " + str(nb_errors) + " ; " + list_errors + "\n")

	return nb_errors



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_dir", default='2014', type=str) #year to compute: it is also the
	parser.add_argument("--year", default='2014', type=str) #year to compute: it is also the name of the directory containing the original .json
	parser.add_argument("--output_dir", default="MentalRotationJSONS", type=str)
	parser.add_argument("--verbose", action='store_true', help="Print number of documents with missing keys, store the list of this document in a .txt and another file with the documents that contain all the key words. Gives also the .json with incomplete keys in json_all.json")
	parser.add_argument("--generate_key_words", action='store_true', help="Automatically generate the key words from the title")
	parser.add_argument("--source", default='Istex', type=str)
	parser.add_argument("--json_keys", default=["id:istex_id", "publicationDate", "title","abstract"], type=str, nargs='+', help="List the key word used in istex, then the one you want to use for your own json file, separated by ':'. Sample : \"host:host\", \"id:istex_id\", \"publicationDate:publicationDate\",  \"title\":\"title\", \"abstract\":\"abstract\", \"doi\":\"doi\"") # it is a sample based on the syntaxe of istex .json metadata files
	
	args = parser.parse_args()
	year = args.year
	input_dir = args.input_dir
	output_dir = args.output_dir	
	source = args.source
	verbose = args.verbose
	key_word_list = args.json_keys
	generate_key_words = args.generate_key_words

	if not os.path.exists(os.path.dirname(output_dir)):
		os.makedirs(os.path.dirname(output_dir))

	dirName=input_dir
	if verbose :
		excepterrors_list=os.path.join(output_dir, input_dir.rstrip('/').split("/")[-1]+"exceptionFilesErrors.txt")
		f_errors = open(excepterrors_list,"w")
		f_errors.write('Errors starts\n')
		alldoc_file=os.path.join(output_dir, input_dir.rstrip('/').split("/")[-1]+"json_all.json")
		f_all_docs=open(alldoc_file,"w")
		perfectdoc_list=os.path.join(output_dir, input_dir.rstrip('/').split("/")[-1]+"perfect_doc.txt")
		perf_f = open(perfectdoc_list, "w")
		perf_f.write("List of documents containing all the required key words\n")

	f_perfect=open(os.path.join(output_dir, input_dir.rstrip('/').split("/")[-1]+"json_perfect.json"), "w")

	if generate_key_words :
		stop = stopwords.words('english')
	else : stop = []
	prec="[\n"
	prec_perf = "[\n" 
	nb_doc_with_errors = 0
	nb_docs = 0
	for f in  os.listdir(dirName):
		nb_docs += 1
		pathdata=os.path.join(dirName, f)
		if verbose :	
			nb_errors=ReadJson(pathdata, key_word_list, f_perfect, prec, prec_perf, perfectdoc_list=perf_f, f_all_docs=f_all_docs, f_errors = f_errors, generate_key_words = generate_key_words, stop_words=stop,  source=source, verbose = True) 
		else :
			nb_errors=ReadJson(pathdata, key_word_list,f_perfect,  prec, prec_perf, generate_key_words = generate_key_words, stop_words=stop, source=source) 
		if nb_errors == 0 :
			prec_perf=",\n"
		if nb_errors > 0 :
			nb_doc_with_errors += 1
		prec=",\n"
			
	prec="]\n"
	if verbose :
		f_all_docs.write(prec)
		f_all_docs.close()
		f_errors.close()
		perf_f.close()
	f_perfect.write(prec)
	f_perfect.close()
	print "Total number of documents: ", nb_docs
	print "Number of documents with missing key(s): ", nb_doc_with_errors
