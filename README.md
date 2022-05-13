# AUTO DOC Ext

[![Build](https://github.com/barbacbd/auto_doc/actions/workflows/python-app.yml/badge.svg)](https://github.com/barbacbd/auto_doc/actions/workflows/python-app.yml)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) 
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/barbacbd/auto_doc/pulse/commit-activity)
[![GitHub latest commit](https://img.shields.io/github/last-commit/barbacbd/auto_doc)](https://github.com/barbacbd/auto_doc/commit/)


The repository contains the application (`docu`), an extension for sphinx's autodoc (which is already an extension). The package `autodoc-ext`
will install this application `docu`. Documentation can be found [here](https://barbacbd.github.io/auto_doc/html/index.html).

# docu

The application consists of two execution paths:

- clean
- create

## Clean

The execution path will clean up all artifacts that were created during the `create` execution path.

### Usage

```
usage: docu clean [-h] [-s SOURCE_DIR] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE_DIR, --source_dir SOURCE_DIR
                        Installation directory for the artifacts. This will be
                        the site where project documentation is generated.
  -v, --verbose         Verbosity level for logging
```

The follow example will cleanup the artifacts located in `example_dir` if they exist.

```
docu clean -s example_dir -vvvvv
```


## Create

The execution path will create the documentation and the artifacts necessary to cleanup the
information in the future. 

### Usage

```
positional arguments:
  project               Name of the project that the application will document

optional arguments:
  -h, --help            show this help message and exit
  -a AUTHOR [AUTHOR ...], --author AUTHOR [AUTHOR ...]
                        Author(s) (space separated) that created the project
  -e VERSION, --version VERSION
                        Version for the project
  -c COPYRIGHT, --copyright COPYRIGHT
                        Year of the copyright for the project
  -t THEME, --theme THEME
                        Sphinx docmumentation theme, see https://www.sphinx-
                        doc.org/en/master/usage/theming.html for more
                        information.
  -d PROJECT_SOURCE, --source_dir PROJECT_SOURCE
                        Directory where the project files reside. These files
                        should include the ones for which documenation will be
                        generated.
  -s SOURCE_DIR, --install_dir SOURCE_DIR
                        Installation directory for the artifacts. This will be
                        the site where project documentation is generated.
  -b BUILD_DIR, --build_dir BUILD_DIR
                        Directory where the documentation will be built. The
                        value should be relative to SOURCE_DIR.
  --extensions EXTENSIONS [EXTENSIONS ...]
                        Add any Sphinx extension module names here, as
                        strings. These can be sphinx generated or custom
                        extensions.
  --templates TEMPLATES [TEMPLATES ...]
                        Paths that contain templates, these should be relative
                        to the SOURCE_DIR.
  --exclusions EXCLUSIONS [EXCLUSIONS ...]
                        List of patterns, relative to SOURCE_DIR, that match
                        files and directories to ignore when looking for
                        source files.
  --static STATIC_PATHS [STATIC_PATHS ...]
                        Add any paths that contain custom static files (such
                        as style sheets), relative to SOURCE_DIR.
  --hide_artifacts      When present, the artifacts file will be hidden in the
                        SOURCE_DIR.
```

## User Notes

- `AUTHOR` is a list of names. To add a single user with first and last name use `"firstname lastname"`. To add multiple users use `"firstname1 lastname1" "firstname2 lastname2" ...`.
- `extensions`, `templates`, `exclusions`, and `static_paths` are lists.
- Each `v` you add with `-v` increases the depth of the logs. Example `-vvvv`.


# FAQ

Q: I am receiving an error similar to

```
.../venv/lib/python3.6/site-packages/sphinx/ext/autosummary/templates/autosummary/base.rst:3: ERROR: Error in "currentmodule" directive:
maximum 1 argument(s) allowed, 3 supplied.
```

What do I do?

A: You can either delete the venv and try without a venv or simply add venv to the exclusions parameter.
