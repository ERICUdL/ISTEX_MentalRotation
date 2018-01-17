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




# script to pass from a directory of .json file, to one file.json, summarizing all the documents.
#main_dir="Artificial_Intelligence"
#l=("Artificial_Intelligence" "Information_Systems" "Rehabilitation" "Philosophy" "Microscopy" "Infectious_Diseases" "Respiratory_System" "Literature" "Robotics" "Pediatrics" "Mechanics" "Condensed_Matter" "Transplantation" "Religion" "Pathology" "Immunology" "Nursing" "Substance_Abuse" "Thermodynamics" "Psychology" "Ophthalmology" "Ceramics" "Toxicology" "Neuroimaging" "Sociology" "Psychiatry" "Oncology" "biophysics" "Emergency_Medicine" "Surgery" "Physiology" "Mycology" "Biomaterials")
l=("Artificial_Intelligence")
subdir_S="Subject"
subdir_T="Title"
subdir_A="Abstract"
subdir_K="Keywords"

results_all_json="AllJSONPerfect"
if [ ! -d $results_all_json ]; then
	mkdir -p $results_all_json
fi

results_json="JSONPerfect"
if [ ! -d $results_json ]; then
	mkdir -p $results_json
fi

results_csv="AllCSVPerfect"
if [ ! -d $results_csv ]; then
	mkdir -p $results_csv
fi

for main_dir in "${l[@]}"
do
	l_dir=($subdir_T $subdir_A $subdir_S $subdir_K)
	for d in "${l_dir[@]}"
	do
		dir_out="ThemesIstexIdList/"$main_dir"/"$d
		output_dir="$results_all_json/$main_dir"
		if [ ! -d $output_dir ]; then
			mkdir -p $output_dir
		fi
		output_dirs="$output_dir/"$d"JSON"
		echo $output_dir
		echo $output_dirs
		if [ ! -d $output_dirs ]; then
			mkdir -p $output_dirs
		fi
		python jsonGenerateGeneric.py --input_dir $dir_out --output_dir $output_dirs --verbose
		# faut préciser les noms de fichiers !!
		cp $output_dirs/*json_perfect*.json $results_json"/"$main_dir"_"$d"_json_perfect.json"
		sed 's/.*\///g' $output_dirs/*perfect_doc.txt | sed 's/\..*//g' > $results_csv"/"$main_dir"_"$d"perfect_doc.csv"
	done
done






#python ../IstexDataDownload/jsonGenerateGenericWithoutYear.py --input_dir $main_dir"/"$subdir_SK --output_dir $output_dirsk --verbose


#python ../IstexDataDownload/jsonGenerateGenericWithoutYear.py --input_dir $main_dir"/"$subdir_TA --output_dir $output_dirta --verbose
