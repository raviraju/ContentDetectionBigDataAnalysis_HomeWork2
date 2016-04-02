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

from tika import parser
from vector import Vector
import os, itertools, argparse, csv
from requests import ConnectionError
from time import sleep
import json 

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))
    try:
        filename_list = [filename for filename in filename_list if "metadata" in parser.from_file(filename)]
    except ConnectionError:
        sleep(1)
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in acceptTypes]
    else:
        print "Accepting all MIME Types....."

    return filename_list


def computeScores(inputDir, outCSV, acceptTypes):
    
    with open(outCSV, "wb") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate","y-coordinate","Similarity_score"])        

        files_tuple = itertools.combinations(filterFiles(inputDir, acceptTypes), 2)
        for file1, file2 in files_tuple:
            try:
                row_cosine_distance = [file1, file2]
                            
                file1_parsedData = parser.from_file(file1)
                file2_parsedData = parser.from_file(file2)
           
                v1 = Vector(file1, file1_parsedData["metadata"])
                v2 = Vector(file2, file2_parsedData["metadata"])
            

                row_cosine_distance.append(v1.cosTheta(v2))            

                a.writerow(row_cosine_distance)  
            except ConnectionError:
                sleep(1)
            except KeyError:
                continue

def computeScoresJson(inputDir, outCSV, acceptTypes, jsonKey):
    
    with open(outCSV, "wb") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate","y-coordinate","Similarity_score"])        

        files_tuple = itertools.combinations(filterFiles(inputDir, acceptTypes), 2)
        for file1, file2 in files_tuple:
            try:
                row_cosine_distance = [file1, file2]
                
                with open(file1) as json_file1 , open(file2) as json_file2:
                    print "######"
                    jsonDict1 = json.load(json_file1)
                    jsonDict2 = json.load(json_file2)
                    if ((jsonKey in jsonDict1) and (jsonKey in jsonDict2)):
                        v1 = Vector(file1, {jsonKey : jsonDict1[jsonKey] })
                        print v1.getFileName(),
                        print v1.getFeature()
                       
                        v2 = Vector(file2, {jsonKey : jsonDict2[jsonKey] })
                        print v2.getFileName(),
                        print v2.getFeature()
                        row_cosine_distance.append(v1.cosTheta(v2))
                        a.writerow(row_cosine_distance)  
            except ConnectionError:
                sleep(1)
            except KeyError:
                continue                


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Cosine similarity based on Metadata values')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Cosine similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    argParser.add_argument('--J', help='Optional: compute Cosine similarity only on passed json key metadata')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV and args.J:
        computeScoresJson(args.inputDir, args.outCSV, args.accept, args.J)
    elif args.inputDir and args.outCSV:
		computeScores(args.inputDir, args.outCSV, args.accept)
