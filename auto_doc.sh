#!/bin/bash
#######################################################################
# Bash script to automate the process of running sphinx on a project
# including all of the installation and setup required for new themes
# and extensions.
#######################################################################

COLOR_OFF='\033[0m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'

function WARN() {
    echo -e "${YELLOW}[${FUNCNAME[0]}]: ${1}${COLOR_OFF}"
}
function DEBUG() {
    echo -e "${GREEN}[${FUNCNAME[0]}]: ${1}${COLOR_OFF}"
}
function INFO() {
    echo -e "${BLUE}[${FUNCNAME[0]}]: ${1}${COLOR_OFF}"
}

read -p $'\e[33mProject Name\e[0m: ' PROJECT
read -p $'\e[33mAuthor(s)\e[0m: ' AUTHOR
read -p $'\e[33mVersion\e[0m: ' VERSION
read -p $'\e[33mCopyright year\e[0m: ' COPYRIGHT

pyv=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
INFO "python $pyv"

# create the virtual environment if it doesn't exist
[ -d auto_doc_venv ] && created=0 ||  created=1
if [ ! -d auto_doc_venv ]; then
    DEBUG "Creating venv: auto_doc_venv."
    python3 -m venv auto_doc_venv;
else
    # warning that new packages will be installed and that it wont be deleted 
    WARN "New packages will be installed to the venv."
    WARN "auto_doc_venv will NOT be cleaned up upon completion."
fi

# activate the virtual environment
INFO "Activating auto_doc_venv"
source auto_doc_venv/bin/activate;

# attempt to install all of the required python packages
INFO "Installing new packages ..."
pip install pip --upgrade;
pip install sphinx;

# install the current package.
pip install . --upgrade;

if [ -d docs ]; then
    WARN "Removing previous instance of docs ..."
    rm -rf docs
fi

# create the directory and push it on to the stack
INFO "Creating directory docs, and pushing to stack."
mkdir docs;
pushd docs;

INFO "Creating directories build and source."
mkdir build;
mkdir source;

INFO "Creating Makefile ..."
# generate the make file (not using a batch file for now)
cat <<EOF >Makefile
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= 
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@\$(SPHINXBUILD) -M help "\$(SOURCEDIR)" "\$(BUILDDIR)" \$(SPHINXOPTS) \$(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  \$(O) is meant as a shortcut for \$(SPHINXOPTS).
%: Makefile
	@\$(SPHINXBUILD) -M \$@ "\$(SOURCEDIR)" "\$(BUILDDIR)" \$(SPHINXOPTS) \$(O)

EOF

INFO "Pushing source to the stack."
# push the source directory on to the stack
pushd source;

INFO "Creating index.rst ..."
cat <<EOF >index.rst
.. nautical documentation master file, created by
   sphinx-quickstart on Sun May 29 13:39:51 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root \`toctree\` directive.

Welcome to nautical's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
EOF


INFO "Creating conf.py ..."
DEBUG "Filling conf.py with user specified data ..."
# generate the python configuration file
cat <<EOF >conf.py
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = '$PROJECT'
copyright = '$COPYRIGHT, $AUTHOR'
author = '$AUTHOR'
release = '$VERSION'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.githubpages',
    'sphinx.ext.ifconfig',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',]

# Set values for Napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['venv', '__pycache__']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
EOF

INFO "Popping source from the stack."
popd;

INFO "Running sphinx-apidoc ...";
echo $PROJECT
echo "sphinx-apidoc -f -o ../docs/source/ ../$PROJECT;"
sphinx-apidoc -f -o ../docs/source/ ../$PROJECT;

# generate all of the docs!
INFO "Running makefile ...";
make html;

# create the base index.html file
INFO "Creating a base index.html ...";
cat <<EOF > index.html
<meta http-equiv="refresh" content="0; url=./build/html/index.html" />
EOF

INFO "Moving the .nojekyll file ...";
mv build/html/.nojekyll .;

INFO "Popping docs from the stack."
popd;

DEBUG "Deactivating virtual environment ...";
deactivate;

# if the virtual environment was created by us, remove it
if [[ $created == 1 ]]; then
    INFO "Removing auto_doc_venv ...";
    rm -rf auto_doc_venv
fi
