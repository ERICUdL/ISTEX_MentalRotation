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

# Script to merge by pairs the json files per  topic according to their field where the topic appears.

l=("Artificial_Intelligence" "Information_Systems" "Rehabilitation" "Philosophy" "Microscopy" "Infectious_Diseases" "Respiratory_System" "Literature" "Robotics" "Pediatrics" "Mechanics" "Condensed_Matter" "Transplantation" "Religion" "Pathology" "Immunology" "Nursing" "Substance_Abuse" "Thermodynamics" "Psychology" "Ophthalmology" "Ceramics" "Toxicology" "Neuroimaging" "Sociology" "Psychiatry" "Oncology" "biophysics" "Emergency_Medicine" "Surgery" "Physiology" "Mycology" "Biomaterials")

json_dir="JSONPerfect"
csv_dir="AllCSVPerfect"
tmp="tmp"
merged_json="JSON_Merged"
merged_csv="CSV_Merged"

#l=("Artificial_Intelligence")

if [ ! -d $tmp ]; then
	mkdir -p $tmp
fi

if [ ! -d $merged_csv ]; then
	mkdir -p $merged_csv
fi

if [ ! -d $merged_json ]; then
	mkdir -p $merged_json
fi

for main_file in "${l[@]}" 
do 
	tmp_abstract_csv=$tmp'/'$main_file'_Abstract.csv'
	tmp_abstract_json=$tmp'/'$main_file'_Abstract.json'
	tmp_title_uniq_csv=$tmp'/'$main_file'_TitleUniq.csv'
	tmp_merged_titleabstract_csv=$merged_csv'/'$main_file'_AbstractTitle.csv'
	tmp_title_csv=$tmp'/'$main_file'_Title.csv'
	tmp_title_json=$tmp'/'$main_file'_Title.json'
	
	tmp_keywords_csv=$tmp'/'$main_file'_Keywords.csv'
	tmp_keywords_json=$tmp'/'$main_file'_Keywords.json'
	tmp_subject_uniq_csv=$tmp'/'$main_file'_SubjectUniq.csv'
	tmp_merged_subjectkeywords_csv=$merged_csv'/'$main_file'_KeywordsSubject.csv'
	tmp_subject_csv=$tmp'/'$main_file'_Subject.csv'
	tmp_subject_json=$tmp'/'$main_file'_Subject.json'
# remove the first line that explains the format of the file and move the results to tmp
	sed 1d $csv_dir'/'$main_file'_Abstractperfect_doc.csv' > $tmp_abstract_csv
	sed 1d $csv_dir'/'$main_file'_Titleperfect_doc.csv' > $tmp_title_csv
	title_uniq=$tmp'/'$main_file'_TitleUniq.csv'

	sed 1d $csv_dir'/'$main_file'_Keywordsperfect_doc.csv' > $tmp_keywords_csv
	sed 1d $csv_dir'/'$main_file'_Subjectperfect_doc.csv' > $tmp_subject_csv
	subject_uniq=$tmp'/'$main_file'_SubjectUniq.csv'

	
	# select only documents in title but not in abstract
	sort $tmp_abstract_csv $tmp_abstract_csv $tmp_title_csv > $tmp_title_uniq_csv
	sort $tmp_keywords_csv $tmp_keywords_csv $tmpsubject_csv > $tmp_subject_uniq_csv
	#create the merged file in a csv format.
	cat $tmp_abstract_csv $tmp_title_csv | sort -u > $tmp_merged_titleabstract_csv
	cat $tmp_keywords_csv $tmp_subject_csv | sort -u > $tmp_merged_subjectkeywords_csv

	#cp $json_dir'/'$main_file'_Title_json_perfect.json' $tmp
	#cp $json_dir'/'$main_file'_Abstract_json_perfect.json' $tmp
	#cp $json_dir'/'$main_file'_Subject_json_perfect.json' $tmp
	#cp $json_dir'/'$main_file'_Keywords_json_perfect.json' $tmp
	json_base_AT=$json_dir'/'$main_file'_Abstract_json_perfect.json'
	json_2add_AT=$json_dir'/'$main_file'_Title_json_perfect.json'
	json_output_AT=$merged_json'/'$main_file'_AbstractTitle.json'
	#json_base_SK=$json_dir'/'$main_file'_Keywords_json_perfect.json'
	#json_2add_SK=$json_dir'/'$main_file'_Subject_json_perfect.json'
	#json_output_SK=$merged_json'/'$main_file'_KeywordsSubject.json'


python MergeJson.py --json_base $json_base_AT --json_2add $json_2add_AT --csv_2add $tmp_title_uniq_csv --json_output $json_output_AT
# The next liine should be used in case there are keywords files, but until now there are not
#python AllCSVPerfect/testMerge/TestPythonMergeJson.py --json_base $json_base_SK --json_2add $json_2add_SK --csv_2add $tmp_subject_uniq_csv --json_output $json_output_SK
	rm $tmp'/'*
done
