import json
import os
import sys

def get_all_files_in_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list

def process_link(link):
    #http://scholar.google.com/https://pdfs.semanticscholar.org/dff1/e0cb10d97eb35b5c9f7517546aa5a0fdcbcb.pdf
    index = link.find("http://scholar.google.com/")
    if index != -1:
        #print index
        link = link[len("http://scholar.google.com/"):]
    return link
    
def main():
    
    pdfDict = {}
    urlDict = {}
    i = 0
    total_no_of_pdf_docs = 0
    total_no_of_url_docs = 0
    input_dir = sys.argv[1]
    input_files = get_all_files_in_directory(input_dir)
    for ip_file in input_files:
        with open(ip_file) as json_file:
            i = i + 1
            print i,
            print " : ",            
            key = (ip_file.split('/')[-1]).rstrip(".json")
            print key
            jsonDict = json.load(json_file)
            if "grobid__header_Title" in jsonDict:
                title = jsonDict["grobid__header_Title"]
            else:
                title = ""
            
            if "doi" in jsonDict:
                doi = jsonDict["doi"]
            else:
                doi = ""
                
            if "relatedPub_PDFLink" in jsonDict:
                no_of_pdf_links = 0
                list_of_pdfs = []
                for link in jsonDict["relatedPub_PDFLink"]:
                    #print link
                    if len(link) > 0:
                        no_of_pdf_links = no_of_pdf_links + 1                        
                        link = process_link(link)
                        list_of_pdfs.append({"name" : link})
                #print "no_of_pdf_links : ",
                #print no_of_pdf_links
                
                if no_of_pdf_links not in pdfDict:
                    pdfDict[no_of_pdf_links] = {}
                value = {}
                value["children"] = list_of_pdfs
                value["doi"] = doi
                value["name"] = title
                if "docs" in pdfDict[no_of_pdf_links]:
                    pdfDict[no_of_pdf_links]["docs"][key] = value
                else:
                    pdfDict[no_of_pdf_links]["docs"] = { key : value }
                no_of_pdf_docs = len(pdfDict[no_of_pdf_links]["docs"].keys())
                pdfDict[no_of_pdf_links]["no_of_docs"] = no_of_pdf_docs
            
            if "relatedPub_URL" in jsonDict:
                no_of_urls = 0
                list_of_urls = []
                for link in jsonDict["relatedPub_URL"]:
                    #print link
                    if len(link) > 0:
                        no_of_urls = no_of_urls + 1
                        link = process_link(link)
                        list_of_urls.append({"name" : link})
                #print "no_of_urls : ",
                #print no_of_urls

                if no_of_urls not in urlDict:
                    urlDict[no_of_urls] = {}
                value = {}
                value["children"] = list_of_urls
                value["doi"] = doi
                value["name"] = title
                if "docs" in urlDict[no_of_urls]:
                    urlDict[no_of_urls]["docs"][key] = value
                else:
                    urlDict[no_of_urls]["docs"] = { key : value }
                #urlDict[no_of_urls]["no_of_docs"] = len(urlDict[no_of_urls]["docs"].keys())
                no_of_url_docs = len(urlDict[no_of_urls]["docs"].keys())
                urlDict[no_of_urls]["no_of_docs"] = no_of_url_docs
    
    master_child_list=[]
    for key in pdfDict.keys():
        total_no_of_pdf_docs = total_no_of_pdf_docs + pdfDict[key]["no_of_docs"]
        superDict = {}
        cluster_key = "cluster" + str(key)
        superDict.update({"name" : cluster_key})
        child_list = []
        for k in pdfDict[key]["docs"].keys():
            #print json.dumps({"key":k},indent=4)
            #print json.dumps(pdfDict[key]["docs"][k],indent=4)
            tempDict = {}
            tempDict.update({"key":k})
            tempDict.update(pdfDict[key]["docs"][k])
            #print json.dumps(tempDict,indent=4)
            child_list.append(tempDict)
        superDict.update({"children":child_list})        
        #print json.dumps(superDict,indent=4)
        master_child_list.append(superDict)    
    final_pdfDict = {"name":"clusters", "children" : master_child_list}
    #print json.dumps(final_pdfDict,indent=4)
    print "Total number of docs with related pdfs found : ",
    print total_no_of_pdf_docs        
    with open("pdfDict.json", 'w') as json_file:
        json.dump(final_pdfDict, json_file, indent = 4)
        
    master_child_list=[]
    for key in urlDict.keys():
        total_no_of_url_docs = total_no_of_pdf_docs + urlDict[key]["no_of_docs"]
        superDict = {}
        cluster_key = "cluster" + str(key)
        superDict.update({"name" : cluster_key})
        child_list = []
        for k in urlDict[key]["docs"].keys():
            #print json.dumps({"key":k},indent=4)
            #print json.dumps(urlDict[key]["docs"][k],indent=4)
            tempDict = {}
            tempDict.update({"key":k})
            tempDict.update(urlDict[key]["docs"][k])
            #print json.dumps(tempDict,indent=4)
            child_list.append(tempDict)
        superDict.update({"children":child_list})        
        #print json.dumps(superDict,indent=4)
        master_child_list.append(superDict)    
    final_urlDict = {"name":"clusters", "children" : master_child_list}
    #print json.dumps(final_urlDict,indent=4)
    print "Total number of docs with related pdfs found : ",
    print total_no_of_url_docs        
    with open("urlDict.json", 'w') as json_file:
        json.dump(final_urlDict, json_file, indent = 4)

    
    
                
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage : python extract_pdf_url.py <path_to_json_files>" 
        exit(0)
    main()
