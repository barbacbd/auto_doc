import pytest
from autodoc_ext.templates import generate_sphinx, generate_rst, generate_modules_rst, generate_docs_dir
from os import remove, makedirs
from os.path import exists, isfile, join, dirname, abspath
from shutil import rmtree
from autodoc_ext.tree import Node


def test_template_generation():
    '''Generate files from the base config parametes'''
    generated_files = generate_sphinx()

    for filename in generated_files:
        remove(filename)

    assert len(generated_files) > 0


def test_generate_modules():
    '''Generate the modules.rst'''
    tempdir = "./test"
    makedirs(tempdir)

    generate_modules_rst("TESTPACKAGE", tempdir)
    assert exists(join(tempdir, "modules.rst"))
    assert isfile(join(tempdir, "modules.rst"))

    rmtree(tempdir)


def test_generate_rst():
    '''Generate the rst files for a dir'''
    tree = Node("TEST")
    artifacts = generate_rst(
        tree, dirname(abspath(__file__)))
    # there are files in this directory
    assert len(artifacts) > 0
    
    for x in ("docs", "TEST.rst", "modules.rst"):
        if exists(x):
            if isfile(x):
                remove(x)
            else:
                rmtree(x)
    
    
def test_generate_docs_dir():
    '''Generate the docs directory with two files'''
    tempdir = "./testdocs"

    output = generate_docs_dir(".", "testdocs")
    assert exists(join(tempdir, ".nojekyll"))
    assert isfile(join(tempdir, ".nojekyll"))
    assert exists(join(tempdir, "index.html"))
    assert isfile(join(tempdir, "index.html"))
    assert len(output) > 0

    rmtree(tempdir)    