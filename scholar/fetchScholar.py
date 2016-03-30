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
			print "Using Author : ", 
			print author
			query.set_author(author)
			querier.send_query(query)
			related_list = scholar.json(querier)
			if related_list:
				print "No of related publications found : ",
				print len(related_list)
				for item in related_list:
					#print item.keys()
					#item["relatedAuthor"] = author
					publications.append(item)
			#time.sleep(random.randrange(10, 40, 2));
			time.sleep(20);
	return publications

def getPublications_Title(title):
	querier = ScholarQuerier()
	settings = ScholarSettings()
	querier.apply_settings(settings)
	query = SearchScholarQuery()
	publications = []
	query.set_words(title)
	querier.send_query(query)
	related_list = scholar.json(querier)
	if related_list:
		print "No of related publications found : ",
		print len(related_list)
		for item in related_list:
			#print item.keys()
			#item["relatedTitle"] = title[0]
			publications.append(item)
	#time.sleep(random.randrange(10, 40, 2));
	#time.sleep(60);
	return publications
	
def blocked():
	print "Test if blocked...."
	#time.sleep(random.randrange(10, 40, 2));
	time.sleep(60);
	publications = []
	querier = ScholarQuerier()
	settings = ScholarSettings()
	querier.apply_settings(settings)
	query = SearchScholarQuery()
	query.set_author("Ryan Baker")
	querier.send_query(query)
	related_list = scholar.json(querier)
	if related_list:
		print "Block Test : No of related publications found : ",
		print len(related_list)
		for item in related_list:
			publications.append(item)
	if len(publications) == 0:
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
		print "Setting DOI for : ",
		print fileNameKey
		jsondict["doi"] = doiDict[fileNameKey]
	else:
		print "Cannot set DOI for :",
		print fileName
		
	#if blocked():
	#	print "we are blocked, cannot proceed"
	#	exit(0);
	
	if 'grobid__header_Title' in jsondict.keys():
		if blocked():
			print "we are blocked, cannot proceed"
			exit(0);
		relatedPublDataList = getPublications_Title(jsondict['grobid__header_Title'])
		print "Using Title, Total No of related publications found : ",
		print len(relatedPublDataList)
		
		jsondict["relatedPub_ClusterID"] 	= []
		jsondict["relatedPub_Title"] 		= []
		jsondict["relatedPub_URL"]			= []
		jsondict["relatedPub_CitationsList"]= []
		jsondict["relatedPub_PDFLink"]		= []
		jsondict["relatedPub_Excerpt"]		= []
		jsondict["relatedPub_Year"]			= []
		jsondict["relatedPub_Citations"]	= []
		
		for pubData in relatedPublDataList:
			if "Cluster ID" in pubData:
				jsondict["relatedPub_ClusterID"].append(pubData["Cluster ID"])
			else:
				jsondict["relatedPub_ClusterID"].append("")
				
			if "Title" in pubData:
				jsondict["relatedPub_Title"].append(pubData["Title"])
			else:
				jsondict["relatedPub_Title"].append("")
				
			if "URL" in pubData:
				jsondict["relatedPub_URL"].append(pubData["URL"])
			else:
				jsondict["relatedPub_URL"].append("")
				
			if "Citations list" in pubData:
				jsondict["relatedPub_CitationsList"].append(pubData["Citations list"])
			else:
				jsondict["relatedPub_CitationsList"].append("")
				
			if "PDF link" in pubData:
				jsondict["relatedPub_PDFLink"].append(pubData["PDF link"])
			else:
				jsondict["relatedPub_PDFLink"].append("")
				
			if "Excerpt" in pubData:
				jsondict["relatedPub_Excerpt"].append(pubData["Excerpt"])
			else:
				jsondict["relatedPub_Excerpt"].append("")
				
			if "Year" in pubData:
				jsondict["relatedPub_Year"].append(pubData["Year"])
			else:
				jsondict["relatedPub_Year"].append("")
				
			if "Citations" in pubData:
				jsondict["relatedPub_Citations"].append(pubData["Citations"])
			else:
				jsondict["relatedPub_Citations"].append("")

				
			
	#elif 'grobid__header_Authors' in jsondict.keys():
		#authors = [];
		#for author_info in jsondict['grobid__header_Authors']:
			#for author in author_info.split("1"):
				#authors.append(author.strip());
		##if blocked():
		##	print "we are blocked, cannot proceed"
		##	exit(0);
				
		#jsondict["relatedPub"] = getPublications(authors)
		#print "Using Authors Total No of related publications found : ",
		#print len(jsondict["relatedPub"])	
	else:
		#print "grobid_Authors or grobid__header_Title TEI info not_found...Skipping"
		print "grobid__header_Title TEI info not_found...Skipping"
		
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
