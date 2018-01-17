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


# script to create the json list of documents for 33 topics.

# Step 1: harvets the json information for each document of the 33 topics
# for each topic, we store the json file in a different directory, according to the place of the keyword (fields: title, abstract, keywords, subject): a subdirectory for each field is build.
# we separate the fields in the request to be able to harvest more documents, since the API restricts to 10000 the number of results we can consult.
python SelectIfTheme.py --output_dir  ThemesIstexIdList > test.log

#Step 2
#extract from the jsons file only the json elements we need for the experiment and compile all the interesting json information of the documents in one json file (actually 2 : one for abstract and title, one for subject, since we have no results for keyword.) The results are stored in a new directory : JSONPerfect
#We also create a directory containing csv file that are only a list of the istex_id of the documents for each topic, per field.
# You have to change the list of topics if you want to proceed a specific one or all the topics at the same time.
# By default, we only work on Artificial Intelligence.
# This script creates a lot of results since it stores the errors if any, distinguish all the json and only the json that have all the information required for the experiment.
# the main interesting directories are JSONPerfect and AllCSVPerfect
./CreateJsonSummary.sh

#Merge the results of abstract/title data, since we need them together for the experiment.
# we are supposed to do the same for subject/keyword, but since there are no keyword, we just move the interesting files.
# CSV are in CSV_Merged
# JSON are in JSON_Merged
# BE CAREFULL : the code do not take into account errors due to empty files or bad format. It seems that sometimes, ./CreateJsonSummary.sh produce unterminated .json file. I was not able to reproduce the error afterwards.
./mergeFiles.sh
