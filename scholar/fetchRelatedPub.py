#! /usr/bin/env python
import sys
import json
from pprint import pprint
import scholar
from scholar import ScholarQuerier
from scholar import ScholarSettings
from scholar import SearchScholarQuery

def getPublications(author):
	print author
	querier = ScholarQuerier()
	settings = ScholarSettings()
	querier.apply_settings(settings)
	query = SearchScholarQuery()
	query.set_author(author)
	querier.send_query(query)
	#scholar.csv(querier)
	scholar.txt(querier, with_globals=False)

def main():
	if len(sys.argv) != 2:
		print "usage : python fetchRelatedPub.py file_author_names.json"
		return 0
	input_file = sys.argv[1];
	#print "file to be parsed", input_file
	with open(input_file) as json_data:
		jsondict = json.load(json_data)
		#pprint(d)
	for item in jsondict.items():
		filename 	= item[0]
		authors		= item[1]
		for author in authors:
			#print author
			getPublications(author)
	
if __name__ == "__main__":
    sys.exit(main())
