#!/usr/bin/env bash
# Script to make the docs for swmfpy.
# Requires pydoc-markdown
# run `pip install pydoc-markdown --user`
# then run this script in the project root directory

pydoc-markdown -v -I. --render-toc -m swmfpy -m swmfpy.web -m swmfpy.io -m swmfpy.paramin -m swmfpy.tools | sed 's/\\043/#/g' - > DOCUMENTATION.markdown

