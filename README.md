[![Snap Status](https://build.snapcraft.io/badge/canonical-docs/canonical-doc-utils.svg)](https://build.snapcraft.io/user/canonical-docs/canonical-doc-utils)

# canonical-doc-utils
Tools used for working with Markdown/documentation-builder repositories. The individual tools and usage are detailed below

# Installing

The tools are published as a snap in the snap store. Currently, they require the '--classic' confinement option (until we work out how to read ssh keys from within a strict mode snap).

Try:

      sudo snap install canonical-doc-utils --classic
      


## Backport

This command is exposed as `canonical-doc-utils.backport` when installed from a snap, or as `docs-backport` if you installed the python module.

### Usage

     canonical-doc-utils.backport [-h] [-u USER] [-p PASSWORD] [--issuenumber ISSUENUMBER] [-b BRANCH] [repo]

**-h** returns the standard user help

**-u, --user** is your githb username

**-p, --password** is github password, or 'Personal Access Token' if you are using 2fa

**--issuenumber** is the number (e.g. #1801) assigned to the pull request you wish to backport

** -b, --branch ** is the target branch in the repo you want to backport to

**repo** is the repository name, e.g. 'juju' or 'maas'. 

If you omit any of these things, an interactive mode will ask you for the relevant details and give helpful lists of options.

The issue lister is particularly useful, as it gives details of all the commits in a PR, so you know you have the right one.

Once running, this utility will:

  * create a local copy of YOUR fork of theselected repo
  * update this by pulling from the upstream/master
  * create a new branch
  * apply the cherry-pick commits from the PR you selected
  * push this new branch to your fork (named something appropriate, like 'bp#1801to2.1'
  * generate a pull request against the apporpriate branch of the upstream docs
  
## ```discourse-put```

This is a simple wrapper function which will post a string or a file to a discourse site

### usage
usage: discourse-put.py [-h] [-s SERVER] [-u USER] [-k KEY] [-c CATEGORY]
                        [-t TITLE] (-b BODY | -f FILE)

Post Markdown or other text to discourse 1.2.19

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        URL of discourse instance
  -u USER, --user USER  Username
  -k KEY, --key KEY     api key for this discourse
  -c CATEGORY, --category CATEGORY
                        The category to make this post in
  -t TITLE, --title TITLE
                        the title of the topic
  -b BODY, --body BODY  A string containing the body text of the post
  -f FILE, --file FILE  A file containing the body of the post

Example:

```bash
canonical-doc-utils.discourse-put.py -s https://canonical-docs.trydiscourse.com -u 'evilnick' -k 'dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxb' -c 'Tests' -t 'Auto post of a file to discourse' -f ../test.md 
```   

