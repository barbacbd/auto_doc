from jinja2 import Template
from os.path import abspath, dirname, isfile, join
from os import listdir
from logging import getLogger
from .args import check_args
from os.path import exists, join
from os import makedirs
from shutil import rmtree
from pathlib import Path


log = getLogger()


subPackageTemplate = \
'''Subpackages
-----------

.. toctree::
   :maxdepth: 4
  
   {{ SUBPACKAGES }}

'''

autoModuleTemplate = \
'''.. automodule:: {{ PACKAGE }}
   :members:
   :undoc-members:

'''

autoClassTemplate = \
'''.. {{ AUTOTYPE }}:: {{ CLASSNAME }}
   :members:
   :undoc-members:
   :inherited-members:

'''


def generate_sphinx(*args, **kwargs):
    """
    Find all .j2 extension files in this directory. Fill the template files
    with the parameters that were passed in to this function. See
    `args.check_args` for default values. The following artifacts will be placed
    into the `SOURCE_DIR`:
    - Makefile:  see `Makefile.j2`
    - make.bat:  see `make.bat.j2`
    - conf.py:   see `conf.py.j2`
    - index.rst: see `index.rst.j2`
    
    :param PROJECT: Name of the project that the documents are generated for.
    :param COPYRIGHT: Year of the copyright for the `PROJECT`.
    :param AUTHOR: Author(s) of the `PROJECT` as a single string.
    :param VERSION: Version of the `PROJECT`.
    :param EXTENSIONS: Extension packages that can be combined with sphinx.
    :param TEMPLATES: Path(s) containing templates.
    :param EXCLUSIONS: Path(s) and patterns of files to exclude from docs.
    :param THEME: The theme to use for HTML and HTML Help pages.
    :param STATIC_PATHS: Path(s) that contain custom static files.
    :param SOURCE_DIR: Directory for the source of the software package.
    :param BUILD_DIR: Directory where the sphinx build will occur.
    :return: List of files that were generated
    """
    fargs = check_args(**kwargs)
    print(fargs)
    templates_path = join(dirname(abspath(__file__)), "templates/sphinx")
    j2files = {
      join(templates_path, f): f
      for f in listdir(templates_path)
      if isfile(join(templates_path, f)) and f.endswith(".j2")
    }
    source = fargs["SOURCE_DIR"]

    generated_files = []
    for full_file, j2file in j2files.items():

        log.info("Reading template {}".format(full_file))
        with open(full_file, "r") as jf:
            template = Template(jf.read())
            log.debug("Rendering template {}".format(full_file))
            output = template.render(**fargs)

        # write the files to the source directory where project
        # code should reside
        gen_file_name = join(source, j2file.replace(".j2", ""))
        log.info("Writing data to {}".format(gen_file_name))
        with open(gen_file_name, "w+") as ic:
            ic.write(output)
        generated_files.append(gen_file_name)

    return generated_files


def generate_modules_rst(package, directory):
  """Generate the base modules.rst file

  :param package: name of th software package
  :param directory: location where the artifacts will be placed.
  :return: name/path of the generated file
  """
  log.debug("Generating modules.rst")
  template_file = join(dirname(abspath(__file__)), 
                       "templates/rst/modules.rst.j2")
  
  log.info("Reading template {}".format(template_file))
  with open(template_file, "r") as j2file:
    template = Template(j2file.read())
    log.debug("Rendering template {}".format(template_file))
    output = template.render({"PACKAGE": package})
  
  generated_file = join(directory, "modules.rst")
  log.info("Writing data to {}".format(generated_file))
  with open(generated_file, "w+") as gen_file:
    gen_file.write(output)
  
  return generated_file


def generate_rst(tree, directory="."):
    """Generate the rst files for the tree

    :param tree: Node class that is used to generate rst documents.
    :param directory: Output directory for all rst documents.
    :return: Dictionary of artifacts that were created
    """
    def _generate_rst(artifact_dict, t, d, templates, p=None):
        """Generate the rst files for the tree [inner function]

        :param: artifact_dict: Dictionary of artifacts
        :param t: Node class that is used to generate rst documents.
        :param d: Output directory for all rst documents.
        :param templates: dict of Jinja Templates
        :param p: Parent string for the current node. Defaults to None.
        """
        template_data = {"PACKAGE": p+"."+t.name if p is not None else t.name}
        subpackages = ["{}.{}".format(
          template_data["PACKAGE"], child.name) for child in t.children]
        if subpackages:
            template_data["SUBPACKAGE_DATA"] = templates["subs"].render(
              {"SUBPACKAGES": "\n   ".join(subpackages)}
            )

        contents = []
        contents.append(templates["module"].render(template_data))
        for _, shortfile in t.project_files(t.public_filenames).items():
               contents.append(
                 templates["module"].render({"PACKAGE": shortfile}))

        classes = t.classes
        if classes:
            for c in classes:
                auto_class_filler = {
                  "PACKAGE": template_data["PACKAGE"], 
                  "CLASSNAME": c,
                  "AUTOTYPE": "autoclass"
                }
                log.debug("Found class for the module: {}".format(c))
                # exceptions are a special case of classes
                if "error" in c.lower() or "exception" in c.lower():
                    auto_class_filler["AUTOTYPE"] = "autoexception"
                    log.debug("{} is an exception".format(c))

                contents.append(templates["class"].render(auto_class_filler))

        # fill the contents section with the templates created
        template_data["CONTENTS"] = "\n\n".join(contents)
        
        output = templates["rst"].render(template_data)
        rst_filename = join(directory, "{}.rst".format(
          template_data["PACKAGE"]))
        log.info("Generating {}".format(rst_filename))
        with open(rst_filename, "w+") as rst_file:
            rst_file.write(output)
        log.debug("Saving artifact: {}".format(rst_file))
        artifact_dict[str(rst_filename)] = False
        
        for child in t.children:
            _generate_rst(
              artifact_dict,child, d, templates, p=template_data["PACKAGE"])

    # Dictionary that will contain all Templates so they do not need to be 
    # generated each time the inner function is called
    templates = {
      "module": Template(autoModuleTemplate),
      "class": Template(autoClassTemplate),
      "subs": Template(subPackageTemplate)
    }
    template_file = join(dirname(abspath(__file__)), "templates/rst/rst.j2")
    log.info("Reading template {}".format(template_file))
    with open(template_file, "r") as j2file:
      templates["rst"] = Template(j2file.read())
      
    log.info("Generating rst files in {}".format(directory))
    if not exists(directory):
        log.info("Creating directory {}".format(directory))
        makedirs(directory)

    artifacts = {
      directory: False,
      generate_modules_rst(tree.name, directory=directory): False
    }
    _generate_rst(artifacts, tree, directory, templates)
    return artifacts


def generate_docs_dir(source_dir, build_dir):
  """Generate the information required to build Docs

  :param source_dir: Directory of the source
  :param build_dir: Build/Docs directory relative to source_dir
  :return: artifacts that were created
  """
  docs_dir = join(source_dir, build_dir)
  if exists(docs_dir):
    rmtree(docs_dir)
  makedirs(docs_dir)
  
  # create a routing path to the next level index.html
  index_filename = join(docs_dir, "index.html")
  with open(index_filename, "w+") as index_file:
    index_file.write(
      "<meta http-equiv=\"refresh\" content=\"0; url=./html/index.html\" />")

  # create the necessary .nojekyll file
  jekyll_filename = join(docs_dir, ".nojekyll")
  Path(jekyll_filename).touch()
  
  return {index_filename: True, jekyll_filename: True}