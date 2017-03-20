from datetime import datetime
from elasticsearch import Elasticsearch, helpers
import numpy as np
import os, json, requests, argparse

es = Elasticsearch()
#es.indices.create(index='articles', ignore=400)

def json2actions(json_file, _index="articles", _type="mr", start_index=0,  op_type='index'):
	print json_file
	r=open(json_file,'r')
	data=json.load(r)
	r.close()

	size= len(data)
	print size
	actions = np.array(range(size),dtype=np.object)
	_id = start_index
	i = 0
	for doc in data :
		action = {
			'_op_type': op_type,
			"_index": _index,
			"_type": _type,
			"_id": _id,
			"_source": doc,
			}
		actions[i] = action
		i += 1
		_id += 1

	actions = actions.tolist()

	return actions, _id

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("--mr", default='../../ISTEX_MentalRotation/sample_data/MentalRotationInMetaDataIstexWithoutAnnotated.json', type=str) # contains .json files

	args = parser.parse_args()
	mr = args.mr
	start_index = 0

	actions, start_index = json2actions(mr, _index="articles", _type="mr", start_index=start_index, op_type='index')

	try:
		helpers.bulk(es, actions)
	except:
		print actions[0]
		print '____________________________________________________________'
