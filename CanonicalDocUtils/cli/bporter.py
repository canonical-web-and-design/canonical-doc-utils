#!/usr/bin/python3

import getpass
import sys
import argparse
import sh
import os
from github import Github
from github import GithubException

from .utils import sync
from .utils import sshify

# defaults

repo_dict = { 'juju':16817497,
             'maas':56876730,
             'conjure-up':85062558,
             'cloud-docs':83429066,
             'landscape':62312414,
             'doctest':93037144
           } 


def main():

    parser = argparse.ArgumentParser(description='Backporter for docs')
    parser.add_argument('repo', nargs='?', help='github repo to operate on')
    parser.add_argument("-u","--user",
                        help="Username for accessing GitHub")
    parser.add_argument("-p", "--password",
                        help="Token or password for user")
    parser.add_argument("--issuenumber",
                        help="The issue number you wish to backport")
    parser.add_argument("-b", "--branch",
                        help="the branch to backport this to")
    args = parser.parse_args()

    # get user/password if not supplied   
    if not args.user:
      args.user = input("Github username: ")
    if not args.password:
      args.password = getpass.getpass("Github password or personal access token: ")

    g=Github(args.user, args.password)
    
    # retrieve users name and email for git
    u=g.get_user()
    if u.email == '':
      print("Error: You must have set a public email address in GitHub")
      sys.exit(1)
    if not args.repo:
      print("You did not supply a repository, which docs are you backporting?")
      repo_list=list(repo_dict)
      repo_list.sort()
      for x in range(len(repo_list)):
        print("# {} - {} ".format(x,repo_list[x]))
      repo_select = input("Enter number or blank to quit: ")
      if repo_select=='':
        print("Aborted by user")
        sys.exit(0)
      args.repo = repo_list[int(repo_select)]
    #
    print("Retrieving info for {}".format(args.repo))
    args.repo=repo_dict[args.repo]
    try:
      docsrepo=g.get_repo(args.repo)
      pull_list=list(docsrepo.get_pulls('closed'))
    except GithubException as e:
      if e.status == 401:
        print("ERROR: credentials were not accepted by GitHub. Exiting...")
      else:
        print("ERROR: Failed to retrieve data from GitHub")
        print("  Github API Error code - {}".format(e.status))
        print("  Message - {} ".format(e.data['message']))
      sys.exit(1)
    except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
    upstream_url='ssh://'+docsrepo.ssh_url.replace(':','/')

    # select the merged PR
    print("Most recent PRs merged to master")
    for x in range(min(20,len(pull_list))):
      print("{} - #{} - {}".format(x,pull_list[x].number, pull_list[x].title))
    print("Enter list number, or #<number> to choose a specific pull request: ")
    issuenumber= input("Number: ")
    if issuenumber[:1] == '#' :
      issuenumber = int(issuenumber[1:])
    else:
      i = int(issuenumber)
      issuenumber=pull_list[i].number
    # get the actual PR handle

    pull=docsrepo.get_pull(issuenumber)
    commits=list(pull.get_commits())
    # display selected PR
    shalist=[]
    print("You have selected this fabulous PR:")
    print("{} - {} by {}({})\n\n".format(issuenumber,pull.title,pull.user.login,pull.user.name))
    print("It contains the following commits:")
    for x in range(len(commits)):
      fetched=commits[x]
      shalist.append(commits[x].sha)
      msg = fetched.raw_data['commit']['message'].replace('\n','/')
      print("sha({}) - {}".format(commits[x].sha,msg[:45]))

    # find fork url 
    fork_url=''
    forks = list(docsrepo.get_forks())

    for f in forks:
      if args.user == f.owner.login:
        fork_url = f.svn_url[18:]
        fork_handle = f
    if fork_url == '':
      print("You have no fork for this repository. Please create one and try again.")
      sys.exit(0)

    fork_url=sshify(fork_url)

    # select the branch
    targets_list=list(docsrepo.get_branches())
    print("Which branch to target?")
    for x in range(min(20,len(targets_list))):
      print("{} - branch #{}".format(x,targets_list[x].name))
    print("Enter branch number, or #<> to choose a specific branch: ")
    targetnumber= input("Number:")
    if targetnumber[:1] == '#' :
      targetnumber = targetnumber[1:]
    else:
      i = int(targetnumber)
      targetnumber=targets_list[i].name

    branchname='bp-'+str(issuenumber)+'to'+targetnumber
    target= str(targetnumber)
    sync(fork_url, upstream_url, branchname, False)
    cwd=os.getcwd()
    branch_dir=os.path.join(cwd,branchname)
    git=sh.git.bake(_cwd=branch_dir)

    # set git options (in case globals not available - e.g. in a snap)
    git.config('user.email', u.email)
    git.config('user.name', u.name)
    
    # Fetch branch and apply commits
    print("Fetching upstream target branch...")
    git.fetch('upstream', target)
    git.checkout('upstream/'+target)
    print("Applying commits...")
    for commit in shalist:
      git('cherry-pick', commit)
    git.checkout('-b',branchname)
    print("Pushing candidate branch to your fork")
    git.push('origin', branchname)

    # construct the pull request
    pr_title = "Backport #"+str(issuenumber)+" to "+target
    pr_head  = args.user+":"+branchname
    pr_base  = target
    pr_body  = "Autogenerated backport, merge with caution!\n"
    # raise a PR
    try:
      pr = docsrepo.create_pull(title=pr_title,head=pr_head,base=pr_base,body=pr_body)
    except:
      print("There was an error whilst trying to create the PR. Please check your branch")
      sys.exit(1)

    # spit out value of PR
    print("A pull request has been generated. You can find it at: {}".format(pr.html_url))
  
if __name__ == '__main__':
    main()
    
