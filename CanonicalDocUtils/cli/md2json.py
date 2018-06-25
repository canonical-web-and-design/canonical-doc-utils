#!/usr/bin/python3

import sys
import argparse
import os
import yaml
import re


def strip_comments(text):
    """
    Remove any HTML comments (<!-- xxx -->) from the supplied text
    """
    regex = r"""^\s*<!--(.*?)-->"""
    comments = re.compile(regex,
                          re.IGNORECASE |
                          re.VERBOSE |
                          re.DOTALL |
                          re.MULTILINE)
    text = re.sub(comments, '', text)
    return(text)


def get_link(text):
    """
    Returns a dict containing { title: , source:, location:}
    for link found in supplied text, or nothing if no link
    """
    link = {}
    regex = r"\[(.+)\]\((.+)\)"
    match = re.search(regex, text)
    # should only be one link - maybe throw error if more?
    if match:
        link['title'] = match.groups()[0]
        link['source'] = match.groups()[1]
        link['location'] = match.groups()[1].split('/')[-2] + '.md'
        return(link)
    else:
        return(None)


def get_header_groups(text):
    """
    From the supplied text, returns a list of dicts containing
    the header and the text between it and the next valid header
    """
    headers = []
    # match level 2 or lower headers
    regex = r"(\#{2,6})(?:\n|\s+?(.*?)(?:\n|\s+?\#+\s*?$))"
    matches = re.finditer(regex, text, re.IGNORECASE | re.VERBOSE | re.DOTALL)
    
    for m in matches:
        headers.append({'start': m.start(), 'header': m.group().strip(), 'groups': m.groups()})

    # loop through headers and store text from beneath them
    for x, h in enumerate(headers[:-1]):
        body = text[h['start'] + len(h['header']):headers[x+1]['start']]
        h['text'] = body
    # last one reads to EOF
    if len(headers):
        headers[-1]['text'] = text[headers[-1]['start']+len(headers[-1]['header']):]
    return(headers)
  
  
def get_items(text):
    """
    Returns a list containing dicts of links found in a markdown list
    or None if no links found
    """
    items = []
    regex = r"^( {0,3})(\d{1,9}[.)]|[+\-*])\s{1,4}(.+)"
    matches = re.finditer(regex, text, re.MULTILINE)
    level=0
    if matches:
        for m in matches:
            indent = len(m.groups()[0])
            l = get_link(m.groups()[2])
            if l:
                # level assumes multiple-of-two indents
                l['level']= int(len(m.groups()[0])/2)
                items.append(l)
        #last item
        items = ttree2_to_json(items)
        
        # if there is only one, return a list anyhow
        if type(items) == dict:
          items = [items]
        return(items)
    else:
        return(None)

  
def ttree2_to_json(ttree, level=0):
    result = []
    for i in range(0,len(ttree)):
        cn = ttree[i]
        try:
            nn  = ttree[i+1]
        except:
            nn = {'level':-1}

        # Edge cases
        if cn['level']>level:
            continue
        if cn['level']<level:
            return result

        # Recursion
        if nn['level']==level:
            itemdict = { 'title': cn['title'],  'location': cn['location'],'source': cn['source'] }
            result.append(itemdict)
        elif nn['level']>level:
            rr = ttree2_to_json(ttree[i+1:], level=nn['level'])
            itemdict = { 'title': cn['title'],  'location': cn['location'],'source': cn['source'] }
            itemdict['children'] = rr
            result.append(itemdict)
        else:
            itemdict = { 'title': cn['title'],  'location': cn['location'],'source': cn['source'] }
            result.append(itemdict)
            return result
    if result:
        return result 
    return(None)  


def md2json(text):
  # strip comments
  content = strip_comments(text)
  heads = get_header_groups(content)
  for h in heads:
      # get links from lists in text
      i = get_items(h['text'])
      h['children']=i
      h['title'] = h['groups'][1]
      del h['start']
      del h['text']
      del h['groups']
  # print(yaml.dump(heads, default_flow_style=False))
  nav_object = {'navigation': heads}
  return(nav_object)


def main():
  d = """md2json

         Takes Mardown input as a string or a file and returns a
         json object with a structure detailing any of the headings
         and links found within.

         Links are formatted to point to a local markdown file of the same 
         name as the 'slug' of the original link. Additionally the 'source' 
         key points to the original (relative) url of the source, for further
         processing.
      """

  parser = argparse.ArgumentParser(description=d)
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("-s", "--string",
                     help="A string containing the markdown text")
  group.add_argument("-f", "--file",
                     help="A file containing the markdown text")
  args = parser.parse_args()
  if args.file:
      with open(args.file, 'r') as infile:
          args.string = infile.read()
  output = md2json(args.string)
  sys.stdout.write(str(output))

if __name__ == '__main__':
  main()
