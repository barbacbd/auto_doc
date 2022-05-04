import pytest
from autodoc_ext.templates import generate
from os import remove


def test_template_generation():
    '''Generate files from the base config parametes'''
    generated_files = generate()

    for filename in generated_files:
        remove(filename)

    assert len(generated_files) > 0
