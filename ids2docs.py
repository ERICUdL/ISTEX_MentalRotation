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

def get_doc_by_istex_id(istex_ids, istex_dir):
	res = dict()
	for fname in os.listdir(istex_dir):
		for doc in json.load(open(os.path.join(istex_dir, fname))):
			istex_id = doc["istex_id"]
			if istex_id in istex_ids :
				line = doc["title"] + " __ " + doc["abstract"]
				res["ISTEX_"+istex_id] = line
	return res

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--results_file", default='results/results.pickle', type=str)
	parser.add_argument("--istex_dir", default='sample_data/ISTEX/', type=str)
	parser.add_argument("--out_file", default="LDA_res_input.pickle", type=str) # name of the output file
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

	dict_par = get_doc_by_istex_id(istex_ids, istex_dir)
	pickle.dump(dict_par, open(os.path.join(out_dir, out_file), "w"))
	print 'length of response file: ', len(dict_par)
	print 'response file could be found at: ', os.path.join(out_dir, out_file)
