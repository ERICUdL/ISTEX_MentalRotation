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
import random

class ParagraphsDict(object):
	def __init__(self, istex_mr=None, ucbl=None, istex_dir=None, nb_selec = 0):
		self.istex_mr = istex_mr
		self.ucbl = ucbl
		self.istex_dir = istex_dir
		self.istex_mr = istex_mr
		self.index = dict()
		self.inverse_index = dict()
		self.ucbl_count = 0
		self.mr_count = 0
		self.istex_count = 0
		self.nb_selec = nb_selec
		self.dict = dict()

	def create_dict(self):
## UCBL data loading
		if self.ucbl is not None:
			ucbl = self.ucbl
			r=open(ucbl,'r')
			data=json.load(r)
			r.close()
			# for UCBL data
			for doc in data :
				line = doc["title"]+" __ " + doc["abstract"]

				self.dict["UCBL_"+doc["istex_id"]] = line
				self.index["UCBL_"+doc["istex_id"]] = str(self.count())
				self.ucbl_count += 1

## ISTEX Mental Rotation data loading
		if self.istex_mr is not None:
			istex_mr = self.istex_mr
			r=open(istex_mr,'r')
			data=json.load(r)
			r.close()
			for doc in data :
				line = doc["title"]+" __ " + doc["abstract"]
				self.dict["MRISTEX_"+doc["istex_id"]] = line
				self.index["MRISTEX_"+doc["istex_id"]] = str(self.count())
				self.mr_count += 1

## Istex data selection of documents iteration
# set nb doc to selection: add as a parametter

		if self.istex_dir is not None:
			istex_dir = self.istex_dir
			#create a loop to count the total number of documents
			total_nb_docs = 0
			for fname in os.listdir(istex_dir):
				for doc in json.load(open(os.path.join(istex_dir, fname))):
					total_nb_docs+=1
			tmp_nb_docs = 0	
			l_doc_id=range(total_nb_docs)		
			selected_ids = random.sample(l_doc_id, self.nb_selec) # verify if it is the good function
			print selected_ids
			for fname in os.listdir(istex_dir):
				for doc in json.load(open(os.path.join(istex_dir, fname))):
					tmp_nb_docs+=1					
					if tmp_nb_docs in selected_ids :
						print tmp_nb_docs
						line = doc["title"]+" __ " + doc["abstract"]
						self.dict["ISTEX_"+doc["istex_id"]] = line
						self.index[self.count()] = "ISTEX_"+doc["istex_id"]
						self.istex_count += 1

		print 'number of ISTEX MR abstracts: ', self.mr_count
		print 'total number of paragraphs and abstracts: ', self.count()
		print 'number of ucbl articles: ', self.ucbl_count
		print 'number of istex articles other than ucbl: ', self.istex_count
		return self.dict


	def to_unicode(self,line) :
			try :
				line = line.encode('utf-8','ignore').decode('utf-8')
			except:
				line2 = ""
				for w in line.split() :
					try :
						line2+=w.encode('utf-8','ignore').decode('utf-8')+" "
					except :
						if w[-1] in ['?','.','!'] :
							line2 += w[-1] + " "
				line = line2.rstrip() # remove last space if it exists
			return line

	def tokenize(self, line):

		lst = line.lower().split()
		lst = [ i for i in lst if not i.isdigit()]
		return lst

	def yield_element(self, words_lst, tag=None, count=None):
		if tag is not None:
			yield LabeledSentence(words=words_lst ,tags=[tag+'_%s' % str(count)])
		else:
			yield words_lst

	def count(self):
		count = self.mr_count + self.istex_count + self.ucbl_count
		return count


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--ucbl_file", default='sample_data/sportArticlesAsIstex_UniqID_183.json', type=str) # is a .json file
	parser.add_argument("--istex_dir", default='sample_data/ISTEX/', type=str) # path to ISTEX corpus
	parser.add_argument("--istex_mr", default='sample_data/MentalRotationInMetaDataIstexWithoutAnnotated.json', type=str) # is a .json file
	parser.add_argument("--nb_selec", default=400, type=int) # number of smples
	parser.add_argument("--out_file", default='LDA_sampled_input.pickle', type=str) # name of the output file
	parser.add_argument("--out_dir", default='results', type=str) # name of the output directory

	args = parser.parse_args()
	ucbl = args.ucbl_file
	istex_mr = args.istex_mr
	istex_dir = args.istex_dir
	nb_selec = args.nb_selec
	out_file = args.out_file
	out_dir = args.out_dir

	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	paragraphs = ParagraphsDict(istex_mr=istex_mr, ucbl=ucbl, istex_dir=istex_dir, nb_selec=nb_selec)
	dict_par = paragraphs.create_dict()
	
	pickle.dump(dict_par, open(os.path.join(out_dir, out_file), "w"))
	print 'response file could be found at: ', os.path.join(out_dir, out_file)
