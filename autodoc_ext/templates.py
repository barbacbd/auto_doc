from jinja2 import Template
from os.path import abspath, dirname, isfile, join
from os import listdir
from logging import getLogger
from .args import check_args


log = getLogger()


def generate(*args, **kwargs):
    """
    Find all .j2 extension files in this directory. Fill the template files
    with the parameters that were passed in to this function.
    Args:
      PROJECT                 (str): Name of the project that the documents
                                     are generated for.
      COPYRIGHT               (int): Year of the copyright for the `PROJECT`.
      AUTHOR                  (str): Author(s) of the `PROJECT` as a single
                                     string.
      VERSION                 (str): Version of the `PROJECT`.
      EXTENSIONS        (list[str]): Extension packages that can be combined
                                     with sphinx. Ex: rinoh.
      TEMPLATES         (list[str]): Path(s) containing templates.
      EXCLUSIONS   (list[str/path]): Path(s) and patterns of files to exclude
                                     from documentation.
      THEME                   (str): The theme to use for HTML and HTML Help
                                     pages.
      STATIC_PATHS (list[str/path]): Path(s) that contain custom static files.
      SOURCE_DIR         (str/path): Directory where the source of the
                                     software package is located.
      BUILD_DIR          (str/path): Directory where the sphinx build will
                                     occur.

    Artifacts:
      The following artifacts will be placed into the `SOURCE_DIR`

      Makefile: see `Makefile.j2`
      make.bat: see `make.bat.j2`
      conf.py:  see `conf.py.j2`


    Returns:
      List of files that were generated
    """

    args = check_args(kwargs)
    templates_path = join(dirname(abspath(__file__)), "templates")
    j2files = {
      join(templates_path, f): f
      for f in listdir(templates_path)
      if isfile(join(templates_path, f)) and f.endswith(".j2")
    }
    source = args["SOURCE_DIR"]

    generated_files = []
    for full_file, j2file in j2files.items():

        log.debug("Reading template {}".format(full_file))
        with open(full_file, "r") as jf:
            template = Template(jf.read())
            log.debug("Rendering template {}".format(full_file))
            output = template.render(**args)

        # write the files to the source directory where project
        # code should reside
        gen_file_name = join(source, j2file.replace(".j2", ""))
        log.debug("Writing data to {}".format(gen_file_name))
        with open(gen_file_name, "w+") as ic:
            ic.write(output)
        generated_files.append(gen_file_name)

    return generated_files
