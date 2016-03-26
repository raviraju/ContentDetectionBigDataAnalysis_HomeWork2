#! /usr/bin/env python
import sys
import os
import json
import time
from pprint import pprint
import scholar
from scholar import ScholarQuerier
from scholar import ScholarSettings
from scholar import SearchScholarQuery

def getPublications(authors):
	print authors
	querier = ScholarQuerier()
	settings = ScholarSettings()
	querier.apply_settings(settings)
	query = SearchScholarQuery()

	publications = []
	for author in authors:
		if len(author) > 0:
			print "Author : ", 
			print author
			query.set_author(author)
			querier.send_query(query)
			related_list = scholar.json(querier)
			if related_list:
				print "No of related publications found : ",
				print len(related_list)
				for item in related_list:
					publications.append(item)
					#print item
			time.sleep(10);
	return publications
	#with open('output.json', 'a') as outfile:
	#	json.dump(publications, outfile, indent = 4)

def fetchScholarInfo(input_file):
	#input_file = sys.argv[1];
	print "fetchScholarInfo : " + input_file
	with open(input_file) as json_file:
		jsondict = json.load(json_file)
		#pprint(d)
	#print jsondict.keys();
	
	authors = [];
	if 'grobid_Authors' in jsondict.keys():
		for author_info in jsondict['grobid_Authors']:
			for author in author_info.split("1"):
				authors.append(author.strip());
				
		jsondict["relatedPub"] = getPublications(authors)
		print "Total No of related publications found : ",
		print len(jsondict["relatedPub"])
		
		with open(input_file, 'w') as json_file:
			json.dump(jsondict, json_file, indent = 4)
	else:
		print "grobid_Authors TEI info not_found...Skipping"
	

def main():
	if len(sys.argv) != 2:
		print "usage : python fetchScholar.py <path_to_json_files>"
		return 0
	input_dir = sys.argv[1]
	dirs = os.listdir(input_dir)
	# This would print all the files and directories
	for file in dirs:
		fetchScholarInfo(input_dir + file)
	
if __name__ == "__main__":
    sys.exit(main())
