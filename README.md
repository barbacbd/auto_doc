# AUTODOC

Author: Brent Barbachem  
Alias: barbacbd  
Date: May 18, 2019

## Description

A rst file generator for a python project.

## Dependencies 

1. Sphinx
2. rinohtype
3. sphinx-rtd-theme

## How to ?

1. Move to the project that you wish to document.

    `cd my_example_project`

2. Make a directory that the documents should go in.

    `mkdir docs`

3. Move to that new directory and run sphinx-quickstart.

    `cd docs`
    `sphinx-quickstart`

4. In the newly generated source directory, alter the conf.py file.

    4.1 Alter the extensions: 
    
        extensions = ['sphinx.ext.autodoc', 'rinoh.frontend.sphinx', 'sphinx_rtd_theme']

    4.2 Uncomment the following lines:
    
        import os
        import sys
        sys.path.insert(0, os.path.abspath('../..'))
        
        *Note: the path in the section above has also been changed to `../..`*
    
    4.3 Add the following line after the block in 4.2
    
        sys.setrecursionlimit(1500)
    
    4.4 Replace the `html_theme` with:
    
        html_theme = "sphinx_rtd_theme"

5. Move to the base directory for the project.

6. Run the autodoc program

    `autodoc example -d "__pycache__" "other_dirs_to_exclude" -f "__main__.py"` 
    
    This will run the autodoc program on the python package `example` inside of the
    `my_example_project` directory where the directories `__pycache__` and
    `other_dirs_to_exclude` as well as files `__main__.py` will be excluded from the
    search. As a default parameter, the rst files will be saved to a folder called rst_files.

7. Move all of the files from rst_files to `docs/source`

8. Move back to the `docs` directory

    `cd docs`

9. Make the html page.

    `make html`

10. Run the build with rinohtype

    `sphinx-build -b rinoh source _build/rinoh`

11. You can find the html page inside of `docs/build/html/index.html`

12. You can find a pdf inside of `example-docs/_build/rinoh/{project}.pdf`

*If your python > 3.7 the latex generator for rinoh will fail*