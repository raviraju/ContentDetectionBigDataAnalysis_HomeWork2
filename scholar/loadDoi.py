#! /usr/bin/env python
import sys
import os
import json

def main():
	if len(sys.argv) != 2:
		print "usage : python loadDoi.py <path_to_doi_file>"
		return 0
	doi = sys.argv[1]
	doiDict = {}
	with open(doi, "r") as f:
		for line in f:
			key = line.split('/')[-1]
			doiDict[key.rstrip('\n')] = line.rstrip('\n')
	with open("doiDict.json", 'w') as json_file:
		json.dump(doiDict, json_file, indent = 4)
	
if __name__ == "__main__":
    sys.exit(main())
