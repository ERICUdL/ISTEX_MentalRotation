# This file is part of Istex_Mental_Rotation.
# Copyright (C) 2016 3ST ERIC Laboratory.
#
# This is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Download the corpus in istex with different formats : tei, txt, pdf: need to have an access to the API (most of the French universities are registered to ISTEX API)
# Select the documents according to the publication date. We also make a selection to download only  documents containing the key phrase "Mental Rotation" in the meta-data, for a specific project conducted with the STAPS department of UCBL.

# co-author : Lucie Martinet <lucie.martinet@univ-lorraine.fr>
# co-author : Hussein AL-NATSHEH <hussein.al-natsheh@ish-lyon.cnrs.fr>
# Affiliation: University of Lyon, ERIC Laboratory, Lyon2, University of Lorraine

# Thanks to ISTEX project for the funding

# You need to install jq (json is a lightweight and flexible command-line JSON processor)


################################################################################"
# Retrieve only the ISTEX ID of documents corresponding to the query
# Be aware we need first to check the number of documents you get, that need to be lower than --size nb or you will miss documents
# Store the results as json form with the option -O, -O- for the standard output
#find the size of the corpus to use

output_dir="JSON_RESULTS"
if [ ! -d $output_dir ]; then
	mkdir -p $output_dir
fi
out_years_json="JSON_Summarys/Json_by_years/"
if [ ! -d $output_dir ]; then
	mkdir -p $output_dir
fi

#Modify according to your wills
# The values we used
#min_year=1990
#max_year=2016

#Test values
min_year=2014
max_year=2015

for ((y=$min_year;y<=$max_year;y=y+1)) ; do
	# retrieve the number of documents corresponding to the query
	size=`wget 'https://api.istex.fr/document/?q=publicationDate:'$y' AND language:( "eng" OR "unknown" ) AND pdfPageCount:[3 60] AND abstractWordCount:[35 500] AND genre:("research-article" OR "conference [eBooks]" OR "article")&size=0' -O- -o /dev/null | jq '.total'`
	#download the istex ids of the documents corresponding to the query
	data=`wget 'https://api.istex.fr/document/?q=publicationDate:'$y' AND language:( "eng" OR "unknown" ) AND pdfPageCount:[3 60] AND abstractWordCount:[35 500] AND genre:("research-article" OR "conference [eBooks]" OR "article")&size='$size -O- -o /dev/null | jq ".hits[].id"`

	if [ ! -d $output_dir'/'$y ]; then
		mkdir $output_dir'/'$y
	fi
 
	echo $size
# download the meta data of the documents in the list
	for d in $data ;
	do
		doc=${d//\"}
		wget https://api.istex.fr/document/$doc/ -O $output_dir/$y/$doc.json -o /dev/null ;
		# to get the pdf, if you are allowed to access ISTEX data (French universities usually are):
		# wget https://api.istex.fr/document/$d/fulltext/pdf
		# wget https://api.istex.fr/document/$d/fulltext/tei
	done
	python jsonGenerate.py --input_dir $output_dir"/"$y --output_dir $out_years_json
	rm -rf $output_dir"/"$y
done

rm -rf $output_dir

#Test values
min_year=2013
max_year=2014

#specific request, with results summarized in one file only. All the documents here need to have "mental rotation" in the metadata
size=`wget 'https://api.istex.fr/document/?q="mental rotation" AND publicationDate:['$min_year' '$max_year'] AND language:( "eng" OR "unknown" ) AND pdfPageCount:[3 60] AND abstractWordCount:[35 500] AND genre:("research-article" OR "conference [eBooks]" OR "article")&size=0' -O- -o /dev/null | jq '.total'`
#download the metadata files
data=`wget 'https://api.istex.fr/document/?q="mental rotation" AND publicationDate:['$min_year' '$max_year'] AND language:( "eng" OR "unknown" ) AND pdfPageCount:[3 60] AND abstractWordCount:[35 500] AND genre:("research-article" OR "conference [eBooks]" OR "article")&size='$size -O- -o /dev/null | jq ".hits[].id"`

output_dir="MentalRotationJSONS/"
if [ ! -d $output_dir ]; then
	mkdir -p $output_dir
fi

echo $size
# download the meta data of the documents
for d in $data ;
do
	doc=${d//\"}
	wget https://api.istex.fr/document/$doc/ -O $output_dir/$doc.json -o /dev/null ;
	# to get the pdf, if you are allowed to access ISTEX data :
	# wget https://api.istex.fr/document/$d/fulltext/pdf
	# wget https://api.istex.fr/document/$d/fulltext/tei
done
python jsonGenerate.py --input_dir $output_dir --output_dir "JSON_Summarys/"

rm -rf $output_dir
