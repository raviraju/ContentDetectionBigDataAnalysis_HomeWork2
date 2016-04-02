#!/usr/bin/env python2.7
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

import tika
from tika import parser
from pprint import pprint
import os
import sys
import getopt
import json
import operator
from time import sleep
from requests import ConnectionError

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

_verbose = False
_keyMode = False
_helpMessage = '''

Usage: similarity [-v] [-f directory] [-c file1 file2]


Options:

-v, --verbose
	Work verbosely rather than silently.

-f, --directory [path to directory]
	read files from this directory recursively

-c, --file [file1 file2]
	compare similarity of given files

--accept [jpeg pdf etc...]
	Optional: compute similarity only on specified IANA MIME Type(s)

-h --help
	show help on the screen

-k --key [key_info]
	run algorithm on specified metadata key

-j, --json
	Use JSON input.	
'''

def verboseLog(message):
	if _verbose:
		print >>sys.stderr, message

class _Usage(Exception):
	''' an error for arguments '''

	def __init__(self, msg):
		self.msg = msg

def main(argv = None):
	if argv is None:
		argv = sys.argv

	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'hvf:c:a:k:j:', ['help', 'verbose', 'directory=', 'file=', 'accept=', 'key=', 'json=' ])
		except getopt.error, msg:
			raise _Usage(msg)

		if len(opts) ==0:
			raise _Usage(_helpMessage)

		dirFile = ""
		filenames = []
		filename_list = []
		allowed_mime_types = []
		directory_flag = 0
		meta_key = ""
		json_input = False

		for option, value in opts:
			if option in ('-h', '--help'):
				raise _Usage(_helpMessage)

			elif option in ('-c', '--file'):
				#extract file names from command line
				if '-c' in argv :
					index_of_file_option = argv.index('-c')
				else :
					index_of_file_option = argv.index('--file')
				filenames = argv[index_of_file_option+1 : ]

			elif option in ('-f', '--directory'):
				dirFile = value
				directory_flag = 1
				for root, dirnames, files in os.walk(dirFile):
					dirnames[:] = [d for d in dirnames if not d.startswith('.')]
					for filename in files:
						if not filename.startswith('.'):							
							filename_list.append(os.path.join(root, filename))

			elif option in ('--accept'):
				#extract accepted mime types from command line
				index_of_mime_type_option = argv.index('--accept')
				allowed_mime_types = argv[index_of_mime_type_option+1 : ]

			elif option in ('-v', '--verbose'):
				global _verbose
				_verbose = True
			
			elif option in ('-k', '--key'):
				meta_key = value
				global _keyMode
				_keyMode = True
			elif option in ('-j', '--json'):
				print "json mode"
				json_input = True

		#format filename
		if directory_flag == 0:			
			filenames = [x.strip() for x in filenames]
			filenames = [filenames[k].strip('\'\n') for k in range(len(filenames))]
			for filename in filenames :
				if not os.path.isfile(os.path.join(dirFile, filename)):
					continue
				filename = os.path.join(dirFile, filename) if dirFile else filename
				filename_list.append(filename)

		if len(filename_list) <2 :
			raise _Usage("you need to type in at least two valid files")

		#allow only files with specifed mime types
		if len(allowed_mime_types) != 0:
			filename_list = [filename for filename in filename_list if parser.from_file(filename) and str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in allowed_mime_types]
		else:
			print "Accepting all MIME Types....."

		union_feature_names = set()
		file_parsed_data = {}
		resemblance_scores = {}
		file_metadata={}
		
		if _keyMode:
			key = meta_key #"X-Parsed-By"
		
		for filename in filename_list:
			file_parsed = []
			# first compute the union of all features
			parsedData = parser.from_file(filename)
			filename_stripped = filename.replace(",", "")
			
			if json_input:
				#print filename
				with open(filename) as json_file:
					jsonDict = json.load(json_file)
					file_metadata[filename_stripped] = jsonDict
					if _keyMode:				
						if key in jsonDict:
							value = jsonDict[key]
							if isinstance(value, list):
								for val in jsonDict[key]:
									print val,
								print
								value = ", ".join([str(val) for val in jsonDict[key]])
							file_parsed.append(str(key.strip(' ').encode('utf-8') + ": " + value.strip(' ').encode('utf-8')))
					else:
						for key in jsonDict:								
							value = jsonDict[key]
							print key
							print value
							if isinstance(value, list):
								for val in jsonDict[key]:
									print val,
								print
								value = ", ".join([str(val) for val in jsonDict[key]])

							file_parsed.append(str(key.strip(' ').encode('utf-8') + ": " + value.strip(' ').encode('utf-8')))
					
					file_parsed_data[filename_stripped] = set(file_parsed)
					union_feature_names = union_feature_names | set(file_parsed_data[filename_stripped])
					print union_feature_names
					print len(union_feature_names)
					print
			else:
				try:
					file_metadata[filename_stripped] = parsedData["metadata"]

					#get key : value of metadata
					
					#for key in parsedData["metadata"]:
					if _keyMode:				
						if key in parsedData["metadata"]:
							value = parsedData["metadata"][key]
							if isinstance(value, list):
								value = ", ".join(parsedData["metadata"][key])

							file_parsed.append(str(key.strip(' ').encode('utf-8') + ": " + value.strip(' ').encode('utf-8')))
					else:#if key in parsedData["metadata"]:
						for key in parsedData["metadata"]:								
							value = parsedData["metadata"][key]
							if isinstance(value, list):
								value = ", ".join(parsedData["metadata"][key])

							file_parsed.append(str(key.strip(' ').encode('utf-8') + ": " + value.strip(' ').encode('utf-8')))

					file_parsed_data[filename_stripped] = set(file_parsed)
					union_feature_names = union_feature_names | set(file_parsed_data[filename_stripped])
					print union_feature_names
					print len(union_feature_names)
					print

				except ConnectionError:
					sleep(1)
				except KeyError:
					continue

		total_num_features = len(union_feature_names)
		
				

		# now compute the specific resemblance and containment scores
		for filename in file_parsed_data:
			overlap = {}
			overlap = file_parsed_data[filename] & set(union_feature_names)
			print "overlap"
			print overlap
			print "#######"
			resemblance_scores[filename] = float(len(overlap))/total_num_features

		sorted_resemblance_scores = sorted(resemblance_scores.items(), key=operator.itemgetter(1), reverse=True)

		'''print "Resemblance:\n"
		for tuple in sorted_resemblance_scores:
			print os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) +"," + tuple[0] + ","+ convertUnicode(file_metadata[tuple[0]])+'\n'''
		with open("similarity-scores.txt", "w") as f:
			f.write("Resemblance : \n")
			for tuple in sorted_resemblance_scores:
				if _keyMode:					
					if key in file_metadata[tuple[0]]:
						f.write(os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) +"," + tuple[0] + ","+ convertUnicode({key:file_metadata[tuple[0]][key]})+'\n')
				else:
					f.write(os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) +"," + tuple[0] + ","+ convertUnicode(file_metadata[tuple[0]])+'\n')
					

	except _Usage, err:
		print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
		return 2

def convertUnicode( fileDict ) :
	fileUTFDict = {}
	print fileDict
	for key in fileDict:
		if isinstance(key, unicode) :
			key = key.encode('utf-8').strip()
		value = fileDict.get(key)
		if isinstance(value, unicode) :
			value = value.encode('utf-8').strip()
		fileUTFDict[key] = value

	return str(fileUTFDict)

if __name__ == "__main__":
	sys.exit(main())






