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
    regex = r"""^<!--(.*?)-->"""
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
        headers.append({'start': m.start(), 'header': m.group(), 'groups': m.groups()})

    # loop through headers and store text from beneath them
    for x, h in enumerate(headers[:-1]):
        body = text[h['start'] + len(h['header']):headers[x+1]['start']]
        h['text'] = body
    # last one reads to EOF
    if len(headers):
        headers[-1]['text'] = text[headers[-1]['start']+len(headers[-1]['header']):]
    return(headers)


def dict_add(adict, key, val):
    """
    Insert a value in dict at key if one does not exist
    Otherwise, convert value to list and append
    """
    if key in adict:
        if type(adict[key]) != list:
            adict[key] = [adict[key]]
            adict[key].append(val)
    else:
        adict[key] = val

    
def ttree_to_json(ttree, level=0):
    result = {}
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
            dict_add(result, 'title', cn['title'])
            dict_add(result, 'location', cn['location'])
            dict_add(result, 'source', cn['source'])
        elif nn['level']>level:
            rr = ttree_to_json(ttree[i+1:], level=nn['level'])
            print("rr = ", rr)
            rr = unravel(rr)
            dict_add(result, 'children', rr)
        else:
            dict_add(result, 'source', cn['source'])
            dict_add(result, 'title', cn['title'])
            dict_add(result, 'location', cn['location'])
            result = unravel(result)
            return result
    return result     
  

def unravel(rr):
    """
    For the case where there are multiple title/links in the tree, 
    they are initially organised as e.g. 'title' : [a,b,c] 
    This function converts such a dict instead to a list of dicts with one value each
    """

    if type(rr) != dict:
      return(rr)
    if type(rr['title']) != list:
      return(rr)
    ret_list = []
    for i in range(len(rr['title'])):      
      newdict = { 'title':   rr['title'][i],
                 'location': rr['location'][i],
                 'source':   rr['source'][i] }
      ret_list.append(newdict)
    return(ret_list)  


def md2yaml(text):
  # strip comments
  content = strip_comments(text)
  print(content)
  heads = get_header_groups(content)
  print(heads)
  return("not done yet")


def main():
  d = """md2yaml

         Takes Mardown input as a string or a file and returns a
         documentation-builder compatible YAML string with a 
         structure detailing any of the headings and links found within

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
  output = md2yaml(args.string)
  sys.stdout.write(output)

if __name__ == '__main__':
  main()
