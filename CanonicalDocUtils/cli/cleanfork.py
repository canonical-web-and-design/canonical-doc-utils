#!/usr/bin/python3

import sys
import argparse
import os

from .utils import sshify
from .utils import sync
    
def main():


  parser = argparse.ArgumentParser(description='Makes a clean working directory, adds upstream and syncs fork with upstream')
  parser.add_argument('fork_url',  nargs=1, help='github fork to use  (e.g. git@github.com/evilnick/docs or just /evilnick/docs)')
  parser.add_argument('upstream_url', nargs=1,help='github upstream to use')
  parser.add_argument('-q', action='store_true', help='make quiet')
  parser.add_argument('branch', nargs='?', default="new-branch", help='Name for new branch')
  args = parser.parse_args()
  args.fork_url = sshify(args.fork_url[0])
  args.upstream_url=sshify(args.upstream_url[0])
  if os.path.exists(args.branch):
     print("A directory with that name already exists - exiting")
     sys.exit(1)
  sync(args.fork_url, args.upstream_url,args.branch,False)

if __name__ == '__main__':
  main()

