#!/usr/bin/python3

import sys
import argparse
import os
import yaml
import re
import requests
import six
from md2json import md2json
#from collections import defaultdict

# build in some defaults?
snapc = 'https://forum.snapcraft.io/t/documentation-outline/3781'

def get_raw_url(url):
    r = url.split('/')
    r = r[0]+'//'+r[2]+'/raw/'+r[-1]
    return(r)
  
  
def nested_fetch(document):
    if isinstance(document, list):    
        for d in document:
            for result in nested_fetch(d):
                yield result    
    if isinstance(document, dict):
        for k, v in six.iteritems(document):
            if k == 'source' :
                yield {'source': v, 'location': document['location']}
            elif isinstance(v, dict):
                for result in nested_fetch(v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in nested_fetch(d):
                        yield result

                      
def fetch_and_save(link_list, prefix, out_dir,args):
    for l in link_list:
        url = get_raw_url(prefix+l['source'])
        if args.verbose:
          print('fetching',url)
        try:
          content = requests.get(url)
        except:
          print("Error fetching url:",url)
          exit(1)
        if (content.status_code != 200):
          print("Error fetching url:",url)
          exit(1)
        #process content
        #### find and replace relative links
        #### do something with images if required
        # output file
        out_filename = os.path.join(out_dir,l['location'])
        with open(out_filename,'w') as o:
            o.write(content.text)
            o.close()
        
      
      
      
def discourse_get(args):
    out_dir = args.output_dir
    if not out_dir:
        out_dir='.'
    # check url is valid
    # fetch url
    raw_url = get_raw_url(args.source)
    prefix = raw_url.split('/')
    prefix = prefix[0]+'//'+prefix[2]
    print(prefix)
    try:
        result = requests.get(raw_url)
    except:
        print("Error fetching url.")
        exit(1)
    if (result.status_code != 200):
        print("Error fetching url.")
        exit(1)
    metadata = md2json(result.text)
    # check not empty
    if not metadata:
        print("No valid content found")
        exit(1)
    # generate metadata.yaml
    metadata_yaml = yaml.dump(metadata, default_flow_style=False)
    with open(os.path.join(out_dir,'metadata.yaml'),'w') as o:
        o.write(metadata_yaml)
        o.close()
    # find all links and source
    link_list = nested_fetch(metadata)
    fetch_and_save(link_list, prefix, out_dir,args)
    # fetch, change and write files
    print(link_list)
    for l in link_list:
      print(l)
    






def main():
  d = """discourse-get

         Given a url pointing to a discourse topic, containing a list of
         links, discourse-get will:
          * Parse the mardkdown found at that location
          * Fetch the related documents and output them in markdown
            format
          * Generate a documentation-builder compatible yaml file 
      """

  parser = argparse.ArgumentParser(description=d)
  parser.add_argument("-s", "--source",
                     help = "A string containing the discourse url")
  parser.add_argument("-o", "--output_dir",
                      help = "The output directory for generated files") 
  parser.add_argument("-v", "--verbose", 
                      help = "The output directory for generated files") 
  args = parser.parse_args()
  result = discourse_get(args)
  

if __name__ == '__main__':
  main()
