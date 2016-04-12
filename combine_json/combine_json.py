from utility import get_all_files_in_directory
import json
import os
import datetime
import sys
# from sets import Set

__author__ = 'Frank, Ravi'


class MeasurementStorage:
    def __init__(self, directory):
        self.measurement_list = []
        self.next = 0
        self.get_measurement_objects_from(directory)

    def get_measurement_objects_from(self, directory):
        files = get_all_files_in_directory(directory)

        for entry in files:
            with open(entry) as input_file:
                self.measurement_list.extend(json.load(input_file))

    def has_next_measurement_object(self):
        if self.next < len(self.measurement_list):
            return True
        else:
            return False

    def get_next_measurement_object(self):
        if not self.has_next_measurement_object():
            return None
        dictionary_object = self.measurement_list[self.next]
        self.next += 1
        filename = dictionary_object.keys()[0]
        measurement_metadata = {'measurement': dictionary_object[filename]}
        return filename, measurement_metadata


class SweetStorage:
    def __init__(self, json_input):
        self.sweet_list = []
        self.next = 0
        self.get_sweet_objects_from(json_input)

    def get_sweet_objects_from(self, json_input):
        with open(json_input) as input_file:
            json_data = json.load(input_file)
            for key in json_data.keys():
                self.sweet_list.append({key: json_data[key]})

    def has_next_sweet_object(self):
        if self.next < len(self.sweet_list):
            return True
        else:
            return False

    def get_next_sweet_object(self):
        if not self.has_next_sweet_object():
            return None
        sweet_object = self.sweet_list[self.next]
        self.next += 1
        filename = sweet_object.keys()[0]
        sweet_metadata = {'sweet': sweet_object[filename].keys()}
        return filename, sweet_metadata


class GeoTopicStorage:
    def __init__(self, directory):
        self.geo_topic_list = []
        self.next = 0
        self.get_geo_topic_objects_from(directory)

    def get_geo_topic_from_single_json(self, directory):
        files = get_all_files_in_directory(directory)
        for entry in files:
            with open(entry) as input_file:
                filename = os.path.basename(input_file.name).split('.')[0]
                metadata = json.load(input_file)
                self.geo_topic_list.append({filename: metadata})

    def get_geo_topic_objects_from(self, directory):
        files = get_all_files_in_directory(directory)
        #print len(files)
        for entry in files:
            with open(entry) as input_file:
                #print(input_file.read())
                self.geo_topic_list.extend(json.load(input_file))

    def has_next_geo_topic_object(self):
        if self.next < len(self.geo_topic_list):
            return True
        else:
            return False

    def get_next_geo_topic_object(self):
        if not self.has_next_geo_topic_object():
            return None
        geo_topic_object = self.geo_topic_list[self.next]
        self.next += 1
        filename = geo_topic_object.keys()[0]
        geo_topic_metadata = geo_topic_object[filename]
        return filename, geo_topic_metadata

def test():
        
    doi = sys.argv[2]
    doiDict = {}
    with open(doi, "r") as f:
        for line in f:
            key = line.split('/')[-1]
            doiDict[key.rstrip('\r\n')] = line.rstrip('\r\n')
    #with open("doiDict.json", 'w') as json_file:
    #    json.dump(doiDict, json_file, indent = 4)
		
    time1 = datetime.datetime.now()
    
    measurement_storage = MeasurementStorage('/media/ravirajukrishna/My Passport/yao_files/measurement/')
    sweet_storage 		= SweetStorage('/media/ravirajukrishna/My Passport/yao_files/sweet/filename-sweet.json')
    
    geo_topic_storage = GeoTopicStorage('/media/ravirajukrishna/My Passport/yao_geoData_Large/')    
    geo_topic_storage.get_geo_topic_from_single_json('/media/ravirajukrishna/My Passport/yao_geoData/')
    
   
    total_dictionary = dict()
		
    while measurement_storage.has_next_measurement_object():
        filename, measurement_metadata = measurement_storage.get_next_measurement_object()
        if filename not in total_dictionary:
            if filename in doiDict:
				total_dictionary[filename] = {"doi" : doiDict[filename]}
            else:
				total_dictionary[filename] = {"doi" : filename}			
        total_dictionary[filename].update(measurement_metadata)
    print "parsed measurement_storage"
    
    while sweet_storage.has_next_sweet_object():
        filename, sweet_metadata = sweet_storage.get_next_sweet_object()
        if filename not in total_dictionary:
            if filename in doiDict:
				total_dictionary[filename] = {"doi" : doiDict[filename]}
            else:
				total_dictionary[filename] = {"doi" : filename}	
        total_dictionary[filename].update(sweet_metadata)
    print "parsed sweet_storage"
        
    while geo_topic_storage.has_next_geo_topic_object():
        filename, geo_topic_metadata = geo_topic_storage.get_next_geo_topic_object()
        if filename not in total_dictionary:
            if filename in doiDict:
				total_dictionary[filename] = {"doi" : doiDict[filename]}
            else:
				total_dictionary[filename] = {"doi" : filename}	
        total_dictionary[filename].update(geo_topic_metadata)
    print "parsed geo_topic_storage"

    input_dir = sys.argv[1]
    input_files = get_all_files_in_directory(input_dir)
    input_files_set = set(input_files)
    for ip_file in input_files_set:
        #print ip_file
        key = ip_file.split('/')[-1]
        filename_part = key.rstrip(".json")
        #print filename_part
        with open(ip_file) as json_file:
            jsondict = json.load(json_file)
            #print json.dumps(jsondict, indent=4)
            if filename_part not in total_dictionary:
                total_dictionary[filename_part] = {}
            total_dictionary[filename_part].update(jsondict)
    print "parsed grobid_scholar"    
    
    #final write to each json file
    i=1
    existing_files_set = set(total_dictionary.keys())	
    for key in existing_files_set:
        filename = "/media/ravirajukrishna/My Passport/result_json/" + key + ".json"
        i = i+1
        print i, 
        print ":",
        print filename
        with open(filename,'w') as json_file:
            json.dump(total_dictionary[key], json_file, indent = 4)



    time2 = datetime.datetime.now()
    print(time2 - time1)


    return


def main():
    time1 = datetime.datetime.now()
	
    measurement_storage = MeasurementStorage('/home/ravirajukrishna/yao_files/measurement1/')
    print(measurement_storage.get_next_measurement_object())
    print(measurement_storage.get_next_measurement_object())
	
    sweet_storage 		= SweetStorage('/home/ravirajukrishna/yao_files/sweet1/filename-sweet.json')
    print(sweet_storage.get_next_sweet_object())
    print(sweet_storage.get_next_sweet_object())
    
    geo_topic_storage = GeoTopicStorage('/media/ravirajukrishna/My Passport/yao_geoData_Large1/from/')
    geo_topic_storage.get_geo_topic_from_single_json('/media/ravirajukrishna/My Passport/yao_geoData1/')
    print len(geo_topic_storage.geo_topic_list)
    print(geo_topic_storage.get_next_geo_topic_object())
    print(geo_topic_storage.get_next_geo_topic_object())
    

    time2 = datetime.datetime.now()
    print(time2 - time1)
    return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage : python combine_json.py <path_to_scholar_doi_grobid_json_files> <path_to_doi.txt>" 
        exit(0)
    #main()
    test()
