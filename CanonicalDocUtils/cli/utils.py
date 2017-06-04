#!/usr/bin/python3

import tempfile
import sh
import shutil
import os

from io import StringIO



def sshify(url):
  if url[:6] == 'ssh://':
    return(url)
  elif url[:10] == 'git@github':
    return('ssh://'+url)
  elif url[:1] == '/':
    return("ssh://git@github.com"+url)
  else:
    return("ssh://git@github.com/"+url)


def sync(fork_url, upstream_url, branch_name, quiet=True):
  buffer=StringIO()
  cwd=os.getcwd()
  temp=tempfile.mkdtemp()
  # fetch the fork
  if not quiet: print("cloning fork from {}".format(fork_url))
  git = sh.git.bake(_cwd=temp)
  git.clone(fork_url)

  # move it
  new_dir=os.path.join(cwd,branch_name)
  tmp_dir=os.path.join(temp,[ name for name in os.listdir(temp) if os.path.isdir(os.path.join(temp, name)) ][0])
  shutil.move(tmp_dir,new_dir)
  if not quiet: print("created directory for {}".format(branch_name))

  # sync with upstream
  git = sh.git.bake(_cwd=new_dir)
  git.remote('add','upstream', upstream_url)
  if not quiet: print("fetching upstream from {}".format(upstream_url))
  git.fetch('upstream','master')
  if not quiet: print("merging upstream/master")
  git.merge('upstream/master',_out=buffer)
  if not quiet: 
    print(buffer.getvalue())
    print("Now pushing back to fork origin")
  git.push('origin','master')

