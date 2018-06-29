#!/usr/bin/python3

import sys
import argparse
import os
import yaml
import re
import requests
import time
import textwrap
import six
from CanonicalDocUtils import __version__
from CanonicalDocUtils import md2json

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

def quote_sub(match):
    text = re.sub('\[/?quote\]','',match.group()).strip()
    char_info= 'ⓘ'
    char_warning = '⚠ '
    # work out what type of note it is
    if text[0] == char_info:
        text = '!!! Note:\n'+ textwrap.fill(text[1:].strip(), width = 75,initial_indent = ' ' *4, subsequent_indent=' '*4)
    elif text[0] == char_warning:
        text = '!!! Warning:\n'+ textwrap.fill(text[1:].strip(), width = 75,initial_indent = ' ' *4, subsequent_indent=' '*4) 
    else:
        # default case where content is unknown is to omit it
        text = ''
    return(text)
                      
def fetch_and_save(link_list, prefix, out_dir,args):
    for l in link_list:
        url = get_raw_url(prefix+l['source'])
        if args.verbose:
            print('fetching \u001b[36m{} \u001b[0m'.format(url))
        try:
            content = requests.get(url)
        except:
            print("Error fetching url:",url)
            exit(1)
        if (content.status_code != 200):
            print("Error fetching url:",url)
            exit(1)
        #process content
        text = content.text
        #### find and replace relative links
        #regex = re.compile("\[(.*?)\]\((.*?)\)", re.MULTILINE)
        # for the moment, just replace ones we know about:
        for i in link_list: 
            text = re.sub(i['source'], i['location'], text, flags=re.MULTILINE)
            
        #### do something with images if required
        #### Fix quote stuff and convert to admonitions
        text = re.sub(r"\[quote\](.*?)\[/quote\]",quote_sub, text, flags=re.DOTALL)
        
        # append timestamp and link to source
        footer_time =  time.strftime("%Y-%m-%d at %H:%M:%S",time.gmtime())
        footer = "<br><hr><br><div class='footer'>For questions and comments see <a href='"+prefix+l['source']+"'>the forum topic</a>."
        footer += "<div class='footer'> Page generated on "+footer_time+ " UTC.</div>"
        text += footer
        # output file
        out_filename = os.path.join(out_dir,l['location'])
        if args.verbose:
            print('Writing markdown file \u001b[34m {} \u001b[0m'.format(out_filename))
        with open(out_filename,'w') as o:
            o.write(text)
            o.close()
      
      
def discourse_get(args):
    out_dir = args.output_dir
    if not out_dir:
        out_dir='.'
    # fetch url
    raw_url = get_raw_url(args.source)
    prefix = raw_url.split('/')
    prefix = prefix[0]+'//'+prefix[2]
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
    gen_list = nested_fetch(metadata)
    link_list=[]
    for l in gen_list:
        link_list.append(l)  
    fetch_and_save(link_list, prefix, out_dir,args)
    # fetch, change and write files


def main():
  d = "discourse-get "+__version__+"""

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
  parser.add_argument("-v", "--verbose", dest='verbose', action='store_true',
                      help = "Verbose output") 
  args = parser.parse_args()
  result = discourse_get(args)
  

if __name__ == '__main__':
  main()
