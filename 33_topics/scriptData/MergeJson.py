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

# Merge 2 json files, using a list of ids that have to be concatenated to the first json file, to avoid duplacation of documents.

import argparse
import json
import csv



def merge_2_json_from_listid (json_filebase, json_fileToAdd, list_csv_ToAdd, output_file_name) :
	with open(json_fileToAdd, "r") as to_add:
		added = json.load(to_add)

	with open(json_filebase, "r") as to_feel :
		feeled = json.load(to_feel)

	with open(list_csv_ToAdd, "r") as csv_file:
		titleonly = csv.reader(csv_file)
		list_csv = []
		for t in titleonly :
			list_csv.append(t[0])
	for f in  added :
		if f["istex_id"] in list_csv:
			feeled.append(f)

	fout = open(output_file_name, "w") 
	fout.write(json.dumps(feeled, indent=2)) 
	fout.close()



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--json_base", default='testAbstracts.json', type=str)
	parser.add_argument("--json_2add", default='testTitle.json', type=str)
	parser.add_argument("--csv_2add", default='testTitleUniq.csv', type=str)
	parser.add_argument("--json_output", default='mergedTitleAbstract.json', type=str)

	args = parser.parse_args()
	json_2add = args.json_2add
	json_base = args.json_base
	csv_2add = args.csv_2add
	json_output = args.json_output

	print json_2add
	print json_base
	merge_2_json_from_listid(json_base, json_2add, csv_2add, json_output)

