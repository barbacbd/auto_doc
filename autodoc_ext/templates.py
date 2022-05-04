from jinja2 import Environment, FileSystemLoader, Template
from os.path import abspath, dirname, isfile, join
from os import listdir
from datetime import datetime
from logging import getLogger
from .args import check_args


log = getLogger()


def generate(*args, **kwargs):
    """
    Find all .j2 extension files in this directory. Fill the template files with the parameters
    that were passed in to this function.
    
    Args: 
      PROJECT                 (str): Name of the project that the documents are generated for.
      COPYRIGHT               (int): Year of the copyright for the `PROJECT`.
      AUTHOR                  (str): Author(s) of the `PROJECT` as a single string.
      VERSION                 (str): Version of the `PROJECT`.
      EXTENSIONS        (list[str]): Extension packages that can be combined with sphinx. Ex: rinoh.
      TEMPLATES         (list[str]): Path(s) containing templates.
      EXCLUSIONS   (list[str/path]): Path(s) and patterns of files to exclude from documentation.
      THEME                   (str): The theme to use for HTML and HTML Help pages.
      STATIC_PATHS (list[str/path]): Path(s) that contain custom static files.
      SOURCE_DIR         (str/path): Directory where the source of the software package is located.
      BUILD_DIR          (str/path): Directory where the sphinx build will occur.

    Artifacts:
      The following artifacts will be placed into the `SOURCE_DIR`

      Makefile: see `Makefile.j2`
      make.bat: see `make.bat.j2`
      conf.py:  see `conf.py.j2`


    Returns:
      None: See `Artifacts`
    """

    args = check_args(kwargs)
    mypath = join(dirname(abspath(__file__)))
    j2files = {join(mypath, f): f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".j2")}
    source = args["SOURCE_DIR"]
    
    for full_file, j2file in j2files.items():

        log.debug("Reading template {}".format(full_file))
        with open(full_file, "r") as jf:
            template = Template(jf.read())
            log.debug("Rendering template {}".format(full_file))
            output = template.render(**args)

        # write the files to the source directory where project code should reside
        log.debug("Writing data to {}".format(join(source, j2file.replace(".j2", ""))))
        with open("{}/{}".format(join(source, j2file.replace(".j2", ""))), "w+") as ic:
            ic.write(output)
