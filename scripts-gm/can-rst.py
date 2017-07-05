#!/usr/bin/env python3
# Pandoc filter using Panflute.
#
# Converts Canonical GitHub Markdown elements not handled by default in
# Pandoc's rst conversion.
#
# To use: 
#   install pandoc: sudo apt install pandoc
#   install panflute: pip install panflute
#
# Use this script with Pandoc's the filter argument: 
#  pandoc --from markdown_github --to rst --output file.rst input_file.md --filter can-rst.py

from panflute import CodeBlock, Str
import panflute as pf

# Search for metadata (a paragraph starting with Title:)
def is_metadata(elem):
    if not type(elem.content[0]) == pf.Str:
        return False
    elif not elem.content[0].text == 'Title:':
        return False
    elif type(elem.content[1]) != pf.Space:
        return False
    else:
        return True

def filterDoc(elem, doc):

    # remove Title and TODO from metadata, if they exist
    if isinstance(elem, pf.Para) and is_metadata(elem):
        return []

    # replace links to md files with links to their html equivalent
    elif isinstance(elem, pf.Link) and elem.url.endswith('.md'):
        elem.url = elem.url[:-3] + '.html'

    # replace no-highlight with bash
    elif type(elem) == CodeBlock and 'no-highlight' in elem.classes:
        elem.classes = ['bash']

    return elem

if __name__ == '__main__':
    pf.run_filter(filterDoc)
