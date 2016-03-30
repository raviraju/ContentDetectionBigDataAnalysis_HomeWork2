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
import random

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
			#time.sleep(random.randrange(10, 40, 2));
			time.sleep(60);
	return publications
	#with open('output.json', 'a') as outfile:
	#	json.dump(publications, outfile, indent = 4)
	
def blocked():
	#time.sleep(random.randrange(10, 40, 2));
	time.sleep(120);
	publications = []
	querier = ScholarQuerier()
	settings = ScholarSettings()
	querier.apply_settings(settings)
	query = SearchScholarQuery()
	query.set_author("Ryan Baker")
	querier.send_query(query)
	related_list = scholar.json(querier)
	if related_list:
		print "No of related publications found : ",
		print len(related_list)
		for item in related_list:
			publications.append(item)
	if len(publications) == 0:
		print publications
		return True
	else:
		return False
		
def fetchScholarInfo(input_dir, fileName, doiDict, resultPath):
	input_file = input_dir + fileName
	#input_file = sys.argv[1];
	print "fetchScholarInfo : " + input_file
	with open(input_file) as json_file:
		jsondict = json.load(json_file)
		#pprint(d)
	#print jsondict.keys();
	
	
	fileNameKey = fileName.rstrip(".json")
	if doiDict.has_key(fileNameKey):
		print "Setting DOI : ",
		print fileNameKey
		jsondict["doi"] = doiDict[fileNameKey]
	else:
		print "Cannot set DOI for :",
		print fileName
	
	authors = [];
	if 'grobid__header_Authors' in jsondict.keys():
		#print "To be processed later: ",
		#print fileName
		#return
		for author_info in jsondict['grobid__header_Authors']:
			for author in author_info.split("1"):
				authors.append(author.strip());
		if blocked():
			print "we are blocked, cannot proceed"
			exit(0);
				
		jsondict["relatedPub"] = getPublications(authors)
		print "Total No of related publications found : ",
		print len(jsondict["relatedPub"])
		
		#with open(input_file, 'w') as json_file:
		#	json.dump(jsondict, json_file, indent = 4)
	else:
		print "grobid_Authors TEI info not_found...Skipping"
		
	with open(input_file, 'w') as json_file:
		json.dump(jsondict, json_file, indent = 4)
	print "Moved file :",
	print fileName
	os.rename(input_dir + fileName, resultPath + fileName)
	

def main():
	if len(sys.argv) != 4:
		print "usage : python fetchScholar.py <path_to_json_files> <path_to_doi> <result_path_to_json_files>" 
		return 0
	
	resultPath = sys.argv[3]
	
	doi = sys.argv[2]
	doiDict = {}
	with open(doi, "r") as f:
		for line in f:
			key = line.split('/')[-1]
			doiDict[key.rstrip('\r\n')] = line.rstrip('\r\n')
	with open("doiDict.json", 'w') as json_file:
		json.dump(doiDict, json_file, indent = 4)

	input_dir = sys.argv[1]
	dirs = os.listdir(input_dir)
	for fileName in dirs:
		fetchScholarInfo(input_dir, fileName, doiDict, resultPath)
	
if __name__ == "__main__":
    sys.exit(main())
