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
import numpy as np

def get_article_by_istex_id(istex_ids, istex_dir):
	size = len(istex_ids)
	res = np.array(range(size), dtype=np.object)
	i = 0
	for fname in os.listdir(istex_dir):
		for doc in json.load(open(os.path.join(istex_dir, fname))):
			istex_id = doc["istex_id"]
			if istex_id in istex_ids :
				article = dict()
				article['text'] = doc["title"] + " __ " + doc["abstract"]
				article['publicationDate'] = doc["publicationDate"]
				article["istex_id"] = doc["istex_id"]
				res[i] = article
				i += 1
	res = res.tolist()
	res = res[:i]
	return res
if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--results_file", default='results/istex_mr_top10k_vec150results.pickle', type=str)
	parser.add_argument("--istex_dir", default='sample_data/ISTEX/', type=str)
	parser.add_argument("--out_file", default="chart_input.json", type=str) # name of the output file
	parser.add_argument("--out_dir", default="results", type=str) # name of the output directory

	args = parser.parse_args()
	results_file = args.results_file
	istex_dir = args.istex_dir
	out_file = args.out_file
	out_dir = args.out_dir

	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	results = pickle.load(open(results_file,'rb'))
	istex_ids = results.keys()
	print "length of the results keys (istex_ids): ", len(istex_ids)

	articles = get_article_by_istex_id(istex_ids, istex_dir)
	json.dump(articles, open(os.path.join(out_dir, out_file), "w"), indent=2)
	print 'length of response file: ', len(articles)
	print 'response file could be found at: ', os.path.join(out_dir, out_file)
