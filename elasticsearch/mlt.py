from elasticsearch import Elasticsearch, helpers
import numpy as np
import os, json, requests, argparse
from stop_words import get_stop_words
import pandas


es = Elasticsearch()
stop_words = get_stop_words('en')


def mlts_query(doc_types, max_size):
	q_size = 0
	for doc_type in doc_types:
		seeds = es.search(index="articles", doc_type=doc_type, size=max_size)
		seeds_size = seeds['hits']['total']
		q_size += seeds_size
	lst = np.array(range(q_size), dtype=np.object)

	for doc_type in doc_types:
		seeds = es.search(index="articles", doc_type=doc_type, size=max_size)
		ex = dict()
		ex["_index"] = "articles"
		ex["_type"] = doc_type
		for (i,d) in enumerate(seeds['hits']['hits']):
		    ex["_id"] = d['_id']
		    lst[i] = ex
	lst = lst.tolist()

# https://www.elastic.co/guide/en/elasticsearch/reference/5.1/query-dsl-mlt-query.html#_parameters_8

	mlt_query = {
	  "from": 0,
	  "size": 10000,
	  "_source": {
	    "includes": [
	      "istex_id",
	      "title",
	      "publicationDate"
	    ]
	  },
	  "query": {
	    "more_like_this": {
	      "fields": [
	        "title",
	        "abstract"
	      ],
		"like": lst,
#		"like_text" : "mental rotation",
		"min_term_freq" : 20,
		"max_query_terms" : 150,
#		"min_doc_freq" : 20,
#		"min_word_length" : ,
		"max_doc_freq" : 3965833, #~95% of the total number of documents (4174561)
#		"max_word_length" : ,
#		"stop_words" : stop_words,
#		"minimum_should_match" : ,

	    }
	  }
	}

	results = es.search(index="articles", doc_type="istex", body=mlt_query)

	return results['hits']['hits']

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--with_mental_rotation", default=1, type=int) # use 0 to only include seed articles
	parser.add_argument("--max_size", default=1000, type=int)

	args = parser.parse_args()
	with_mental_rotation = args.with_mental_rotation
	if with_mental_rotation:
		seed = ['seed', 'mr']
		output_file = 'mlt_results_with_testSet_inQuery.csv'
	else:
		seed = ['seed']
		output_file = 'mlt_results_only_seedSet_inQuery.csv'
	max_size = args.max_size
	results_list =  mlts_query(seed, max_size)

	res = np.array(range(len(results_list)), dtype=np.object)
	for i, doc in enumerate(results_list):
		res[i] = 'https://api.istex.fr/document/'+ doc['_source']['istex_id'] +'/fulltext/pdf'

	results = pandas.DataFrame()
	results['Articles'] = res
	results.to_csv(output_file)

	print 'results could be found in file:', output_file
	print 'number of results: ', len(results_list)
	print 'top 5 results: '
	for i, link in enumerate(res[:5]):
		print 'Rank:', i , 'Link to article:', link
