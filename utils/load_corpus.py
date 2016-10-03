# -*- coding: utf-8 -*-
#
# This file is part of Istex_Mental Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

#Load corpus data


# Author: Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr.>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2

# Thanks to ISTEX project for the foundings


import os
import json
from gensim.models.doc2vec import LabeledSentence
import string as st
import spacy.en 
parser = spacy.load('en')

class Lemmatizer(object):
 	def __init__(self):
 		self.parser = parser
 	def __call__(self, line):
 		line = self.parser(line)
 		return [t.lemma_ for t in line if not t.lemma_.isdigit()]

class Paragraphs(object):
	def __init__(self, istex=None, ucbl=None, wiki=None, tokenize=False, max_nb_wiki_paragraphs=None,
	                 paragraphs_per_article=None, istex_tag=None, wiki_tag=None):
		self.istex = istex
		self.ucbl = ucbl
		self.wiki = wiki
		self.tokenize = tokenize
		self.max_nb_wiki_paragraphs = max_nb_wiki_paragraphs
		self.paragraphs_per_article = paragraphs_per_article
		self.istex_tag = istex_tag
		self.wiki_tag = wiki_tag
		self.index = dict()
		self.inverse_index = dict()
		self.paper_count = 0
		self.wiki_count = 0

	def __iter__(self):
 
## UCBL data loading
		if self.ucbl is not None:
			ucbl = self.ucbl
			r=open(ucbl,'r')
			data=json.load(r)
			r.close()
			# for UCBL data
			for doc in data :
				line = doc["title"]+" __ " + doc["abstract"]
				if self.tokenize:
					u_line = self.to_unicode(line)
					words_lst = self.tokenize(u_line)
					try :
						self.yeild_element(words_lst, tag=self.istex_tag, count=self.paper_count)
						self.index["UCBL"+doc["doi"]] = str(self.paper_count)
						self.inverse_index[str(self.paper_count)] = "UCBL"+doc["doi"]
						self.paper_count += 1
					except : continue
				else:
					yield line
					self.index["UCBL"+doc["doi"]] = str(self.paper_count)
					self.inverse_index[str(self.paper_count)] = "UCBL"+doc["doi"]
					self.paper_count += 1
		self.ucbl_count = self.paper_count
## ISTEX data loading
		first_year = 1990
		last_year = 2016

		if self.istex is not None:
			istex = self.istex
			# ordered to complete the list of documents to read in case the smallest files does not contain enough documents
			for y in sorted(range(first_year,last_year), reverse=True) :
				try :
					f=open(os.path.join(istex,str(y)+"json_perfect.json"), "r")
					js = json.load(f)
					f.close()
				except :
					#print os.path.join(istex,str(y)+"json_perfect.json")
					#print "Year failed ", y 
					pass
				try :
					f=open(os.path.join(istex, str(y)+"articles_json_perfect.json"), "r")
					js += json.load(f)
					f.close()
				except :
					#print "Year article", y 
					pass
				for doc in  js:
					abstract = ""
					if "abstract" in doc :
						abstract = doc["abstract"]
					line = doc["title"]+" __ " + abstract
					if self.tokenize:
						u_line = self.to_unicode(line)
						words_lst = self.tokenize(u_line)
						try :
							self.yield_element(words_lst, tag=self.istex_tag, count=self.paper_count)
							self.index["ISTEX"+doc["doi"]] = str(self.paper_count)
							self.inverse_index[str(self.paper_count)] = "ISTEX"+doc["doi"]
							self.paper_count += 1
						except : pass
					else:
						yield line
						self.index["ISTEX"+doc["doi"]] = str(self.paper_count)
						self.inverse_index[str(self.paper_count)] = "ISTEX"+doc["doi"]
						self.paper_count += 1
		self.istex_count = self.paper_count - self.ucbl_count
## Wikipedia data itteration
		if self.wiki is not None:
			wiki = self.wiki
			for sub in os.listdir(wiki):
				subdir = os.path.join(wiki, sub)
				for fname in os.listdir(subdir):
					paragraphs_per_article_count = 0
					for line in open(os.path.join(subdir, fname)): # each line represent a paragraph in wiki article

						if self.max_nb_wiki_paragraphs is not None and self.wiki_count >= self.max_nb_wiki_paragraphs:
							break

						if len(line.split()) > 2 and line[:8] != '<doc id=': # to verify if the line is a paragraph 
							if self.tokenize:
								u_line = self.to_unicode(line)
								words_lst = self.tokenize(u_line)
								self.yield_element(words_lst, tag=self.wiki_tag, count=self.wiki_count)
							else:
								yield line
							self.wiki_count += 1

							if self.paragraphs_per_article is not None:
								paragraphs_per_article_count += 1

								if paragraphs_per_article_count >= self.paragraphs_per_article:
									break

			print 'number of wikipedia paragraphs: ', self.wiki_count

		print 'number of ISTEX abstracts: ', self.paper_count
		print 'total number of paragraphs and abstracts: ', self.count()
		print 'number of ucbl articles: ', self.ucbl_count
		print 'number of istex articles other than ucbl: ', self.istex_count

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
		count = self.paper_count + self.wiki_count
		return count
