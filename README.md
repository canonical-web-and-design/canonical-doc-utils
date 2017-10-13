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
  
