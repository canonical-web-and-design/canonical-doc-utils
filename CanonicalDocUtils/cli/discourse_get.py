#!/usr/bin/python3

import sys
import argparse
import os
import yaml
import re
import requests
from md2json import md2json

snapc = 'https://forum.snapcraft.io/t/documentation-outline/3781'

def discourse_get(topic, out_dir):
    if not out_dir:
        out_dir='.'
    # check url is valid
    # fetch url
    p = topic.split('/')
    raw_url = p[0]+'//'+p[2]+'/raw/'+p[-1]
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
    print(metadata)
    metadata_yaml = yaml.dump(metadata, default_flow_style=False)
    with open(os.path.join(out_dir,'metadata.yaml'),'w') as o:
        o.write(metadata_yaml)
        o.close()
    
    
    # find all links
    # fetch, change and write files
    # generate metadata.yaml








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
  args = parser.parse_args()
  result = discourse_get(args.source, args.output_dir)
  

if __name__ == '__main__':
  main()
