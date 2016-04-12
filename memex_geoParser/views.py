from django.shortcuts import render
import glob, os
import urllib2
import ast
import requests
from requests.auth import HTTPBasicAuth
from ConfigParser import SafeConfigParser
from compiler.ast import flatten
from os.path import isfile
import string

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.gzip import gzip_page
from .forms import UploadFileForm
from .models import Document

from solr import IndexUploadedFilesText, QueryText, IndexLocationName, QueryLocationName, IndexLatLon, QueryPoints, IndexFile, create_core, IndexStatus, IndexCrawledPoints, GenerateKhooshe, GetIndexSize 
from solr_admin import get_index_core, get_all_domain_details, get_idx_details, update_idx_details

from tika import parser
from tika.tika import ServerEndpoint
from tika.tika import callServer
import traceback

import thread
import time

flip = True

conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


APP_NAME = conf_parser.get('general', 'APP_NAME')
UPLOADED_FILES_PATH = conf_parser.get('general', 'UPLOADED_FILES_PATH')
STATIC = conf_parser.get('general', 'STATIC')
SUBDOMAIN = conf_parser.get('general', 'SUBDOMAIN')
TIKA_SERVER = conf_parser.get('general', 'TIKA_SERVER')

QUERY_RANGE = 500
KHOOSHE_GEN_FREQ = QUERY_RANGE * 30
            
headers = {"content-type" : "application/json"}
params = {"commit" : "true" }

accept_new_khooshe_request = True

def index(request):
    file_name = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Document(docfile=request.FILES['file'])
            instance.save()
            file_name = str(instance.docfile).replace("{0}/{1}/".format(APP_NAME, UPLOADED_FILES_PATH), "")
            return HttpResponse(status=200, content="{{ \"file_name\":\"{0}\" }}".format(file_name), content_type="application/json")
    else:
        form = UploadFileForm()
    return render_to_response('index.html', {'form': form, 'subdomian':SUBDOMAIN}, RequestContext(request))


def index_file(request, file_name):
    IndexFile("uploaded_files", file_name)
    return HttpResponse(status=200)


def list_of_uploaded_files(request):
    '''
    Return list of uploaded files.
    '''
    files_list = []
    file_dir = os.path.realpath(__file__).split("views.py")[0]
    for f in os.listdir("{0}{1}".format(file_dir, UPLOADED_FILES_PATH)):
        if not f.startswith('.'):
            files_list.append(f)
    return HttpResponse(status=200, content="{0}".format(files_list))

# TODO EDIT IT AS PER NEW SCHEMA
def list_of_domains(request):
    '''
    Returns list of Solr cores except "uploaded_files"
    '''
    domains = get_all_domain_details()
    return HttpResponse(status=200, content="[" + str(domains) + "]")

    
def parse_lat_lon(locations):
    print "in parse_lat_lon :",
    print locations
    points = {}
    optionalCount = 0
    for key in locations.keys():
        if key.startswith("Optional_NAME"):
            optionalCount = optionalCount + 1 
    if 'Geographic_NAME' in locations:
        print "locations[\"Geographic_NAME\"] : ",
        print locations["Geographic_NAME"]
        print "locations[\"Geographic_LATITUDE\"] : ",
        print locations["Geographic_LONGITUDE"]
        print "locations[\"Geographic_LONGITUDE\"] : ",
        print locations["Geographic_LATITUDE"]
        points[locations["Geographic_NAME"].replace(" ", "").decode("UTF-8",'ignore')] = [locations["Geographic_LATITUDE"].replace(" ", ""), locations["Geographic_LONGITUDE"].replace(" ", "")]
    else:
        print "No main location found"
    for x in range(1, optionalCount + 1):
        print "locations[\"Optional_NAME{0}\".format(x)] : ",
        print locations["Optional_NAME{0}".format(x)]
        print "locations[\"Optional_LATITUDE{0}\".format(x) : ",
        print locations["Optional_LATITUDE{0}".format(x)]
        print "locations[Optional_LONGITUDE{0}.format(x) : ",
        print locations["Optional_LONGITUDE{0}".format(x)]
        points[locations["Optional_NAME{0}".format(x)].replace(" ", "").decode("UTF-8",'ignore')] = [locations["Optional_LATITUDE{0}".format(x)].replace(" ", ""), locations["Optional_LONGITUDE{0}".format(x)].replace(" ", "")]
    print "points : ",
    print points
    return points


def extract_text(request, file_name):
    '''
        Using Tika to extract text from given file
        and return the text content.
    '''
    if "none" in IndexStatus("text", file_name):
        parsed = parser.from_file("{0}/{1}/{2}".format(APP_NAME, UPLOADED_FILES_PATH, file_name))
        status = IndexUploadedFilesText(file_name, parsed["content"])
        if status[0]:
            return HttpResponse(status=200, content="Text extracted.")
        else:
            return HttpResponse(status=400, content="Cannot extract text.")
    else:
        return HttpResponse(status=200, content="Loading...")



def find_location(request, file_name):
    '''
        Find location name from extracted text using Geograpy.
    '''
    if "none" in IndexStatus("locations", file_name):
        text_content = QueryText(file_name)
        if text_content:
            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json', 'Content-Type' : 'application/geotopic'}, False)
            points = parse_lat_lon(eval(parsed[1])[0])
            
            status = IndexLocationName(file_name, points)
            if status[0]:
                return HttpResponse(status=200, content="Location/s found and index to Solr.")
            else:
                return HttpResponse(status=400, content=status[1])
        else:
            return HttpResponse(status=400, content="Cannot find location.")
    else:
        return HttpResponse(status=200, content="Loading...")



def find_latlon(request, file_name):
    '''
    Find latitude and longitude from location name using GeoPy.
    '''
    if "none" in IndexStatus("points", file_name):
        location_names = QueryLocationName(file_name)
        if location_names:
            points = []
            location_names = ast.literal_eval(location_names)
            for key, values in location_names.iteritems():
                try:
                    points.append(
                        {'loc_name': "{0}".format(key),
                        'position':{
                            'x': "{0}".format(values[0]),
                            'y': "{0}".format(values[1])
                        }
                        }
                    )
                except:
                    pass
            status = IndexLatLon(file_name, points)
            if status[0]:
                return HttpResponse(status=200, content="Latitude and longitude found.")
            else:
                return HttpResponse(status=400, content="Cannot find latitude and longitude.")
        else:
            return HttpResponse(status=400, content="Cannot find latitude and longitude.")
    else:
        return HttpResponse(status=200, content="Loading...")

'''
Works only for file uploads
index geo tagging have different solr schema
TODO - Consider having a unified approach
'''
@gzip_page
def return_points(request, file_name, core_name):
    '''
        Returns geo point for give file
    '''
    results = {}
    points, total_docs, rows_processed = QueryPoints(file_name, core_name)
    results["points"] = points
    results["total_docs"] = total_docs
    results["rows_processed"] = rows_processed
    if total_docs or points:
        return HttpResponse(status=200, content="[{0}]".format(results))
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude(return_points).")

'''
Works only for index geo tagging 
file uploads have different solr schema
TODO - Consider having a unified approach
'''
def return_points_khooshe(request, indexed_path, domain_name):
    '''
        Returns geo point for give file using khooshe
    '''
    
    core_name = get_index_core(domain_name, indexed_path)
    results = {}
    
    results["rows_processed"] = GetIndexSize(core_name)
    results["total_docs"], results["points_count"] = get_idx_details(domain_name, indexed_path)
    
    exclude = set(string.punctuation)
    file_name = ''.join(ch for ch in core_name if ch not in exclude)
    results["khooshe_tile"] = "static/tiles/{0}".format(file_name)
    if results["rows_processed"]:
        return HttpResponse(status=200, content="[{0}]".format(results))
    else:
        return HttpResponse(status=400, content="Cannot find latitude and longitude(return_points_khooshe).")


def _gen_khooshe_update_admin_thread(core_name, domain_name, indexed_path, numFound):
    global accept_new_khooshe_request
    try:
        points_len = GenerateKhooshe(core_name)
        update_idx_details(domain_name, indexed_path, numFound, points_len)
    except Exception as e:
        print traceback.format_exc()
        print e
    accept_new_khooshe_request = True
    

def gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound):
    global accept_new_khooshe_request
    if(accept_new_khooshe_request) :
        accept_new_khooshe_request = False
        thread.start_new_thread(_gen_khooshe_update_admin_thread, (core_name, domain_name, indexed_path, numFound))
        return True
    else:
        print "Rejected Khooshe generation request.. Waiting for previous request to get completed"
        return False

def refresh_khooshe_tiles(request, domain_name, indexed_path):
    core_name = get_index_core(domain_name, indexed_path)
    numFound = GetIndexSize(core_name)
    is_in_queue = gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
    if(is_in_queue):
        return HttpResponse(status=200, content="[{'msg':'Queued Khooshe generation'}]")
    else:
        return HttpResponse(status=200, content="[{'msg':'Can't queue another Khooshe generation'}]")

def query_crawled_index(request, domain_name, indexed_path, username, passwd):
    '''
        To query crawled data that has been indexed into
        Solr or Elastichsearch and return location names
    '''
    if "solr" in indexed_path.lower():
        '''
        Query admin core to get core information for domain_name, indexed_path combination
        '''
        core_name = get_index_core(domain_name, indexed_path)
        print core_name
        if create_core(core_name):
            # 1 query solr QUERY_RANGE records at a time
            # 2     Run GeotopicParser on each doc one at a time
            # 3     keep appending results 
            # 4 Save it in local solr instance
            rows_processed = 0
            try:
                rows_processed = GetIndexSize(core_name)
            except:
                pass
            try:
                url = "{0}/select?q=*%3A*&wt=json&rows=1".format(indexed_path)
                r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                
                if r.status_code != 200:
                    return HttpResponse(status=r.status_code, content=r.reason)
                
                response = r.json()
                numFound = response['response']['numFound']
                print "Total number of records to be geotagged {0}".format(numFound)
                #gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                khooshe_gen_freq_l = rows_processed 
                for row in range(rows_processed, int(numFound), QUERY_RANGE):  # loop solr query
                    if row <= khooshe_gen_freq_l <= (row + QUERY_RANGE):
                        print "Generating khooshe tiles.."
                        gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                        if (khooshe_gen_freq_l >= KHOOSHE_GEN_FREQ):
                            khooshe_gen_freq_l += KHOOSHE_GEN_FREQ
                        else:
                            khooshe_gen_freq_l = (row + QUERY_RANGE) * 2
                    else:
                        print "Skip generating khooshe tiles.. row - {0}, next scheduled - {1} ".format(row,khooshe_gen_freq_l)

                    docs = {}
                    url = "{0}/select?q=*%3A*&start={1}&rows={2}&wt=json".format(indexed_path, row, QUERY_RANGE)
                    print "solr query - {0}".format(url)
                    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, passwd))
                    response = r.json()
                    text = response['response']['docs']
                    docCount = 0
                    for t in text:  # loop tika server starts
                        points = []
                        try:
                            docCount += 1
                            text_content = ''
                            try:
                                for v in t.values():
                                    if(hasattr(v, '__iter__')):
                                        a = u' '.join(unicode(e) for e in v)
                                    elif(isinstance(v, unicode)):
                                        a = v.encode('ascii', 'ignore')
                                    else:
                                        a = str(v)
                                    text_content += a.encode('ascii', 'ignore')
                            except Exception as e:
                                print traceback.format_exc()
                                text_content = str(t.values())
                            
                            # simplify text
                            text_content = ' '.join(text_content.split())
                            
                            parsed = callServer('put', TIKA_SERVER, '/rmeta', text_content, {'Accept': 'application/json', 'Content-Type' : 'application/geotopic'}, False)
                            location_names = parse_lat_lon(eval(parsed[1])[0])
        
                            for key, values in location_names.iteritems():
                                try:
                                    # # TODO - ADD META DATA
                                    points.append(
                                        {'loc_name': smart_str(key),
                                        'position':{
                                            'x': smart_str(values[0]),
                                            'y': smart_str(values[1])
                                        }
                                        }
                                    )
                                except Exception as e:
                                    print "Error while transforming points "
                                    print e
                                    pass
                            print "Found {0} coordinates..".format(len(points))  
                            # print docs
                        except Exception as e:
                            print traceback.format_exc()
                            pass
                        
                        docs[str(t['doi'])] = points
                        # loop tika server ends
                    status = IndexCrawledPoints(core_name, docs)
                    print status
                    # loop solr query ends
                gen_khooshe_update_admin(core_name, domain_name, indexed_path, numFound)
                return HttpResponse(status=200, content= ("Crawled data geo parsed successfully."))
            except Exception as e:
                print traceback.format_exc()
                print e
                return HttpResponse(status=500, content= ("Error while geo parsing crawled data."))

    else:
        return HttpResponse(status=500, content= ("Only solr indexes supported for now"))
    
