#!/usr/bin/python3

import requests
import getpass
import sys
import argparse
import time
import datetime
from CanonicalDocUtils import __version__

def post_new(host,title,category,content,user,key,created=datetime.date.fromtimestamp(time.time()).isoformat()):

    # THIS IS WHAT API EXPECTS
    #
    # title	- {string}  required if creating a new topic or new private message
    # topic_id -	{int} required if creating a new post (OMIT for a new topic)
    # raw - {string} content of post Required
    # category - {integer} optional if creating a new topic, ignored if creating a new post
    # target_usernames {string} OMIT
    # archetype "private_message"	OMIT
    # created_at - {string} e.g. "2017-01-31"

    result = False
    payload = {
       'title': title,
       'category': category,
       'raw': content,
       'created_at': created,
       'api_key': key,
       'api_username:': user
       }
    url = host+'/posts.json'
    r = requests.post(url, params=payload)
    return(r)



def main():

    parser = argparse.ArgumentParser(description='Post Markdown or other text to discourse '+__version__)

    parser.add_argument("-s", "--server",
                        help='URL of discourse instance')
    parser.add_argument("-u","--user",
                        help="Username ")
    parser.add_argument("-k", "--key",
                        help="api key for this discourse")
    parser.add_argument("-c", "--category",
                        help="The category to make this post in")
    parser.add_argument("-t", "--title",
                        help="the title of the topic")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-b", "--body",
                        help="A string containing the body text of the post")
    group.add_argument("-f","--file",
                        help="A file containing the body of the post")
     
    args = parser.parse_args()

    # get user/password if not supplied   
    if not args.user:
      args.user = input("Discourse username: ")
    if not args.key:
      args.key = getpass.getpass("You must supply the API key: ")
    if args.file:
      with open(args.file, 'r') as infile:
        args.body=infile.read()
    print(args.server,args.title,args.category,args.body,args.user,args.key)
    result= post_new(args.server,args.title,args.category,args.body,args.user,args.key)
    print(result.text)
    
    
if __name__ == '__main__':
    main()