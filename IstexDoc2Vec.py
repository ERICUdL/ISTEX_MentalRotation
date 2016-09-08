# -*- coding: utf-8 -*-
#
# This file is part of Beard.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

#Load and transform Istex abstracts into doc2vec representation.


# Author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author: Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2

# Thanks to ISTEX project for the foundings


import os, argparse
import json
from gensim.models.doc2vec import LabeledSentence, Doc2Vec
import string as st

class LoadFileJson() :
	def __init__(self):
		self.index = dict()
		self.count = 0

# loads randomly and as uniformly as possible in years, n istex doc
	def LoadDocumentsIstexAndUCBL(self, directory, ucbl) :
		first_year = 1990
		last_year = 2016
##UCBL data loading
		r=open(ucbl,'r')
		data=json.load(r)
		r.close()
		# for UCBL data
		for doc in data :
			line = doc["title"]+" __ " + doc["abstract"]
			wordsl = self.UnicodAndTokenize(line)
			try :
				yield LabeledSentence(words = wordsl ,tags=['DOC_%s' % str(self.count)]) # tags
				self.index["UCBL"+doc["doi"]] = str(self.count)
				self.count +=1
			except : continue
## ISTEX data loading
		for y in sorted(range(first_year,last_year), reverse=True) : # ordered to complete the list of documents to read in case the smallest files does not contain enough documents
			try :
				f=open(os.path.join(directory,str(y)+"json_perfect.json"), "r")
				js = json.load(f)
				f.close()
			except :
				print os.path.join(directory,str(y)+"json_perfect.json")
				print "Year failed ", y 
				pass
			try :
				f=open(os.path.join(directory, str(y)+"articles_json_perfect.json"), "r")
				js += json.load(f)
				f.close()
			except :
				print "Year article", y 
				pass
			for doc in  js: # choose randomly nb ids
				abstract = ""
				if "abstract" in doc :
					abstract = doc["abstract"]
				line = doc["title"]+" __ " + abstract
				wordsl = self.UnicodAndTokenize(line)
				try :
					yield LabeledSentence(words = wordsl ,tags=['DOC_%s' % str(self.count)])
					self.index["ISTEX"+doc["doi"]] = str(self.count)
					self.count +=1
				except : pass
		print self.count

	def UnicodAndTokenize(self,line) :
			try :
				line = line.encode('utf-8','ignore').decode('utf-8')
			except:
				line2=""
				for w in line.split() :
					try :
						line2+=w.encode('utf-8','ignore').decode('utf-8')+" "
					except :
						if w[-1] in ['?','.','!'] :
							line2+=w[-1]+" "
				line=line2.rstrip() # remove last space if it exists

			return line.lower().split()


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--istex_dir", default='sample_data/ISTEX/', type=str) #contains .json files
	parser.add_argument("--ucbl_file", default='sample_data/sportArticlesAsIstex.json', type=str) #is a .json file
	parser.add_argument("--output_file", default='UcblIstex_matrix_model', type=str) # is a file containing the model: you can use it with Doc2Vec.load
	parser.add_argument("--vec_size", default=300, type=int)
	parser.add_argument("--window", default=8, type=int)
	parser.add_argument("--min_count", default=5, type=int)
	parser.add_argument("--iter", default=5, type=int)

	args = parser.parse_args()
	istex = args.istex_dir
	ucbl = args.ucbl_file
	output = args.output_file
	v_size = args.vec_size
	window_size = args.window
	min_count = args.min_count
	n_iter = args.iter
	corpus = LoadFileJson()
	data = corpus.LoadDocumentsIstexAndUCBL(istex, ucbl) # "sportArticlesAsIstex.json"

	model = Doc2Vec(min_count=min_count, size=v_size, workers=6, iter=n_iter, window=window_size) # use fixe rate of learning
	model.build_vocab(data)

	# remove digits
	print "Vocabulary size before filtering numbers: " , len(model.vocab.keys())
	for voc in model.vocab.keys() :
		if voc.isdigit() :
			del model.vocab[voc]
	del model.vocab['__'] # separator of title/abstract

	print "Vocabulary size after filtering numbers: " , len(model.vocab.keys())

	model.train(data)
	print "corpus count", corpus.count

	f=open(output+"keysIndex","w")
	json.dump(corpus.index,f)
	f.close 
	Doc2Vec.save(model, output)
